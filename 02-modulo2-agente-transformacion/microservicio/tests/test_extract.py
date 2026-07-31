import io
import pathlib

import docx
import pypdf
import pytest

from extract import ExtractionError, extract_text

CV_PDF_PATH = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "cvs-prueba"
    / "Resume- Shirley Mercado.pdf"
)


def test_pdf_real_shirley_mercado():
    data = CV_PDF_PATH.read_bytes()
    result = extract_text("Resume- Shirley Mercado.pdf", data)

    assert result.kind == "pdf"
    assert result.units == 1
    assert not result.truncated
    assert "Caribbean Refrescos" in result.text
    assert "Baxter International" in result.text
    for year in ("2019", "2022", "2024"):
        assert year in result.text
    # headers que pypdf destroza letra por letra ("PR O FIL E", "E XPER IENC E", ...)
    # deben quedar reconstruidos por el fix de letter-spacing
    for header in ("PROFILE", "EXPERIENCE", "EDUCATION", "SKILLS", "CERTIFICATIONS"):
        assert header in result.text


def _build_docx_bytes(paragraphs):
    doc = docx.Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_docx_synthetic():
    paragraphs = ["Jane Doe", "Software Engineer with " + " ".join(["experience"] * 60)]
    data = _build_docx_bytes(paragraphs)
    result = extract_text("cv.docx", data)

    assert result.kind == "docx"
    assert result.units == len(paragraphs)
    assert "Jane Doe" in result.text


def test_plain_text_fallback():
    # cubre el fallback de JazzHR (`resumeMeta`) que devuelve texto plano, no un archivo
    text = "Jane Doe\nSoftware Engineer with " + " ".join(["experience"] * 60)
    data = text.encode("utf-8")
    result = extract_text("resumeMeta.txt", data)

    assert result.kind == "text"
    assert "Jane Doe" in result.text


def _blank_pdf_bytes():
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_no_text_layer_blank_pdf():
    data = _blank_pdf_bytes()
    with pytest.raises(ExtractionError) as exc_info:
        extract_text("blank.pdf", data)
    assert exc_info.value.code == "NO_TEXT_LAYER"


def test_no_text_layer_short_text():
    with pytest.raises(ExtractionError) as exc_info:
        extract_text("short.txt", b"Hi")
    assert exc_info.value.code == "NO_TEXT_LAYER"


def test_corrupt_pdf():
    data = b"%PDF-1.4\nnot a real pdf structure at all, truncated garbage"
    with pytest.raises(ExtractionError) as exc_info:
        extract_text("corrupt.pdf", data)
    assert exc_info.value.code == "CORRUPT_FILE"


def test_corrupt_docx():
    data = b"PK\x03\x04" + b"garbage not a real zip/docx" * 5
    with pytest.raises(ExtractionError) as exc_info:
        extract_text("corrupt.docx", data)
    assert exc_info.value.code == "CORRUPT_FILE"


def test_source_truncated():
    long_text = "word " * 10000  # ~50000 chars, arriba de MAX_CHARS
    data = long_text.encode("utf-8")
    result = extract_text("long.txt", data)

    assert result.truncated
    assert any(w.startswith("SOURCE_TRUNCATED") for w in result.warnings)


def test_letter_spacing_preserves_real_allcaps_lines():
    # mismo patron que "BS ENVIRONMENTAL ENGINEERING" en el CV real: mayusculas legitimas
    # con palabras largas no deben colapsarse, solo las lineas realmente partidas letra a letra
    text = "Jane Doe\n" + "word " * 100 + "\nBS COMPUTER SCIENCE\n"
    result = extract_text("cv.txt", text.encode("utf-8"))

    assert "BS COMPUTER SCIENCE" in result.text
