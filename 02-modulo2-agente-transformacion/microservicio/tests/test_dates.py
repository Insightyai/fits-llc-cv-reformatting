from datetime import date

from dates import calculate_years_experience

NOW = date(2026, 7, 30)


def job(period):
    return {"period": period}


def test_shirley_mercado_real_case():
    experience = [
        job("May 2024 - Present"),
        job("April 2022 - May 2024"),
    ]
    value, warnings = calculate_years_experience(experience, NOW)
    assert value == "4"
    assert warnings == []


def test_single_job_no_present():
    value, warnings = calculate_years_experience([job("Jan 2019 - Dec 2021")], NOW)
    assert value == "3"  # Jan 2019 a Dec 2021 inclusive = 36 meses exactos
    assert warnings == []


def test_overlapping_jobs_do_not_double_count():
    experience = [
        job("Jan 2019 - Dec 2022"),
        job("Jun 2020 - Dec 2021"),  # totalmente contenido en el anterior
    ]
    value, warnings = calculate_years_experience(experience, NOW)
    assert value == "4"  # Jan 2019 a Dec 2022 inclusive = 48 meses exactos, el segundo job no suma


def test_en_dash_and_present_variants():
    value, _ = calculate_years_experience([job("April 2022 – Present")], NOW)
    assert value == "4"
    value, _ = calculate_years_experience([job("April 2022 - Actualidad")], NOW)
    assert value == "4"


def test_spanish_months():
    value, warnings = calculate_years_experience([job("Enero 2020 – actualidad")], NOW)
    assert value == "6"
    assert warnings == []


def test_year_only_is_ambiguous_but_computable():
    value, warnings = calculate_years_experience([job("2019-2021")], NOW)
    assert value == "2"
    assert any(w.startswith("AMBIGUOUS_DATES") for w in warnings)


def test_empty_period_is_unknown():
    value, warnings = calculate_years_experience([job("")], NOW)
    assert value is None
    assert warnings[0].startswith("YEARS_EXPERIENCE_UNKNOWN")


def test_garbage_period_is_unknown():
    value, warnings = calculate_years_experience([job("sometime a while ago")], NOW)
    assert value is None
    assert warnings[0].startswith("YEARS_EXPERIENCE_UNKNOWN")


def test_no_jobs_is_unknown():
    value, warnings = calculate_years_experience([], NOW)
    assert value is None
    assert warnings[0].startswith("YEARS_EXPERIENCE_UNKNOWN")


def test_less_than_a_year_is_unknown():
    value, warnings = calculate_years_experience([job("Jan 2026 - May 2026")], NOW)
    assert value is None
    assert warnings[0].startswith("YEARS_EXPERIENCE_UNKNOWN")


def test_end_before_start_is_unknown():
    value, warnings = calculate_years_experience([job("Jan 2022 - Jan 2020")], NOW)
    assert value is None
    assert warnings[0].startswith("YEARS_EXPERIENCE_UNKNOWN")
