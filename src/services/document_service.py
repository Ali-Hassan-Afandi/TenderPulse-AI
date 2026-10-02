from io import BytesIO
from pypdf import PdfReader
from docx import Document

def extract_text(uploaded):
    name=uploaded.name.lower()
    data=uploaded.getvalue()
    if name.endswith(".pdf"):
        reader=PdfReader(BytesIO(data))
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    if name.endswith(".docx"):
        doc=Document(BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")
    return ""
