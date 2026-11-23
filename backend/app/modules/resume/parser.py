
"""PDF text extraction for the Resume module."""

from io import BytesIO
from pypdf import PdfReader, apply_configuration


MAX_RESUME_PAGES = 30
MAX_RESUME_TEXT = 100000
MAX_STREAM_BYTES = 2 * 1024 * 1024


class ResumeParseError(ValueError):
    """Raised when a resume cannot be read or contains no usable text."""


def extract_resume_text(pdf_bytes: bytes) -> str:
    if not pdf_bytes:
        raise ResumeParseError("The uploaded PDF is empty.")

    try:
        with apply_configuration(
            maximum_declared_stream_length=MAX_STREAM_BYTES,
            array_based_stream_maximum_output_length=MAX_STREAM_BYTES,
            zlib_maximum_output_length=MAX_STREAM_BYTES,
            zlib_maximum_recovery_input_length=MAX_STREAM_BYTES,
            lzw_maximum_output_length=MAX_STREAM_BYTES,
            run_length_maximum_output_length=MAX_STREAM_BYTES,
            brotli_maximum_output_length=MAX_STREAM_BYTES,
            stream_decoding_work_maximum_length=4 * MAX_STREAM_BYTES,
            page_tree_maximum_entries=1000,
            page_tree_maximum_depth=30,
            xform_maximum_invocations_per_extraction=100,
            jbig2dec_binary=None,
        ):
            reader = PdfReader(BytesIO(pdf_bytes), strict=False)
            if reader.is_encrypted:
                raise ResumeParseError("Password-protected PDFs are not supported.")
            if len(reader.pages) > MAX_RESUME_PAGES:
                raise ResumeParseError(f"Resume PDF must have at most {MAX_RESUME_PAGES} pages.")
            pages = []
            length = 0
            for page in reader.pages:
                text = (page.extract_text() or "").strip()
                length += len(text)
                if length > MAX_RESUME_TEXT:
                    raise ResumeParseError("Resume PDF contains too much text.")
                if text:
                    pages.append(text)
            extracted_text = "\n\n".join(pages).strip()

    except ResumeParseError:
        raise
    except Exception as exc:
        raise ResumeParseError(
            "The PDF could not be read. Please upload a valid PDF."
        ) from exc

    if not extracted_text:
        raise ResumeParseError(
            "No readable text found. The PDF may be scanned; "
            "OCR support is not implemented yet."
        )

    return extracted_text
