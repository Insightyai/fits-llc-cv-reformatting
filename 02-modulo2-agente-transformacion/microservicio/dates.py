import re

# Criterio v1 (ver agente/CONTRATO-AGENTE.md): suma de periodos de experience[] sin
# solapamiento, a partir de fechas explicitas. "Present"/"Actualidad"/etc. se resuelve
# contra `now`, siempre inyectado (nunca datetime.now() embebido) -- el propio fixture
# de Shirley Mercado solo da "4" entre abril 2026 y marzo 2027, un test sin `now`
# congelado se rompe solo con el paso del calendario.

MONTHS = {
    "jan": 1, "january": 1, "enero": 1, "ene": 1,
    "feb": 2, "february": 2, "febrero": 2,
    "mar": 3, "march": 3, "marzo": 3,
    "apr": 4, "april": 4, "abril": 4, "abr": 4,
    "may": 5, "mayo": 5,
    "jun": 6, "june": 6, "junio": 6,
    "jul": 7, "july": 7, "julio": 7,
    "aug": 8, "august": 8, "agosto": 8, "ago": 8,
    "sep": 9, "sept": 9, "september": 9, "septiembre": 9, "setiembre": 9,
    "oct": 10, "october": 10, "octubre": 10,
    "nov": 11, "november": 11, "noviembre": 11,
    "dec": 12, "december": 12, "diciembre": 12, "dic": 12,
}

PRESENT_WORDS = {"present", "current", "actualidad", "a la fecha", "actual", "presente", "hoy"}

_MONTH_YEAR_RE = re.compile(r"^([a-záéíóúñ]+)\.?\s+(\d{4})$", re.IGNORECASE)
_NUMERIC_RE = re.compile(r"^(\d{1,2})[/-](\d{4})$")
_YEAR_ONLY_RE = re.compile(r"^(\d{4})$")


def _parse_token(token):
    """None si no parsea, 'present' si es una variante de 'presente', o
    (year, month, approx) donde approx=True si solo habia anio (se asume enero)."""
    token = token.strip().lower().rstrip(".")
    if token in PRESENT_WORDS:
        return "present"
    m = _MONTH_YEAR_RE.match(token)
    if m:
        month_name, year = m.groups()
        month = MONTHS.get(month_name)
        return (int(year), month, False) if month else None
    m = _NUMERIC_RE.match(token)
    if m:
        month, year = m.groups()
        month = int(month)
        return (int(year), month, False) if 1 <= month <= 12 else None
    m = _YEAR_ONLY_RE.match(token)
    if m:
        return (int(m.group(1)), 1, True)
    return None


def parse_period(period):
    """Devuelve (start, end, approx) o None si no se pudo interpretar.
    start/end son (year, month) o 'present'. approx=True si alguno de los dos
    lados solo traia el anio (precision reducida -- ver AMBIGUOUS_DATES)."""
    if not period or not period.strip():
        return None
    normalized = period.replace("–", "-").replace("—", "-")
    normalized = re.sub(r"\bto\b", "-", normalized, flags=re.IGNORECASE)
    parts = [p.strip() for p in normalized.split("-", 1)]
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return None

    start = _parse_token(parts[0])
    if start is None or start == "present":
        return None

    end = _parse_token(parts[1])
    if end is None:
        return None

    approx = start[2] or (end != "present" and end[2])
    start_ym = (start[0], start[1])
    end_ym = "present" if end == "present" else (end[0], end[1])
    return start_ym, end_ym, approx


def _to_index(year_month):
    year, month = year_month
    return year * 12 + (month - 1)


def calculate_years_experience(experience, now):
    """Devuelve (valor: str|None, warnings: list[str]). Nunca inventa un numero:
    si algun periodo no parsea, valor=None + YEARS_EXPERIENCE_UNKNOWN."""
    if not experience:
        return None, ["YEARS_EXPERIENCE_UNKNOWN: no hay experiencia registrada"]

    intervals = []
    any_approx = False
    for job in experience:
        parsed = parse_period(job.get("period") or "")
        if parsed is None:
            return None, [
                f"YEARS_EXPERIENCE_UNKNOWN: periodo no interpretable: {job.get('period')!r}"
            ]
        start, end, approx = parsed
        any_approx = any_approx or approx
        end_ym = (now.year, now.month) if end == "present" else end
        if _to_index(end_ym) < _to_index(start):
            return None, [
                f"YEARS_EXPERIENCE_UNKNOWN: periodo con fin anterior al inicio: {job.get('period')!r}"
            ]
        intervals.append((_to_index(start), _to_index(end_ym)))

    merged = []
    for s, e in sorted(intervals):
        if merged and s <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))

    total_months = sum(e - s + 1 for s, e in merged)
    years = total_months // 12
    if years <= 0:
        return None, ["YEARS_EXPERIENCE_UNKNOWN: experiencia total menor a un anio"]

    warnings = ["AMBIGUOUS_DATES: al menos un periodo solo trae el anio, se asumio enero"] if any_approx else []
    return str(years), warnings
