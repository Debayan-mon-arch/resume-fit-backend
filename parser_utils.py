import fitz  # for PDF
from docx import Document

def extract_text(file_storage):
    try:
        filename = file_storage.filename.lower()
        text = ""

        if filename.endswith(".pdf"):
            file_storage.stream.seek(0)
            doc = fitz.open(stream=file_storage.read(), filetype="pdf")
            for page in doc:
                text += page.get_text()
            doc.close()

        elif filename.endswith(".docx"):
            file_storage.stream.seek(0)
            doc = Document(file_storage)
            text = " ".join([p.text for p in doc.paragraphs])

        return text.replace("\n", " ").strip().lower()

    except Exception as e:
        print(f"Failed to extract text: {e}")
        return ""
