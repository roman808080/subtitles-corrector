def remove_paragraphs(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace all newline characters with spaces, then collapse multiple spaces
    flattened = ' '.join(content.split())

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(flattened)

# Example usage:
remove_paragraphs('test_data/cz_test.txt', 'test_data/cz_test_without_paragraphs.txt')

