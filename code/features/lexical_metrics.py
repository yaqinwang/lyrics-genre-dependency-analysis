"""Historical metric functions relocated without formula changes; source: new_lexical_com.py."""
import os

import re

from collections import Counter

from functools import lru_cache

from typing import Dict, List, Set, Tuple

import numpy as np

import pandas as pd

try:
    import pronouncing  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    pronouncing = None

def parse_conll_tokens(filepath: str) -> Tuple[List[str], List[str], List[str]]:
    """
    Extract lowercase word tokens, lemmas, and POS tags from a CoNLL-formatted lyric file.
    Punctuation-only tokens are discarded.
    """
    tokens: List[str] = []
    pos_tags: List[str] = []
    lemmas: List[str] = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) < 4:
                continue

            token = parts[1]
            lemma = parts[2] if len(parts) > 2 else parts[1]
            pos_tag = parts[3]

            if not any(ch.isalpha() for ch in token):
                continue

            tokens.append(token.lower())
            lemmas.append(lemma.lower())
            pos_tags.append(pos_tag)

    return tokens, lemmas, pos_tags

def calculate_mattr(tokens: List[str], window_size: int = 50) -> float:
    """Moving Average Type-Token Ratio across a sliding window."""
    token_count = len(tokens)
    if token_count == 0:
        return 0.0

    if token_count <= window_size:
        return len(set(tokens)) / token_count

    window_counter = Counter(tokens[:window_size])
    unique_in_window = len(window_counter)
    mattr_values = [unique_in_window / window_size]

    for idx in range(window_size, token_count):
        entering = tokens[idx]
        leaving = tokens[idx - window_size]

        window_counter[entering] += 1
        if window_counter[entering] == 1:
            unique_in_window += 1

        window_counter[leaving] -= 1
        if window_counter[leaving] == 0:
            unique_in_window -= 1
            del window_counter[leaving]

        mattr_values.append(unique_in_window / window_size)

    return float(np.mean(mattr_values))

def calculate_lexical_density(pos_tags: List[str]) -> float:
    """Proportion of tokens that are lexical/content words based on POS tags."""
    if not pos_tags:
        return 0.0

    content_prefixes = ("NN", "VB", "JJ", "RB")
    content_tokens = sum(
        1 for tag in pos_tags if tag and tag.startswith(content_prefixes)
    )
    return content_tokens / len(pos_tags)

def _heuristic_syllable_count(normalized_word: str) -> int:
    """
    Fallback heuristic syllable counter for when CMU dictionary lookup fails.
    
    Uses vowel-group counting with special rules for silent -e.
    Guarantees at least one syllable for non-empty alphabetic words.
    """
    if not normalized_word:
        return 0

    vowels = "aeiouy"
    syllables = 0
    prev_is_vowel = False

    for char in normalized_word:
        is_vowel = char in vowels
        if is_vowel and not prev_is_vowel:
            syllables += 1
        prev_is_vowel = is_vowel

    # Silent -e rule: subtract one if word ends in 'e', has >1 syllable,
    # and doesn't end in 'le' or 'ue'
    if (
        normalized_word.endswith("e")
        and syllables > 1
        and not normalized_word.endswith(("le", "ue"))
    ):
        syllables -= 1

    return syllables or 1

@lru_cache(maxsize=10000)
def count_syllables(word: str) -> int:
    """
    Count syllables in a word using the CMU Pronouncing Dictionary.
    
    The CMU Pronouncing Dictionary provides phonetic transcriptions for over 
    134,000 English words, with syllable information encoded in the stress markers
    (0, 1, 2) on vowel phonemes.
    
    Falls back to a rule-based heuristic if:
    - The pronouncing library is not installed
    - The word is not in the CMU dictionary
    
    Args:
        word: Input word (case-insensitive)
        
    Returns:
        Number of syllables (minimum 1 for non-empty alphabetic words)
    """
    # Normalize: remove non-alphabetic characters and convert to lowercase
    normalized = re.sub(r"[^a-z]", "", word.lower())
    if not normalized:
        return 0

    # Try CMU Pronouncing Dictionary first
    if pronouncing is not None:
        phones_list = pronouncing.phones_for_word(normalized)
        if phones_list:
            # Use the first pronunciation if multiple exist
            # Count stressed vowels (marked with 0, 1, or 2)
            return pronouncing.syllable_count(phones_list[0])
    
    # Fallback to heuristic if CMU lookup fails
    return _heuristic_syllable_count(normalized)

def calculate_average_syllables(tokens: List[str]) -> float:
    """
    Calculate average word length in syllables across all tokens.
    
    Uses CMU Pronouncing Dictionary for accurate syllable counts,
    with heuristic fallback for out-of-vocabulary words.
    
    Args:
        tokens: List of word tokens
        
    Returns:
        Average number of syllables per token
    """
    if not tokens:
        return 0.0

    syllable_total = sum(count_syllables(token) for token in tokens)
    return syllable_total / len(tokens)

