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


def test_docx_name_in_page_header_included():
    # patron real de candidato FITS (Raul Gomez Perez, 24 ago 2026): el nombre esta puesto
    # en el header de pagina de Word, no en el cuerpo -- python-docx doc.paragraphs no lo lee,
    # asi que el LLM nunca ve el nombre y grounding.py bloquea con GROUNDING_NAME_NOT_FOUND.
    doc = docx.Document()
    doc.sections[0].header.paragraphs[0].text = "Jane Doe, M.S."
    doc.add_paragraph("PROFESSIONAL SUMMARY")
    doc.add_paragraph("Engineer with " + " ".join(["experience"] * 60))
    buf = io.BytesIO()
    doc.save(buf)

    result = extract_text("cv.docx", buf.getvalue())

    assert "Jane Doe" in result.text


IBRAHIM_PDF_PATH = CV_PDF_PATH.parent / "Resume- Ibrahim Rivas Andino.pdf"


def test_pdf_floating_dates_reattached_to_role():
    # patron real de candidato FITS (Ibrahim Rivas Andino, 4 sep 2026): el template usa
    # un text-box flotante a la derecha para la fecha de cada rol, separado del bloque de
    # titulo/empresa -- pypdf extrae en el orden del stream del PDF, no en orden visual,
    # asi que las 4 fechas de este CV salian todas agrupadas al principio del texto,
    # desconectadas de a que rol pertenece cada una (el New Format generado mostraba
    # fechas desplazadas/mal atribuidas). El fix reubica cada fecha justo despues del
    # titulo del rol con el que comparte fila (misma coordenada y) -- el tab que inserta
    # el fix se colapsa a un espacio en _sanitize(), igual que cualquier otro tab/espacio
    # del texto extraido, asi que se verifica con un espacio simple.
    data = IBRAHIM_PDF_PATH.read_bytes()
    result = extract_text("Resume- Ibrahim Rivas Andino.pdf", data)

    assert (
        "Quality Assurance & System Validation Specialist (QA Approval Authority)"
        " March 2026 – Present" in result.text
    )
    assert "Quality Control & Quality Assurance Auditor January 2025 – March 2026" in result.text
    assert "Associate Quality Control 2022 – 2025" in result.text
    assert "Manufacturing Associate 2018 – 2021" in result.text
    # las fechas ya no deben quedar sueltas y agrupadas al principio del texto, antes del
    # nombre del candidato (sintoma original del bug)
    assert result.text.index("IBRAHIM") < result.text.index("March 2026 – Present")


def test_pdf_real_shirley_mercado_unaffected_by_date_reattach_fix():
    # regresion: Shirley (y Yajaira/Luis, cubiertos solo manualmente durante el
    # diagnostico) tambien tienen la fecha de cada rol como fragmento de texto aparte,
    # pero el orden del stream de esos PDFs ya las deja pegadas a su fila -- el fix debe
    # ser un no-op para estos casos, nunca debe tocar un texto que ya estaba bien.
    data = CV_PDF_PATH.read_bytes()
    result = extract_text("Resume- Shirley Mercado.pdf", data)
    assert "Caribbean Refrescos, Inc |Cidra, PR" in result.text
    assert "May 2024" in result.text
    assert "Baxter International Inc. | Aibonito, PR" in result.text
    assert "April 2022" in result.text


def test_docx_table_content_included():
    # patron real de candidata FITS (Carmen Lopez, 4 sep 2026): skills y los 10 roles de
    # experiencia estan en tablas de Word, no en parrafos sueltos -- python-docx doc.paragraphs
    # no las lee, asi que el LLM solo vio 1 rol de 5 y ningun skill, generando un resume
    # incompleto (Convert Resume - New Format) sin que grounding.py lo bloqueara (no hay
    # invencion, solo ausencia de contenido real).
    doc = docx.Document()
    doc.add_paragraph("PROFESSIONAL SUMMARY")
    doc.add_paragraph("Engineer with " + " ".join(["experience"] * 60))
    table = doc.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text = "2023 to present"
    table.rows[0].cells[1].text = "QC LABORATORY SCIENTIST\nAbbVie Biotechnology Ltd."
    buf = io.BytesIO()
    doc.save(buf)

    result = extract_text("cv.docx", buf.getvalue())

    assert "AbbVie Biotechnology Ltd." in result.text
    assert "2023 to present" in result.text


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


def test_legacy_doc_rejected():
    # firma OLE2/CFB real de un .doc binario (formato Word pre-2007) descargado de un
    # candidato real de FITS: sin esta deteccion, cae al fallback de texto plano
    # (utf-8 errors="replace") y produce basura decodificable que el LLM alucina como CV real.
    data = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 500
    with pytest.raises(ExtractionError) as exc_info:
        extract_text("resume.doc", data)
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


JAVIER_PDF_PATH = CV_PDF_PATH.parent / "Resume- Javier Rivera Delgado.pdf"


def test_pdf_pervasive_letter_spacing_from_canva():
    # patron real de candidato FITS (Javier Rivera-Delgado, 8 sep 2026): un PDF generado con
    # Canva separa cada caracter con un espacio simple en TODO el cuerpo del texto, no solo en
    # los encabezados de seccion ("I n d u s t r i a l m a i n t e n a n c e..."). A diferencia
    # del caso de Shirley Mercado (headers en chunks de 2-4 letras), aca la unica pista
    # recuperable es que pypdf preserva el espacio real entre palabras como espacio DOBLE
    # (el espacio ancho del PDF) contra el espacio simple entre letras -- se pierde en cuanto
    # _sanitize() colapsa espacios repetidos, asi que el fix tiene que reconstruir las palabras
    # antes de eso. Sin este fix, grounding.py bloqueaba con 17 GROUNDING_TOKEN_NOT_FOUND
    # (empresas, certificaciones y skills reales que el modelo si transcribio bien, pero que
    # nunca aparecen como substring literal en la fuente destrozada letra por letra).
    data = JAVIER_PDF_PATH.read_bytes()
    result = extract_text("Resume- Javier Rivera Delgado.pdf", data)

    assert "Optima" in result.text
    assert "Kerry Ingredients" in result.text
    assert "Polaris" in result.text
    assert "Lakeside Foods" in result.text
    assert "Amgen LTD" in result.text
    assert "US Cotton LLC" in result.text
    assert "Bristol Myers Squibb" in result.text
    assert "McNeil" in result.text
    assert "Huertas College" in result.text
    assert "Industrial Welding" in result.text
    assert "Kaizen Certification" in result.text
    assert "Instrumentation" in result.text
    assert "Team Leadership" in result.text
    assert "javierboricua91@gmail.com" in result.text
    assert "787-909-4443" in result.text
