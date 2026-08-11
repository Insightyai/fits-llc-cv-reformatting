import io
import re
import unicodedata
from dataclasses import dataclass, field

import pypdf
from docx import Document

# Fase 1 del agente de transformacion (ver agente/CONTRATO-AGENTE.md).
# Extraccion de texto sin LLM: si esto falla o detecta NO_TEXT_LAYER, nunca se llama a Claude.

MIN_CHARS = 400
MIN_WORDS = 40
MAX_CHARS = 20000

# Empiricamente derivado del PDF real de Shirley Mercado extraido con pypdf: el kerning de
# ciertas fuentes hace que headers como "PROFILE"/"EXPERIENCE"/"EDUCATION"/"SKILLS"/
# "CERTIFICATIONS"/"REFERENCES" salgan partidos letra por letra ("PR O FIL E", "E XPER IENC E").
# Heuristica: una linea completa de >=3 tokens, cada uno 1-4 letras mayusculas, se colapsa sin
# espacios. No es perfecto (una linea real tipo "SAN JUAN PR" tambien matchearia) -- aceptable
# porque esta normalizacion solo afecta el texto que ve el LLM, nunca el grounding contra el
# texto crudo.
_LETTER_SPACING_RE = re.compile(r"^(?:[A-Z]{1,4}\s+){2,}[A-Z]{1,4}$")


class ExtractionError(Exception):
    def __init__(self, code, detail):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


@dataclass
class ExtractResult:
    text: str
    kind: str
    units: int
    truncated: bool = False
    warnings: list = field(default_factory=list)


def _sniff_kind(data: bytes) -> str:
    if data[:5] == b"%PDF-":
        return "pdf"
    if data[:2] == b"PK":
        return "docx"
    if data[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        return "legacy_doc"
    return "text"


def _extract_pdf(data: bytes):
    reader = pypdf.PdfReader(io.BytesIO(data))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages), len(reader.pages)


def _extract_docx(data: bytes):
    doc = Document(io.BytesIO(data))
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs), len(paragraphs)


def _fix_letter_spacing(text: str) -> str:
    fixed_lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if _LETTER_SPACING_RE.match(stripped):
            fixed_lines.append(stripped.replace(" ", ""))
        else:
            fixed_lines.append(line)
    return "\n".join(fixed_lines)


def _sanitize(text: str) -> str:
    text = "".join(
        ch for ch in text
        if ch in ("\n", "\t") or unicodedata.category(ch)[0] != "C"
    )
    text = unicodedata.normalize("NFKC", text)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    cleaned, blank_run = [], 0
    for line in lines:
        if line == "":
            blank_run += 1
            if blank_run > 1:
                continue
        else:
            blank_run = 0
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def extract_text(filename: str, data: bytes) -> ExtractResult:
    kind = _sniff_kind(data)

    if kind == "legacy_doc":
        raise ExtractionError(
            "CORRUPT_FILE", f"{filename}: formato .doc legacy (binario, pre-2007) no soportado, se requiere PDF o DOCX"
        )

    try:
        if kind == "pdf":
            raw, units = _extract_pdf(data)
        elif kind == "docx":
            raw, units = _extract_docx(data)
        else:
            kind = "text"
            raw, units = data.decode("utf-8", errors="replace"), 1
    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError(
            "CORRUPT_FILE", f"no se pudo leer {filename} como {kind}: {exc}"
        ) from exc

    raw = _fix_letter_spacing(raw)
    clean = _sanitize(raw)

    words = clean.split()
    if len(clean) < MIN_CHARS or len(words) < MIN_WORDS:
        raise ExtractionError(
            "NO_TEXT_LAYER",
            f"solo {len(clean)} caracteres / {len(words)} palabras extraidas de "
            f"{units} pagina(s)/parrafo(s) ({filename}) -- CV probablemente escaneado "
            "o sin capa de texto",
        )

    warnings = []
    truncated = False
    if len(clean) > MAX_CHARS:
        clean = clean[:MAX_CHARS]
        truncated = True
        warnings.append(f"SOURCE_TRUNCATED: texto cortado a {MAX_CHARS} caracteres")

    return ExtractResult(text=clean, kind=kind, units=units, truncated=truncated, warnings=warnings)
