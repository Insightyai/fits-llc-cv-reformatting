import re

from dates import combine_periods

_MONTH_ABBR_RE = re.compile(r"\b(Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\b(?!\.)")
_HYPHEN_RANGE_RE = re.compile(r"\s-\s")
_ABBREV_MISSING_DOT_RE = re.compile(r"\(([A-Z]\.[A-Z])\)")
_GPA_COMMA_RE = re.compile(r"(GPA:\s*[\d.]+),(\s*Thesis:)")
_PERCENT_RANGE_RE = re.compile(r"(\d+)-(\d+)%")


def format_period_for_display(period):
    """Agrega punto tras abreviaturas de mes y normaliza el separador a raya larga
    (canon de Paola: 'Jan. 2021 – Dec. 2025'), nunca cambia el contenido semantico
    de la fecha -- solo puntuacion, aplicado despues de que grounding.py ya valido el
    periodo crudo."""
    if not period:
        return period
    period = _MONTH_ABBR_RE.sub(lambda m: m.group(0) + ".", period)
    period = _HYPHEN_RANGE_RE.sub(" – ", period)
    return period


def _fix_abbrev_missing_dot(text):
    """'(B.S)' -> '(B.S.)' -- abreviatura de 2 letras a la que le falta el punto
    final, patron encontrado en output real del agente (Steven Palmer-Velazquez)."""
    text = _ABBREV_MISSING_DOT_RE.sub(lambda m: f"({m.group(1)}.)", text)
    text = _GPA_COMMA_RE.sub(lambda m: f"{m.group(1)}.{m.group(2)}", text)
    return text


def format_bullet_text(text):
    """Normaliza puntuacion de bullets sin tocar el contenido: rango numerico con
    '%' usa raya larga, no guion (canon de Paola: '15-20%' -> '15–20%')."""
    return _PERCENT_RANGE_RE.sub(lambda m: f"{m.group(1)}–{m.group(2)}%", text)


def format_education_entry(e):
    return {"degree": _fix_abbrev_missing_dot(e["degree"]), "institution": e["institution"]}


def build_education_entries(education):
    return [format_education_entry(e) for e in education]


def _company_key(x):
    return (x["company"], x.get("location"))


def build_experience_companies(experience, role_period_style="tab"):
    """Agrupa experience[] por empresa consecutiva (mismo patron en los 6 CVs canon
    de Paola: un candidato con dos roles seguidos en la misma empresa, sin haberse ido
    entremedio, se muestra como un solo encabezado de empresa -- con el periodo total
    de la permanencia -- y un sub-encabezado en negrita por rol, con su propio periodo
    solo cuando hay 2+ roles agrupados. Empresas no consecutivas (el candidato volvio
    despues de trabajar en otro lado) no se agrupan.

    role_period_style controla como se muestra el periodo del rol cuando difiere del
    periodo combinado de la empresa: "tab" (New Format/Non Template, columna a la
    derecha) o "parens" (BD Format, canon de Edgeliz Ramos Rosario: "Engineer I
    (Oct. 2023 - Present)", inline)."""
    companies = []
    for x in experience:
        if companies and _company_key(companies[-1]["_source"][-1]) == _company_key(x):
            companies[-1]["_source"].append(x)
        else:
            companies.append({"_source": [x]})

    result = []
    for company in companies:
        roles = company["_source"]
        first = roles[0]
        header = first["company"]
        if first.get("location"):
            header += f", {first['location']}"
        period = combine_periods([r.get("period") for r in roles])
        period_display = format_period_for_display(period) if period else None
        if period_display:
            header += f"\t{period_display}"

        multi_role = len(roles) > 1
        role_entries = []
        for r in roles:
            role_header = r["title"]
            role_period_display = format_period_for_display(r.get("period")) if r.get("period") else None
            if multi_role and role_period_display and role_period_display != period_display:
                if role_period_style == "parens":
                    role_header += f" ({role_period_display})"
                else:
                    role_header += f"\t{role_period_display}"
            role_entries.append({"header": role_header, "bullets": [format_bullet_text(b) for b in r["bullets"]]})

        result.append({"header": header, "roles": role_entries})
    return result


def build_new_format_context(cv):
    return {
        "full_name": cv["full_name"],
        "years_experience": cv.get("years_experience"),
        "summary": cv["summary"],
        "education_items": build_education_entries(cv["education"]),
        "experience_companies": build_experience_companies(cv["experience"]),
        "certifications_items": cv.get("certifications", []),
        "skills_items": cv["skills"],
    }


def build_bd_format_context(cv):
    return {
        "full_name": cv["full_name"],
        "town": cv.get("town"),
        "summary": cv["summary"],
        "experience_companies": build_experience_companies(cv["experience"], role_period_style="parens"),
        "education_items": build_education_entries(cv["education"]),
        "certifications_items": cv.get("certifications", []),
    }


CONTEXT_BUILDERS = {
    "new_format": build_new_format_context,
    "non_template": build_new_format_context,
    "bd_format": build_bd_format_context,
}


CONTROL_TAG_STYLE = "CV Control Tag"


def strip_empty_paragraphs(document):
    for p in list(document.paragraphs):
        if p.style.name == CONTROL_TAG_STYLE:
            p._p.getparent().remove(p._p)
