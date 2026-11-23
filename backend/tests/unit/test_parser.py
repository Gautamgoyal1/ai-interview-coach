"""Unit tests for resume PDF parsing."""

from io import BytesIO

import pytest
from pypdf import PdfWriter

from app.modules.resume.parser import (
    ResumeParseError,
    extract_resume_text,
)


def create_text_pdf(text: str) -> bytes:
    """Create a small PDF containing extractable text."""
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(72, 750, text)
    pdf.save()
    return buffer.getvalue()


def test_empty_pdf_bytes_are_rejected():
    with pytest.raises(ResumeParseError, match="uploaded PDF is empty"):
        extract_resume_text(b"")


def test_invalid_pdf_bytes_are_rejected():
    with pytest.raises(ResumeParseError, match="could not be read"):
        extract_resume_text(b"This is not a PDF")


def test_text_pdf_extracts_content():
    pdf_bytes = create_text_pdf(
        "Python developer with machine learning experience"
    )

    result = extract_resume_text(pdf_bytes)

    assert "Python developer" in result
    assert "machine learning" in result


def test_pdf_without_readable_text_is_rejected():
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)

    buffer = BytesIO()
    writer.write(buffer)

    with pytest.raises(ResumeParseError, match="No readable text found"):
        extract_resume_text(buffer.getvalue())


def test_encrypted_pdf_is_rejected():
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.encrypt("test-password")

    buffer = BytesIO()
    writer.write(buffer)

    with pytest.raises(
        ResumeParseError,
        match="Password-protected PDFs are not supported",
    ):
        extract_resume_text(buffer.getvalue())


def test_many_page_pdf_is_rejected_before_text_extraction():
    writer = PdfWriter()
    for _ in range(31):
        writer.add_blank_page(width=100, height=100)
    buffer = BytesIO()
    writer.write(buffer)
    with pytest.raises(ResumeParseError, match="at most 30 pages"):
        extract_resume_text(buffer.getvalue())


def test_text_length_limit_is_enforced(monkeypatch):
    from app.modules.resume import parser

    monkeypatch.setattr(parser, "MAX_RESUME_TEXT", 10)
    with pytest.raises(ResumeParseError, match="too much text"):
        extract_resume_text(create_text_pdf("Python developer experience"))


def test_compressed_stream_limit_is_enforced_and_configuration_is_restored(monkeypatch):
    from pypdf import PdfReader, get_configuration
    from pypdf.generic import DecodedStreamObject, NameObject
    from app.modules.resume import parser

    previous = get_configuration()
    writer = PdfWriter()
    page = writer.add_page(PdfReader(BytesIO(create_text_pdf("Python developer"))).pages[0])
    stream = DecodedStreamObject()
    stream.set_data(b"BT /F1 12 Tf 10 10 Td (Python developer) Tj ET\n" + b" " * 4096)
    page[NameObject("/Contents")] = writer._add_object(stream.flate_encode())
    buffer = BytesIO()
    writer.write(buffer)
    assert len(buffer.getvalue()) < 2048  # Small compressed fixture, not a resource stress test.
    assert "Python developer" in extract_resume_text(buffer.getvalue())
    monkeypatch.setattr(parser, "MAX_STREAM_BYTES", 1024)
    # Some pypdf versions return empty text after rejecting a content stream;
    # either controlled parse failure must prevent accepting the readable payload.
    with pytest.raises(ResumeParseError):
        extract_resume_text(buffer.getvalue())
    assert get_configuration() == previous
