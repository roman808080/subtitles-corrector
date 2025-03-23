#!/usr/bin/env python3

import re
from typing import List, Tuple

def parse_srt(srt_file: str) -> List[Tuple[str, str]]:
    """Parse SRT file and extract subtitle entries with timestamps."""
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract subtitle entries (index, timestamp, text)
    pattern = r'(\d+)\s+(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\s+([\s\S]*?)(?=\n\n\d+\s+|$)'
    matches = re.findall(pattern, content)
    
    # Return list of (timestamp, text) tuples
    return [(timestamp, text.strip()) for _, timestamp, text in matches]

def parse_txt(txt_file: str) -> str:
    """Parse TXT file containing the correct text."""
    with open(txt_file, 'r', encoding='utf-8') as f:
        return f.read().strip()

def split_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs."""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    return paragraphs

def create_corrected_srt(timestamps: List[Tuple[str, str]], paragraphs: List[str]) -> str:
    """Create corrected SRT file by combining timestamps with correct paragraphs."""
    if len(timestamps) == 0 or len(paragraphs) == 0:
        return ""
    
    # Determine distribution of paragraphs across subtitles
    subs_count = len(timestamps)
    para_count = len(paragraphs)
    
    # Handle case where there are more paragraphs than subtitles
    if para_count > subs_count:
        # Merge excess paragraphs with the last ones
        paragraphs = paragraphs[:subs_count-1] + [' '.join(paragraphs[subs_count-1:])]
    
    # Handle case where there are more subtitles than paragraphs
    paragraph_text = ' '.join(paragraphs)
    
    # Split the text approximately evenly across the subtitles
    total_chars = len(paragraph_text)
    chars_per_sub = total_chars / subs_count
    
    corrected_srt = []
    sub_index = 1
    
    # Create a rough character-based split of the text
    start_idx = 0
    for i, (timestamp, _) in enumerate(timestamps):
        is_last = i == len(timestamps) - 1
        
        if is_last:
            # Last subtitle gets the rest of the text
            text_segment = paragraph_text[start_idx:]
        else:
            # Calculate approximate end point for this subtitle
            end_idx = min(int(start_idx + chars_per_sub), total_chars)
            
            # Find a good breaking point (prefer at end of sentence or space)
            if end_idx < total_chars:
                # Try to find sentence end (.!?) within reasonable distance
                sentence_end = -1
                for punct in ['.', '!', '?']:
                    pos = paragraph_text.find(punct, end_idx - 20, end_idx + 20)
                    if pos > 0 and (sentence_end == -1 or pos < sentence_end):
                        sentence_end = pos + 1  # Include the punctuation
                
                if sentence_end > 0:
                    end_idx = sentence_end
                else:
                    # Fall back to word boundary
                    space_pos = paragraph_text.find(' ', end_idx)
                    if space_pos > 0 and space_pos - end_idx < 20:
                        end_idx = space_pos
            
            text_segment = paragraph_text[start_idx:end_idx].strip()
            start_idx = end_idx
        
        # Add to corrected subtitles
        corrected_srt.append(f"{sub_index}\n{timestamp}\n{text_segment}\n")
        sub_index += 1
    
    return "\n".join(corrected_srt)

def main(srt_file: str, txt_file: str, output_file: str) -> None:
    """Main function to correct subtitles using proper text."""
    # Parse input files
    timestamps = parse_srt(srt_file)
    correct_text = parse_txt(txt_file)
    paragraphs = split_paragraphs(correct_text)
    
    # Create corrected SRT
    corrected_srt = create_corrected_srt(timestamps, paragraphs)
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(corrected_srt)
    
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