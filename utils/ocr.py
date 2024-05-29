from pdf2image import convert_from_path
import pytesseract
import os
os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr/4.00/tessdata"

# Path to the PDF file
def get_hindi_text(pdf_path):
    print("here")
    pages = convert_from_path(pdf_path, 300)

    all_text = ''
    for i, page in enumerate(pages):
        text = pytesseract.image_to_string(page, lang='hin')
        all_text += f'Page {i + 1}:\n{text}\n\n'

    print('OCR complete.')
    return all_text

