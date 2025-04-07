from difflib import SequenceMatcher

def transfer_linebreaks(from_text, to_text):
    # Split the version with breaks into lines
    broken_lines = from_text.strip().splitlines()

    output = []
    current_index = 0

    for line in broken_lines:
        line = line.strip()
        if not line:
            continue

        # Try to find the best match for this line in the unbroken text
        matcher = SequenceMatcher(None, to_text[current_index:], line)
        match = matcher.find_longest_match(0, len(to_text) - current_index, 0, len(line))

        # Slice from last index to matched end and insert a newline
        matched_text = to_text[current_index:current_index + match.b + match.size]
        output.append(matched_text.strip())
        current_index += match.b + match.size

    return '\n'.join(output)

# Load files
with open('test_data/cz_generated_without_timestamps.txt', encoding='utf-8') as f:
    broken_text = f.read()

with open('test_data/cz_test_without_paragraphs.txt', encoding='utf-8') as f:
    full_text = f.read()

# Run the transfer
aligned_text = transfer_linebreaks(broken_text, full_text)

# Save output
with open('test_data/restructured_with_linebreaks.txt', 'w', encoding='utf-8') as f:
    f.write(aligned_text)

print("✅ Line breaks transferred and saved as 'restructured_with_linebreaks.txt'")

