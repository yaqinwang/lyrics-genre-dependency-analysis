"""Historical metric functions relocated without formula changes; source: synnew2_py."""
import os

import pandas as pd

import numpy as np

from collections import Counter

def calculate_hierarchical_distance(filepath):
    """Calculate MHD for a single song using formula (4) from the paper."""
    sentences = []
    current_sentence = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                if current_sentence:
                    sentences.append(current_sentence)
                    current_sentence = {}
                continue
            
            parts = line.split('\t')
            if len(parts) >= 7:
                token_id = int(parts[0])
                head_id = int(parts[5])
                current_sentence[token_id] = head_id
    
    if current_sentence:
        sentences.append(current_sentence)
    
    # Calculate MHD for EACH sentence separately
    sentence_mhds = []
    for sentence in sentences:
        sentence_depths = []
        for token_id in sentence:
            depth = 0
            current = token_id
            visited = set()
            
            # Count edges/steps to reach root
            while current != 0 and current in sentence:
                if current in visited:
                    break
                visited.add(current)
                current = sentence[current]
                depth += 1
            
            if current == 0:
                hd = depth - 1  # Root has HD = 0
                # Exclude root (HD=0) from calculation
                if hd > 0:
                    sentence_depths.append(hd)
        
        # Calculate MHD for this sentence (formula 2)
        if sentence_depths:
            sentence_mhd = np.mean(sentence_depths)
            sentence_mhds.append(sentence_mhd)
    
    # Calculate MHD₂ for the song (formula 4): average of sentence MHDs
    return np.mean(sentence_mhds) if sentence_mhds else 0

def calculate_line_features(filepath):
    """
    Calculate line length and line repetition rate for a song.
    
    The line repetition rate measures what proportion of lines in the song
    are repetitions of earlier lines. This is a key stylistic feature in lyrics,
    where choruses, hooks, and repeated phrases are common.
    
    Returns:
        - avg_line_length: Average number of tokens per line
        - line_repetition_rate: Percentage of lines that are repetitions
                                (excludes first occurrence, counts only repeats)
    """
    lines = []
    current_line_tokens = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                # End of sentence/line
                if current_line_tokens:
                    lines.append(tuple(current_line_tokens))
                    current_line_tokens = []
                continue
            
            parts = line.split('\t')
            if len(parts) >= 7:
                token = parts[1]  # The actual word/token
                current_line_tokens.append(token.lower())
        
        # Don't forget the last line
        if current_line_tokens:
            lines.append(tuple(current_line_tokens))
    
    if not lines:
        return 0, 0
    
    # Calculate average line length
    line_lengths = [len(line) for line in lines]
    avg_line_length = np.mean(line_lengths) if line_lengths else 0
    
    # Calculate line repetition rate
    # Count how many lines are repetitions (excluding first occurrences)
    line_counts = Counter(lines)
    
    # For each unique line that appears >1 times, count the extra occurrences
    # Example: line appearing 3 times contributes 2 repetitions (3 - 1)
    repeated_line_instances = sum(count - 1 for count in line_counts.values() if count > 1)
    total_lines = len(lines)
    
    # Percentage of lines that are repetitions
    line_repetition_rate = (repeated_line_instances / total_lines * 100) if total_lines > 0 else 0
    
    return avg_line_length, line_repetition_rate

def calculate_song_syntactic_features(filepath):
    """
    Extract core syntactic complexity features for a single song.
    
    Returns dictionary with:
        - MDD: Mean Dependency Distance (formula 3)
        - MHD: Mean Hierarchical Distance (formula 4)
        - avg_line_length: Average tokens per line
        - line_repetition_rate: Percentage of lines that are repetitions
    """
    # Parse sentences first
    sentences = []
    current_sentence = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                if current_sentence:
                    sentences.append(current_sentence)
                    current_sentence = {}
                continue
            
            parts = line.split('\t')
            if len(parts) >= 7:
                token_id = int(parts[0])
                head_id = int(parts[5])
                current_sentence[token_id] = head_id
    
    if current_sentence:
        sentences.append(current_sentence)
    
    # Calculate MDD for EACH sentence separately (formula 1)
    sentence_mdds = []
    for sentence in sentences:
        sentence_distances = []
        for token_id, head_id in sentence.items():
            if head_id != 0:  # Exclude ROOT
                distance = abs(token_id - head_id)
                sentence_distances.append(distance)
        
        # Calculate MDD for this sentence
        if sentence_distances:
            sentence_mdd = np.mean(sentence_distances)
            sentence_mdds.append(sentence_mdd)
    
    # Calculate MDD₂ for the song (formula 3): average of sentence MDDs
    mdd = np.mean(sentence_mdds) if sentence_mdds else 0
    
    # Calculate MHD₂ for the song (formula 4)
    mhd = calculate_hierarchical_distance(filepath)
    
    # Calculate line features
    avg_line_length, line_repetition_rate = calculate_line_features(filepath)
    
    return {
        'MDD': mdd,
        'MHD': mhd,
        'avg_line_length': avg_line_length,
        'line_repetition_rate': line_repetition_rate
    }

def extract_all_songs_syntactic(folder_path, genre_mapping):
    """
    Extract syntactic features for all songs.
    """
    song_data = []
    
    print("\n" + "="*80)
    print("EXTRACTING SYNTACTIC FEATURES FOR ALL SONGS")
    print("="*80)
    
    for genre_name, prefix in genre_mapping.items():
        print(f"\nProcessing {genre_name}...")
        count = 0
        
        for filename in os.listdir(folder_path):
            if filename.startswith(prefix) and filename.endswith('.conll'):
                filepath = os.path.join(folder_path, filename)
                
                try:
                    # Extract syntactic features
                    syn_features = calculate_song_syntactic_features(filepath)
                    
                    # Clean file ID
                    file_id = filename.replace('.txt.conll', '').replace('.conll', '')
                    
                    song_data.append({
                        'file_id': file_id,
                        'genre': genre_name,
                        'MDD': syn_features['MDD'],
                        'MHD': syn_features['MHD'],
                        'avg_line_length': syn_features['avg_line_length'],
                        'line_repetition_rate': syn_features['line_repetition_rate']
                    })
                    
                    count += 1
                    
                except Exception as e:
                    print(f"  Error with {filename}: {e}")
        
        print(f"  ✓ Processed {count} songs")
    
    df_syntactic = pd.DataFrame(song_data)
    
    print(f"\n" + "="*80)
    print(f"TOTAL SONGS PROCESSED: {len(df_syntactic)}")
    print("="*80)
    
    # Show summary statistics
    print("\nSyntactic measures by genre (means):")
    print(df_syntactic.groupby('genre')[['MDD', 'MHD', 'avg_line_length', 'line_repetition_rate']].mean())
    
    return df_syntactic
