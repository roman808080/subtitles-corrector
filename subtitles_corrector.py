#!/usr/bin/env python3

import re
import difflib
from typing import List, Tuple, Dict

def parse_srt(srt_file: str) -> List[Dict]:
    """Parse SRT file and extract subtitle entries."""
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract subtitle entries (index, timestamp, text)
    pattern = r'(\d+)\s+(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\s+([\s\S]*?)(?=\n\n\d+\s+|$)'
    matches = re.findall(pattern, content)
    
    # Return list of subtitle entries
    return [
        {
            'index': int(index),
            'timestamp': timestamp,
            'text': text.strip()
        } 
        for index, timestamp, text in matches
    ]

def parse_txt(txt_file: str) -> str:
    """Parse TXT file containing the correct text."""
    with open(txt_file, 'r', encoding='utf-8') as f:
        return f.read().strip()

def align_text_to_subtitles(subtitles: List[Dict], correct_text: str) -> List[Dict]:
    """
    Align the correct text to the original subtitles using difflib
    and create corrected subtitles.
    """
    # Concatenate all original subtitle text
    original_text = ' '.join(sub['text'] for sub in subtitles)
    
    # Use difflib to align the texts
    matcher = difflib.SequenceMatcher(None, original_text, correct_text)
    
    # Create a mapping from original text positions to corrected text positions
    position_map = {}
    for block in matcher.get_matching_blocks():
        for i in range(block.size):
            position_map[block.a + i] = block.b + i
    
    # Create corrected subtitles
    corrected_subtitles = []
    
    # Current position in the original text
    original_pos = 0
    
    for sub in subtitles:
        sub_text = sub['text']
        sub_start = original_pos
        sub_end = sub_start + len(sub_text)
        
        # Find corresponding start and end positions in corrected text
        correct_start = position_map.get(sub_start, None)
        
        # Find the closest mapped position for the end
        correct_end = None
        for i in range(sub_end, sub_start - 1, -1):
            if i in position_map:
                correct_end = position_map[i] + 1  # +1 to include the character at that position
                break
        
        # If we couldn't find a direct mapping, use an approximation
        if correct_start is None or correct_end is None:
            # Estimate based on relative position in the document
            if sub_start >= len(original_text):
                ratio = 1.0
            else:
                ratio = sub_start / len(original_text)
            correct_start = int(ratio * len(correct_text))
            
            if sub_end >= len(original_text):
                ratio = 1.0
            else:
                ratio = sub_end / len(original_text)
            correct_end = int(ratio * len(correct_text))
        
        # Find word boundaries to improve readability
        if correct_start > 0 and correct_text[correct_start - 1] != ' ':
            # Find the previous space
            prev_space = correct_text.rfind(' ', 0, correct_start)
            if prev_space != -1:
                correct_start = prev_space + 1
        
        if correct_end < len(correct_text) and correct_text[correct_end - 1] != ' ':
            # Find the next space
            next_space = correct_text.find(' ', correct_end)
            if next_space != -1:
                correct_end = next_space
        
        # Extract the corrected text for this subtitle
        corrected_text = correct_text[correct_start:correct_end].strip()
        
        # Ensure we have some text
        if not corrected_text and sub_text:
            # Fall back to a proportion-based approach for this subtitle
            total_len = sum(len(s['text']) for s in subtitles)
            proportion = len(sub_text) / total_len if total_len > 0 else 0
            start_char = int(len(correct_text) * (sum(len(s['text']) for s in subtitles[:sub['index']-1]) / total_len))
            char_count = int(len(correct_text) * proportion)
            corrected_text = correct_text[start_char:start_char + char_count].strip()
        
        # Create the corrected subtitle
        corrected_subtitles.append({
            'index': sub['index'],
            'timestamp': sub['timestamp'],
            'text': corrected_text
        })
        
        # Update the position for the next subtitle
        original_pos = sub_end + 1  # +1 for the space we added between subtitles
    
    return corrected_subtitles

def format_srt(subtitles: List[Dict]) -> str:
    """Format subtitles into SRT format."""
    srt_content = []
    
    for sub in subtitles:
        # Ensure we have text for this subtitle
        if not sub['text']:
            continue
            
        srt_content.append(f"{sub['index']}\n{sub['timestamp']}\n{sub['text']}\n")
    
    return "\n".join(srt_content)

def main(srt_file: str, txt_file: str, output_file: str) -> None:
    """Main function to correct subtitles using proper text."""
    # Parse input files
    subtitles = parse_srt(srt_file)
    correct_text = parse_txt(txt_file)
    
    # Align text to subtitles
    corrected_subtitles = align_text_to_subtitles(subtitles, correct_text)
    
    # Format and write output
    srt_content = format_srt(corrected_subtitles)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(srt_content)
    
    print(f"Corrected subtitles saved to {output_file}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python subtitles_corrector.py <srt_file> <txt_file> [output_file]")
        sys.exit(1)
    
    srt_file = sys.argv[1]
    txt_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else "corrected.srt"
    
    main(srt_file, txt_file, output_file)