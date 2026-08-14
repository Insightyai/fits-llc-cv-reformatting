import re
import unicodedata
from dataclasses import dataclass, field

# Fase 3 del agente de transformacion (ver agente/CONTRATO-AGENTE.md): checks
# deterministicos sobre el texto fuente ya extraido. Nunca decide solo, es la red
# de seguridad anti-invencion -- errors[] siempre implica estado `failed`.

_DASH_RE = re.compile(r"[‐-―−]")
_QUOTE_RE = re.compile(r"[‘’“”]")
_WS_RE = re.compile(r"\s+")
_TOKEN_SPLIT_RE = re.compile(r"[^\w]+", re.UNICODE)

LEGAL_SUFFIXES = {"inc", "llc", "corp", "corporation", "co", "ltd", "sa", "plc", "gmbh"}
STOPWORDS = {"the", "and", "of", "de", "la", "el", "los", "las"}

_PHONE_RE = re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")
_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
_METRIC_RE = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")

_I_EXCEPTIONS_BEFORE = {"phase", "level", "class", "type", "operator", "part"}
_ROMAN_NUMERAL_SEQUENCE_RE = re.compile(r"^\s*[&,/]\s*I{2,3}\b")

# Palabras genericas de vocabulario profesional que un summary reescrito (regla 4 del
# PRD) puede usar sin que esten literalmente en la fuente -- reduce ruido del check
# suave de la Fase 3. No es (ni pretende ser) un stemmer: "engineer"/"engineering" son
# formas distintas de la misma raiz y sin esta lista generarian un falso positivo real
# contra el propio fixture de Shirley Mercado.
SUMMARY_SOFT_STOPWORDS = {
    "engineer", "engineering", "professional", "operational", "compliance",
    "regulatory", "industry", "industries", "environment", "environmental",
    "settings", "controlled", "systems", "quality", "strengthening",
    "upholding", "ensuring", "sustainability", "programs", "tracking",
    "working", "managed", "management", "leadership", "communication",
    "international", "technical", "training", "skills", "background",
    "dedicated", "focused", "results", "driven", "detail", "oriented",
    "strong", "ability", "knowledge", "understanding", "various", "multiple",
    "several", "across", "within", "through", "between", "during", "include",
    "includes", "including", "related", "similar", "overall", "general",
    "specific", "particular", "current", "previous", "recent", "significant",
    "successful", "effective", "efficient", "comprehensive", "extensive",
    "substantial", "requirements", "hands-on",
}


@dataclass
class GroundingReport:
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


def normalize(text):
    text = (text or "").replace("&", " and ")
    text = _DASH_RE.sub("-", text)
    text = _QUOTE_RE.sub("'", text)
    text = text.casefold()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return _WS_RE.sub(" ", text).strip()


def despace(text):
    return normalize(text).replace(" ", "")


def significant_tokens(value):
    tokens = [t for t in _TOKEN_SPLIT_RE.split(normalize(value)) if t]
    tokens = [t for t in tokens if t not in STOPWORDS and t not in LEGAL_SUFFIXES]
    return [t for t in tokens if len(t) >= 3]


def extract_years(source_text):
    masked = _PHONE_RE.sub(lambda m: "#" * len(m.group()), source_text or "")
    return {m.group() for m in _YEAR_RE.finditer(masked)}


def extract_years_from_value(value):
    return {m.group() for m in _YEAR_RE.finditer(value or "")}


def extract_metrics(text):
    metrics = set()
    for m in _METRIC_RE.finditer(text or ""):
        bare = m.group().strip("$%").replace(",", "")
        if not bare or not any(c.isdigit() for c in bare):
            continue
        if _YEAR_RE.fullmatch(bare):
            continue  # los anios se chequean aparte (_check_years)
        metrics.add(bare)
    return metrics


_PERIOD_RANGE_RE = re.compile(
    r"(?:[A-Za-z]+\.?\s+\d{4}|\d{1,2}[/-]\d{4})\s*[-–—]\s*"
    r"(?:[A-Za-z]+\.?\s+\d{4}|\d{1,2}[/-]\d{4}|present|current|actualidad)",
    re.IGNORECASE,
)


