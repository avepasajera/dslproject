# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import sys
import chardet
import codecs
import extract

def detect_and_convert(filename):
    rawdata = open(filename, 'rb').read()
    result = chardet.detect(rawdata)
    encoding = result['encoding']

    print(f"Detected encoding: {encoding}")

    data = rawdata.decode(encoding, 'ignore')
    with codecs.open(filename, 'w', 'utf-8') as f:
        f.write(data)

if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     print("Usage: python convert_encoding.py <filename>")
    #     sys.exit(1)
    #
    # filename = sys.argv[1]
    # detect_and_convert(filename)
    srt_file = 'srt/english/Braveheart.srt'


    result = extract.extract_lines(srt_file)
    for line in result:
        print()

# Press the green button in the gutter to run the script.


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
