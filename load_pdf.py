import fitz  # PyMuPDF

def load_pdf(path: str) -> str:
    """
    Load text from a PDF using PyMuPDF.
    """
    doc = fitz.open(path)
    text = ""

    for page in doc:
        text += page.get_text()

    return text