def count_heuristic_jobs(source_text):
    """Cuenta rangos de fecha tipo 'Mes Anio - Mes Anio/Present' en la fuente, como
    proxy de cuantos empleos lista el CV original (cada empleo suele traer un rango).
    Heuristica, no estructura real -- solo dispara SECTION_COVERAGE_LOW (warning)."""
    return len(_PERIOD_RANGE_RE.findall(source_text or ""))


def _check_source_backed(value, source_words, error_code, warning_code, report, label):
    tokens = significant_tokens(value)
    if not tokens:
        report.warnings.append(f"{warning_code}: {label} sin tokens verificables")
        return
    if not any(t in source_words for t in tokens):
        report.errors.append(f"{error_code}: {label} no aparece en la fuente")


def _check_literal_soft(value, source_words, warning_code, report):
    tokens = significant_tokens(value)
    if tokens and not any(t in source_words for t in tokens):
        report.warnings.append(
            f"{warning_code}: {value!r} no matchea lexicamente la fuente (puede ser traduccion)"
        )


def _check_i_statement(text, report):
    if not text:
        return
    for m in re.finditer(r"\bI\b", text):
        preceding_words = text[: m.start()].split()
        prev = re.sub(r"[^a-zA-Z]", "", preceding_words[-1]).lower() if preceding_words else ""
        following = text[m.end() : m.end() + 12]
        if prev in _I_EXCEPTIONS_BEFORE or following.lower().startswith("/o"):
            continue
        if _ROMAN_NUMERAL_SEQUENCE_RE.match(following):
            continue
        snippet = text[max(0, m.start() - 20) : m.end() + 10].strip()
        report.errors.append(f"GROUNDING_I_STATEMENT: {snippet!r}")

    for word in ("my", "mine"):
        for m in re.finditer(rf"\b{word}\b", text, re.IGNORECASE):
            snippet = text[max(0, m.start() - 20) : m.end() + 10].strip()
            report.errors.append(f"GROUNDING_I_STATEMENT: {snippet!r}")

    # case-sensitive a proposito: excluye "ME"/"Me" (Maine, Mechanical Engineering)
    for m in re.finditer(r"\bme\b", text):
        snippet = text[max(0, m.start() - 20) : m.end() + 10].strip()
        report.errors.append(f"GROUNDING_I_STATEMENT: {snippet!r}")


def _check_metrics(bullet, source_metrics, translated, report):
    for metric in extract_metrics(bullet):
        if metric in source_metrics:
            continue
        snippet = bullet[:60] + ("..." if len(bullet) > 60 else "")
        if translated:
            report.warnings.append(f"METRIC_NOT_VERIFIED: {metric!r} (bullet: {snippet!r})")
        else:
            report.errors.append(f"GROUNDING_METRIC_NOT_FOUND: {metric!r} (bullet: {snippet!r})")


def _check_summary_claims(summary, source_words, report):
    tokens = {t for t in _TOKEN_SPLIT_RE.split(normalize(summary)) if t}
    flagged = sorted(
        w for w in tokens if len(w) >= 7 and w not in SUMMARY_SOFT_STOPWORDS and w not in source_words
    )
    if flagged:
        report.warnings.append(f"SUMMARY_CLAIM_NOT_VERIFIED: {', '.join(flagged)} no aparece en la fuente")


