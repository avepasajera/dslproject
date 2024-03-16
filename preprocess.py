import re
import os
import sys
import chardet
import codecs


def detect_and_convert(filename):
    """if the file has a different encoding,
    this program helps to detect the encoding in order to later convert it to the correct one"""

    rawdata = open(filename, 'rb').read()
    result = chardet.detect(rawdata)
    encoding = result['encoding']
    print(f"Detected encoding: {encoding}")
    data = rawdata.decode(encoding, 'ignore')
    with codecs.open(filename, 'w', 'utf-8') as f:
        f.write(data)


def remove_xml_tags(text):
    """preprocess and normalise the .srt format to remove the xml tags"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def process_srt_file(file_path):
    """preprocess the srt file and remove xml tags to normalise the format"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    with open(file_path, 'w', encoding='utf-8') as file:
        for line in content:
            if not line.strip():  # Skip blank lines
                file.write(line)
            elif '--> ' in line:  # Skip timestamp lines
                file.write(line)
            else:  # Process subtitle lines
                file.write(remove_xml_tags(line))


def parse_srt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    subtitles = []
    pattern = re.compile(r'(\d+)\n(\d\d:\d\d:\d\d,\d\d\d --> \d\d:\d\d:\d\d,\d\d\d)\n(.*?)(?:\n\n|$)', re.DOTALL)
    for match in pattern.finditer(content):
        index, timestamp, text = match.groups()
        subtitles.append((timestamp, text.strip()))

    return subtitles


def align_subtitles(en_dir, ru_dir, sindhi_dir, max_diff_ms=100):
    # Assuming each directory contains only one SRT file per film
    en_files = [f for f in os.listdir(en_dir) if f.endswith('.srt')]
    ru_files = [f for f in os.listdir(ru_dir) if f.endswith('.srt')]
    sindhi_files = [f for f in os.listdir(sindhi_dir) if f.endswith('.srt')]

    aligned_subtitles = {}

    for en_file, ru_file, sindhi_file in zip(en_files, ru_files, sindhi_files):
        en_path = os.path.join(en_dir, en_file)
        ru_path = os.path.join(ru_dir, ru_file)
        sindhi_path = os.path.join(sindhi_dir, sindhi_file)

        en_subtitles = parse_srt_file(en_path)
        ru_subtitles = parse_srt_file(ru_path)
        sindhi_subtitles = parse_srt_file(sindhi_path)

        # Align subtitles based on timestamps
        en_timestamps, ru_timestamps, sindhi_timestamps = [], [], []
        en_texts, ru_texts, sindhi_texts = [], [], []

        for timestamp, text in en_subtitles:
            en_timestamps.append(timestamp)
            en_texts.append(text)

        for timestamp, text in ru_subtitles:
            ru_timestamps.append(timestamp)
            ru_texts.append(text)

        for timestamp, text in sindhi_subtitles:
            sindhi_timestamps.append(timestamp)
            sindhi_texts.append(text)

        aligned_sub = []

        for en_ts, en_txt in zip(en_timestamps, en_texts):
            ru_idx = find_closest_index(ru_timestamps, en_ts, max_diff_ms)
            sindhi_idx = find_closest_index(sindhi_timestamps, en_ts, max_diff_ms)

            ru_txt = ru_texts[ru_idx] if ru_idx != -1 else ''
            sindhi_txt = sindhi_texts[sindhi_idx] if sindhi_idx != -1 else ''

            aligned_sub.append((en_txt, ru_txt, sindhi_txt))

        # Store the aligned subtitles in the dictionary using the film name as the key
        film_name = os.path.splitext(en_file)[0]
        aligned_subtitles[film_name] = aligned_sub

    return aligned_subtitles

def find_closest_index(timestamps, target_ts, max_diff_ms):
    closest_idx = -1
    closest_diff = float('inf')

    for idx, ts in enumerate(timestamps):
        diff_ms = abs(timestamp_to_ms(ts) - timestamp_to_ms(target_ts))
        if diff_ms < closest_diff and diff_ms <= max_diff_ms:
            closest_idx = idx
            closest_diff = diff_ms

    return closest_idx

def timestamp_to_ms(timestamp):
    h, m, s = timestamp.split('-->')[0].strip().split(':')
    h, m, s = int(h), int(m), float(s.replace(',', '.'))
    ms = int(s * 1000)
    return (h * 3600 + m * 60) * 1000 + ms




if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     print("Usage: python convert_encoding.py <filename>")
    #     sys.exit(1)
    #
    # filename = sys.argv[1]
    # detect_and_convert(filename)
    # srt_file = 'srt/english/Braveheart.srt'
    # directories = ['srt/english', 'srt/russian', 'srt/sindhi'] # commented as completed
    # for directory in directories:
    #     for filename in os.listdir(directory):
    #         if filename.endswith('.srt'):
    #             file_path = os.path.join(directory, filename)
    #             process_srt_file(file_path)
    #             print(f'Processed {file_path}')
    aligned_subtitles = align_subtitles(en_dir='srt/english',
                                        ru_dir='srt/russian',
                                        sindhi_dir='srt/sindhi')
    # Print the number of films with aligned subtitles
    print(f"Number of films with aligned subtitles: {len(aligned_subtitles)}")

    # Print the aligned subtitles for the first film
    film_name = list(aligned_subtitles.keys())[0]
    print(f"Aligned subtitles for the first film ({film_name}):")
    for en_txt, ru_txt, sindhi_txt in aligned_subtitles[film_name]:
        print(f"English: {en_txt}\nRussian: {ru_txt}\nSindhi: {sindhi_txt}\n")

