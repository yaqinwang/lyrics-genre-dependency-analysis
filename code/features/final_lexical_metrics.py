"""Authoritative final lexical metrics: approved CMU method with retained-token floor.

lexical_metrics remains the unmodified pre-floor implementation for provenance.
Only calculate_average_syllables is overridden. The lexical retention filter,
lookup normalization, CMU selection, fallback, and denominator are unchanged.
"""
from lexical_metrics import *
import lexical_metrics as previous

def final_syllable_count(retained_token):
    """Use only after the historical lexical-retention filter."""
    return max(previous.count_syllables(retained_token), 1)

def calculate_average_syllables(tokens):
    return sum(final_syllable_count(token) for token in tokens) / len(tokens) if tokens else 0.0

# Avoid inherited collection functions resolving the old module's averaging function.
def extract_lexical_complexity(folder_path, genre_mapping, frequency_list_path, mattr_window=50):
    entries = previous.collect_song_token_data(folder_path, genre_mapping)
    common = previous.load_frequency_list(frequency_list_path)
    records = []
    for entry in entries:
        tokens, lemmas, tags = entry['tokens'], entry['lemmas'], entry['pos_tags']
        records.append(dict(file_id=entry['file_id'], genre=entry['genre'],
            MATTR=previous.calculate_mattr(tokens, mattr_window),
            lexical_density=previous.calculate_lexical_density(tags),
            avg_syllables=calculate_average_syllables(tokens),
            lexical_sophistication=previous.calculate_lexical_sophistication(lemmas,tags,common),
            token_count=len(tokens)))
    return previous.pd.DataFrame(records)