def evaluate(cv, source_text):
    """Evalua el CV transformado contra el texto fuente ya extraido. Nunca lanza --
    devuelve un GroundingReport; el llamador decide el estado (ok/review/failed,
    ver agente/CONTRATO-AGENTE.md)."""
    report = GroundingReport()
    source_norm = normalize(source_text)
    source_desp = despace(source_text)
    source_words = {t for t in _TOKEN_SPLIT_RE.split(source_norm) if t}
    source_years = extract_years(source_text)
    source_metrics = extract_metrics(source_text)
    translated = bool(cv.get("_meta", {}).get("translated"))

    name_tokens = [t for t in normalize(cv.get("full_name", "")).split() if len(t) >= 3]
    missing_name = [t for t in name_tokens if t not in source_desp]
    if missing_name:
        report.errors.append(
            f"GROUNDING_NAME_NOT_FOUND: {', '.join(missing_name)} no aparece en la fuente"
        )

    town = cv.get("town")
    if town:
        if normalize(town) not in source_norm:
            report.errors.append(f"GROUNDING_TOWN_NOT_FOUND: town={town!r} no aparece en la fuente")
        else:
            town_norm = normalize(town)
            employer_locations = [
                normalize(job.get("location") or "") for job in cv.get("experience", [])
            ]
            if any(loc and (town_norm in loc or loc in town_norm) for loc in employer_locations):
                report.warnings.append(
                    f"TOWN_MAY_BE_EMPLOYER_CITY: town={town!r} coincide con la ciudad de un empleador"
                )

    experience = cv.get("experience", [])
    periods = [job.get("period") for job in experience] + [
        edu.get("period") for edu in cv.get("education", [])
    ]
    any_period = any(p and p.strip() for p in periods)
    years_checkable = bool(source_years)
    if any_period and not years_checkable:
        report.warnings.append(
            "YEARS_NOT_VERIFIABLE_IN_SOURCE: la fuente no tiene anios de 4 digitos reconocibles"
        )

    for job in experience:
        _check_source_backed(
            job.get("company", ""), source_words,
            "GROUNDING_TOKEN_NOT_FOUND", "COMPANY_NOT_VERIFIABLE", report,
            label=f"company={job.get('company')!r}",
        )
        _check_literal_soft(job.get("title", ""), source_words, "TITLE_NOT_LITERAL_IN_SOURCE", report)

        period = job.get("period") or ""
        if not period.strip():
            report.warnings.append("EMPTY_PERIOD: un empleo llego sin fechas")
        elif years_checkable:
            for year in extract_years_from_value(period):
                if year not in source_years:
                    report.errors.append(
                        f"GROUNDING_YEAR_NOT_FOUND: {year} (periodo {period!r}) no esta en la fuente"
                    )

        for bullet in job.get("bullets", []):
            _check_i_statement(bullet, report)
            _check_metrics(bullet, source_metrics, translated, report)

    _check_i_statement(cv.get("summary", ""), report)

    education = cv.get("education", [])
    if not education:
        report.warnings.append("NO_EDUCATION_SECTION: el CV no trae seccion de educacion")
    for edu in education:
        _check_literal_soft(
            edu.get("institution", ""), source_words, "INSTITUTION_NOT_LITERAL_IN_SOURCE", report
        )
        period = edu.get("period")
        if period is not None and not period.strip():
            report.warnings.append("EMPTY_PERIOD: educacion sin fechas")
        elif period and years_checkable:
            for year in extract_years_from_value(period):
                if year not in source_years:
                    report.errors.append(
                        f"GROUNDING_YEAR_NOT_FOUND: {year} (periodo {period!r}) no esta en la fuente"
                    )

    for cert in cv.get("certifications", []):
        _check_source_backed(
            cert, source_words, "GROUNDING_TOKEN_NOT_FOUND", "COMPANY_NOT_VERIFIABLE", report,
            label=f"certification={cert!r}",
        )
    for skill in cv.get("skills", []):
        _check_source_backed(
            skill, source_words, "GROUNDING_TOKEN_NOT_FOUND", "COMPANY_NOT_VERIFIABLE", report,
            label=f"skill={skill!r}",
        )

    heuristic_jobs = count_heuristic_jobs(source_text)
    if heuristic_jobs > len(experience):
        report.warnings.append(
            f"SECTION_COVERAGE_LOW: la fuente parece tener {heuristic_jobs} empleo(s), "
            f"el CV transformado trae {len(experience)}"
        )

    _check_summary_claims(cv.get("summary", ""), source_words, report)

    return report
