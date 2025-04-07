import difflib

with open('test_data/cz_test_without_paragraphs.txt') as f1, open('test_data/cz_generated_without_timestamps.txt') as f2:
    lines1 = f1.readlines()
    lines2 = f2.readlines()

diff = difflib.unified_diff(lines1, lines2, fromfile='file1.txt', tofile='file2.txt')

print("".join(diff))

