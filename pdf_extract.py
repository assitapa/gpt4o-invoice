import fitz # PyMuPDF

def extract_text_from_pdf(file_path):
    # Open the PDF file
    doc = fitz.open(file_path)
    text = ''
    for page in doc:
        text += page.get_text()
    doc.close()
    return text