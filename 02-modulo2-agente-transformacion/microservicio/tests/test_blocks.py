from blocks import (
    build_bd_format_context,
    build_education_entries,
    build_experience_companies,
    build_new_format_context,
    format_bullet_text,
    format_period_for_display,
)


def job(company, title, period, bullets, location=None):
    return {
        "company": company,
        "title": title,
        "location": location,
        "period": period,
        "bullets": bullets,
    }


def test_single_role_company_has_one_role_no_period_in_role_header():
    experience = [job("Abbott", "Senior Capstone Project", "Aug. 2025 – Dec. 2025", ["Did X."])]
    companies = build_experience_companies(experience)
    assert len(companies) == 1
    company = companies[0]
    assert company["header"] == "Abbott\tAug. 2025 – Dec. 2025"
    assert len(company["roles"]) == 1
    assert company["roles"][0]["header"] == "Senior Capstone Project"
    assert company["roles"][0]["bullets"] == ["Did X."]


def test_company_header_includes_location_when_present():
    experience = [
        job("Haleon", "Machinery Safety EHS Co-op", "Jun. 2026 – Present", ["Did Y."], location="Guayama, PR")
    ]
    companies = build_experience_companies(experience)
    assert companies[0]["header"] == "Haleon, Guayama, PR\tJun. 2026 – Present"


def test_fresenius_kabi_two_roles_grouped_under_one_company_header():
    """Caso real de Edgeliz Ramos Rosario (canon BD): dos roles consecutivos en la
    misma empresa se agrupan en un solo bloque, con el periodo total en el header de
    empresa y el periodo propio de cada rol entre parentesis en su propio header."""
    experience = [
        job(
            "Fresenius Kabi",
            "Engineer I",
            "Oct. 2023 – Present",
            ["Led execution."],
            location="San Germán, PR",
        ),
        job(
            "Fresenius Kabi",
            "Jr. Technical Consultant",
            "Feb. 2023 – Oct. 2023",
            ["Developed docs."],
            location="San Germán, PR",
        ),
    ]
    companies = build_experience_companies(experience)
    assert len(companies) == 1
    company = companies[0]
    assert company["header"] == "Fresenius Kabi, San Germán, PR\tFeb. 2023 – Present"
    assert len(company["roles"]) == 2
    assert company["roles"][0]["header"] == "Engineer I\tOct. 2023 – Present"
    assert company["roles"][0]["bullets"] == ["Led execution."]
    assert company["roles"][1]["header"] == "Jr. Technical Consultant\tFeb. 2023 – Oct. 2023"


def test_non_consecutive_same_company_not_grouped():
    """Si el candidato volvio a la misma empresa despues de trabajar en otro lado, no
    se agrupa -- son dos bloques de experiencia separados, no un mismo periodo."""
    experience = [
        job("Acme", "Role A", "Jan 2024 – Present", ["a"]),
        job("Other Co", "Role B", "Jan 2023 – Dec 2023", ["b"]),
        job("Acme", "Role C", "Jan 2020 – Dec 2022", ["c"]),
    ]
    companies = build_experience_companies(experience)
    assert len(companies) == 3
    assert companies[0]["header"] == "Acme\tJan. 2024 – Present"
    assert companies[2]["header"] == "Acme\tJan. 2020 – Dec. 2022"


def test_missing_period_omits_period_from_header():
    """CV sin fechas para un proyecto (ej. Edward Cruz Vega, canon BD) -- el header de
    empresa no debe imprimir un tab colgante ni la palabra None."""
    experience = [job("Amphenol Advanced Sensors", "Ergonomic Evaluation Project", None, ["Evaluated tables."])]
    companies = build_experience_companies(experience)
    assert companies[0]["header"] == "Amphenol Advanced Sensors"
    assert companies[0]["roles"][0]["header"] == "Ergonomic Evaluation Project"


def test_multi_role_company_with_missing_periods_role_header_has_no_parens():
    experience = [
        job("Acme", "Role A", None, ["a"]),
        job("Acme", "Role B", "Jan 2020 - Dec 2021", ["b"]),
    ]
    companies = build_experience_companies(experience)
    assert companies[0]["header"] == "Acme\tJan. 2020 – Dec. 2021"
    assert companies[0]["roles"][0]["header"] == "Role A"
    assert companies[0]["roles"][1]["header"] == "Role B\tJan. 2020 – Dec. 2021"