def calculate_lexical_sophistication(
    lemmas: List[str],
    pos_tags: List[str],
    common_lemmas: Set[str],
) -> float:
    """
    Percentage of content-word lemmas that fall outside the supplied high-frequency list.
    
    Args:
        lemmas: List of lemmatized words
        pos_tags: Corresponding POS tags
        common_lemmas: Set of high-frequency lemmas (e.g., COCA top 5000)
        
    Returns:
        Percentage of sophisticated (low-frequency) content words
    """
    content_prefixes = ("NN", "VB", "JJ", "RB")
    content_lemmas = [
        lemma
        for lemma, tag in zip(lemmas, pos_tags)
        if lemma and tag and tag.startswith(content_prefixes)
    ]

    if not content_lemmas:
        return 0.0

    sophisticated = sum(1 for lemma in content_lemmas if lemma not in common_lemmas)
    return sophisticated / len(content_lemmas) * 100.0

def collect_song_token_data(
    folder_path: str,
    genre_mapping: Dict[str, str],
) -> List[Dict[str, object]]:
    """
    Parse every relevant song file, capturing tokens, POS tags, and genre metadata.
    
    Args:
        folder_path: Directory containing CoNLL-formatted lyric files
        genre_mapping: Dictionary mapping genre names to filename prefixes
        
    Returns:
        List of dictionaries containing song-level token data
    """
    song_entries: List[Dict[str, object]] = []

    for genre_name, prefix in genre_mapping.items():
        for filename in os.listdir(folder_path):
            if not (filename.startswith(prefix) and filename.endswith(".conll")):
                continue

            filepath = os.path.join(folder_path, filename)
            tokens, lemmas, pos_tags = parse_conll_tokens(filepath)

            if not tokens:
                continue

            file_id = filename.replace(".txt.conll", "").replace(".conll", "")
            song_entries.append(
                {
                    "file_id": file_id,
                    "genre": genre_name,
                    "tokens": tokens,
                    "lemmas": lemmas,
                    "pos_tags": pos_tags,
                }
            )

    return song_entries

def extract_lexical_complexity(
    folder_path: str,
    genre_mapping: Dict[str, str],
    frequency_list_path: str,
    mattr_window: int = 50,
) -> pd.DataFrame:
    """
    Compute lexical complexity metrics for every song in the given folder.
    
    Metrics computed:
    - MATTR: Moving Average Type-Token Ratio (lexical diversity)
    - lexical_density: Proportion of content words
    - avg_syllables: Average word length in syllables (CMU dictionary-based)
    - lexical_sophistication: Percentage of low-frequency content words
    
    Args:
        folder_path: Directory containing CoNLL-formatted lyric files
        genre_mapping: Dictionary mapping genre names to filename prefixes
        frequency_list_path: Path to COCA frequency list CSV
        mattr_window: Window size for MATTR calculation (default: 50)
        
    Returns:
        DataFrame with one row per song and all lexical complexity measures
    """
    song_entries = collect_song_token_data(folder_path, genre_mapping)
    common_lemmas = load_frequency_list(frequency_list_path)

    records = []
    for entry in song_entries:
        tokens = entry["tokens"]
        lemmas = entry["lemmas"]
        pos_tags = entry["pos_tags"]

        mattr = calculate_mattr(tokens, window_size=mattr_window)
        lexical_density = calculate_lexical_density(pos_tags)
        avg_syllables = calculate_average_syllables(tokens)
        lexical_sophistication = calculate_lexical_sophistication(
            lemmas, pos_tags, common_lemmas
        )

        records.append(
            {
                "file_id": entry["file_id"],
                "genre": entry["genre"],
                "MATTR": mattr,
                "lexical_density": lexical_density,
                "avg_syllables": avg_syllables,
                "lexical_sophistication": lexical_sophistication,
                "token_count": len(tokens),
            }
        )

    return pd.DataFrame(records)

def load_frequency_list(frequency_list_path: str, top_n: int = 5000) -> Set[str]:
    """
    Load the top-N lemma list (e.g., COCA 5k) into a set for quick membership checks.
    
    Entries are normalized to lowercase for case-insensitive matching.
    
    Args:
        frequency_list_path: Path to CSV file with 'lemma' column
        top_n: Number of top-frequency lemmas to load (default: 5000)
        
    Returns:
        Set of high-frequency lemmas
        
    Raises:
        FileNotFoundError: If frequency list file doesn't exist
        ValueError: If CSV is empty or missing 'lemma' column
    """
    if not os.path.exists(frequency_list_path):
        raise FileNotFoundError(
            f"Frequency list not found at '{frequency_list_path}'. "
            "Provide a COCA top-5000 lemma list to compute lexical sophistication."
        )

    import csv

    lemmas: Set[str] = set()
    with open(frequency_list_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows_read = 0
        for row in reader:
            lemma = row.get("lemma")
            if lemma:
                lemmas.add(lemma.strip().lower())
            rows_read += 1
            if top_n and rows_read >= top_n:
                break

    if not lemmas:
        raise ValueError(
            "Frequency list appears empty or missing 'lemma' column. "
            "Ensure the CSV matches the COCA WordFrequency format."
        )

    return lemmas
