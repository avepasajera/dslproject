import re

def extract_lines(srt_file):
    with open(srt_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    extracted_lines = []
    temp_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if re.match(r'\d\d:\d\d:\d\d,\d\d\d --> \d\d:\d\d:\d\d,\d\d\d', line):
            temp_lines = []
            while lines:
                line = lines.pop(0)
                if line.strip():
                    temp_lines.append(line)
                else:
                    extracted_lines.append(" ".join(temp_lines[1:]))
                    break

    return extracted_lines


