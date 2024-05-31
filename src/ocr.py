from pdf2image import convert_from_path
import pytesseract
import os
os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr/4.00/tessdata"

# Path to the PDF file
def get_hindi_text(pdf_path):
    pages = convert_from_path(pdf_path, 300)

    all_text = ''
    for i, page in enumerate(pages):
        text = pytesseract.image_to_string(page, lang='hin')
        all_text += f'{text}\n'

    print('OCR complete.')
    return all_text

def merge_lines_between_empty_lines(text):
    lines = text.split('\n')
    merged_lines = []
    current_block = []
    for line in lines:
        if not line.strip():
            if current_block:
                merged_lines.append(' '.join(current_block))
                current_block = []
            merged_lines.append('')
        else:
            current_block.append(line.strip())
    if current_block:
        merged_lines.append(' '.join(current_block))
    fixed_text = '\n'.join(merged_lines)
    return fixed_text