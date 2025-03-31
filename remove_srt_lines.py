import re

def srt_to_txt(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into blocks by double newline
    blocks = content.strip().split('\n\n')

    # Extract only the subtitle text lines
    subtitles = []
    for block in blocks:
        lines = block.strip().split('\n')

        # Remove lines that are numbers or timestamps
        text_lines = [line for line in lines if not re.match(r'^\d+$', line) and not re.match(r'\d{2}:\d{2}:\d{2},\d{3}', line)]
        if text_lines:
            subtitles.append(' '.join(text_lines))  # Combine multi-line subs into one line

    # Write to txt file
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in subtitles:
            f.write(line + '\n')

# Example usage:
srt_to_txt('test_data/cz_generated.srt', 'cz_generated_without_timestamps.txt')

