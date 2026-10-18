from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

base = Path(__file__).resolve().parent.parent
resume_path = base / "tests" / "fixtures" / "sample_resume.txt"
pdf_path = base / "tests" / "fixtures" / "sample_resume.pdf"

text = resume_path.read_text(encoding="utf-8")
pdf = canvas.Canvas(str(pdf_path), pagesize=letter)
width, height = letter

x = 50
y = height - 50

for line in text.splitlines():
    if y < 50:
        pdf.showPage()
        y = height - 50

    pdf.drawString(x, y, line[:110])
    y -= 16

pdf.save()
print(f"Created synthetic resume PDF: {pdf_path}")