def test_new_format_context_uses_experience_companies():
    cv = {
        "full_name": "Jane Doe",
        "years_experience": "5",
        "summary": "Summary.",
        "education": [],
        "experience": [job("Acme", "Role A", "Jan 2020 - Dec 2021", ["a"])],
        "certifications": [],
        "skills": ["Skill A"],
    }
    context = build_new_format_context(cv)
    assert "experience_companies" in context
    assert "experience_jobs" not in context
    assert context["experience_companies"][0]["roles"][0]["header"] == "Role A"


def test_bd_format_context_drops_skills_from_summary():
    cv = {
        "full_name": "Jane Doe",
        "town": "Mayagüez, PR",
        "summary": "Summary.",
        "skills": ["Skill A"],
        "experience": [job("Acme", "Role A", "Jan 2020 - Dec 2021", ["a"])],
        "education": [],
        "certifications": [],
    }
    context = build_bd_format_context(cv)
    assert "skills_items" not in context
    assert context["town"] == "Mayagüez, PR"
    assert context["experience_companies"][0]["header"] == "Acme\tJan. 2020 – Dec. 2021"


def test_format_period_adds_dot_after_month_abbreviations():
    # canon de Paola (Yanina): "Jan. 2021 – Dec. 2025", nunca "May." (ya es palabra completa)
    assert format_period_for_display("Jan 2021 - Dec 2025") == "Jan. 2021 – Dec. 2025"
    assert format_period_for_display("May 2026 – Jul. 2026") == "May 2026 – Jul. 2026"
    assert format_period_for_display("Sept 2023 - Present") == "Sept. 2023 – Present"
    assert format_period_for_display(None) is None


def test_multi_role_header_uses_dotted_period():
    experience = [
        {"company": "UPR", "title": "Role A", "location": None, "period": "Jan 2021 - Dec 2022", "bullets": ["a"]},
        {"company": "UPR", "title": "Role B", "location": None, "period": "Jan 2023 - Dec 2024", "bullets": ["b"]},
    ]
    companies = build_experience_companies(experience)
    assert "Jan. 2021 – Dec. 2024" in companies[0]["header"]
    assert companies[0]["roles"][0]["header"] == "Role A\tJan. 2021 – Dec. 2022"


def test_format_bullet_text_uses_en_dash_in_percent_range():
    assert format_bullet_text("Achieved a 15-20% reduction.") == "Achieved a 15–20% reduction."
    assert format_bullet_text("No range here.") == "No range here."


def test_education_entry_fixes_gpa_comma_before_thesis():
    education = [{
        "degree": 'Master of Science (M.S.) in X, GPA: 3.75, Thesis: "Y"',
        "institution": "UPR", "period": None,
    }]
    entries = build_education_entries(education)
    assert entries[0]["degree"] == 'Master of Science (M.S.) in X, GPA: 3.75. Thesis: "Y"'


def test_education_entry_fixes_missing_dot_in_abbreviation():
    # candidato real (Steven Palmer-Velazquez): el agente devolvio "(B.S)" sin el
    # punto final -- el patron es seguro de corregir (abreviatura de 2 letras).
    education = [{"degree": "Bachelor of Science (B.S) in Chemistry", "institution": "UPR", "period": None}]
    entries = build_education_entries(education)
    assert entries[0]["degree"] == "Bachelor of Science (B.S.) in Chemistry"


def test_education_entries_split_degree_institution_no_period():
    # canon de Paola (Yanina, Andrea): educacion muestra grado en negrita y la
    # institucion debajo, sin fechas -- nunca un string combinado con periodo.
    education = [{"degree": "B.S. in Chemistry", "institution": "UPR Mayaguez", "period": "2019 - 2023"}]
    entries = build_education_entries(education)
    assert entries == [{"degree": "B.S. in Chemistry", "institution": "UPR Mayaguez"}]


def test_new_format_context_uses_education_entries_not_strings():
    cv = {
        "full_name": "Jane Doe",
        "years_experience": "3",
        "summary": "Summary.",
        "skills": [],
        "certifications": [],
        "experience": [],
        "education": [{"degree": "B.S. in Chemistry", "institution": "UPR Mayaguez", "period": "2019 - 2023"}],
    }
    context = build_new_format_context(cv)
    assert context["education_items"] == [{"degree": "B.S. in Chemistry", "institution": "UPR Mayaguez"}]
