import pdfplumber
import re

def extract_bold_italic_text_phrases(pdf_file, start_page=8, end_page=512):
    extracted_text = {}

    # List of possible sentiment categories
    sent_list = [
        "высок.", "груб.", "ирон.", "книжн.", "неодобр.", "одобр.",
        "отвлеч.", "перен.", "презр.", "пренебр.", "прост.", "проф.",
        "разг.", "устар.", "фольк.", "шутл.", "экспрес."
    ]
    # Regular expression to detect if a word is a number
    number_pattern = re.compile(r'\d+')

    # Open the PDF using pdfplumber
    with pdfplumber.open(pdf_file) as pdf:
        total_pages = min(end_page, len(pdf.pages))  # Limit to the last page (512 or total)

        for page_number in range(start_page - 1, total_pages):  # Iterate from page 8 to end_page
            page = pdf.pages[page_number]
            # Extract all the words and their font properties
            words = page.extract_words(extra_attrs=['fontname'])

            bold_text = []
            italic_text = []
            plain_text = []
            current_phase = "bold"

            for word_info in words:
                text = word_info['text']
                fontname = word_info.get('fontname', '').lower()

                # Skip if the text is a number
                if number_pattern.match(text):
                    continue

                # Skip if the font name matches the redundant header font
                if fontname == 'jsxeyb+arialmt' or fontname == 'nizhct+avantgardegothicc':
                    continue

                # Determine if the word is bold, italic, or normal
                if 'bold' in fontname:
                    # If we encounter bold again, save the previous phrase
                    if bold_text and (italic_text or plain_text):
                        # Determine sentiment
                        sentiment = ' '.join(italic_text).strip().lower() if italic_text else "UNK"
                        if sentiment not in sent_list:
                            sentiment = "UNK"

                        # Create a tuple for the key: (bold_text, sentiment)
                        key = (' '.join(bold_text).strip(), sentiment)
                        # Store the plain text as the value in the dictionary
                        extracted_text[key] = ' '.join(plain_text).strip()

                        # Reset for the next phrase
                        bold_text = []
                        italic_text = []
                        plain_text = []
                        current_phase = "bold"

                    bold_text.append(text)
                elif 'italic' in fontname:
                    current_phase = "italic"
                    italic_text.append(text)
                else:
                    if current_phase == "italic" or current_phase == "bold":  # Add plain text after italic or bold text
                        plain_text.append(text)

            # Save the last extracted phrase on the page if any
            if bold_text and (italic_text or plain_text):
                # Determine sentiment
                sentiment = ' '.join(italic_text).strip().lower() if italic_text else "UNK"
                if sentiment not in sent_list:
                    sentiment = "UNK"

                key = (' '.join(bold_text).strip(), sentiment)
                extracted_text[key] = ' '.join(plain_text).strip()

    return extracted_text

def save_extracted_text_to_file(extracted_text, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for key, value in extracted_text.items():
            bold, italic = key
            f.write(f"Phrase: {bold}\n")
            f.write(f"Sentiment: {italic}\n")
            f.write(f"Meaning: {value}\n")
            f.write("\n")  # Add a blank line between entries

if __name__ == "__main__":
    pdf_file_path = 'rusdict.pdf'
    output_file_path = 'rus_phraseology.txt'
    # Extract the text
    extracted_text = extract_bold_italic_text_phrases(pdf_file_path, start_page=8, end_page=463)

    # Save the extracted text to a file
    save_extracted_text_to_file(extracted_text, output_file_path)

    print(f"Extracted text has been saved to {output_file_path}")
