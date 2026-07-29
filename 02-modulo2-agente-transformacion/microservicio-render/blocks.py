def format_education_item(e):
    item = f"{e['degree']}, {e['institution']}"
    if e.get("period"):
        item += f" ({e['period']})"
    return item


def build_education_items(education):
    return [format_education_item(e) for e in education]


def build_experience_jobs(experience):
    jobs = []
    for x in experience:
        header = f"{x['title']} — {x['company']}"
        if x.get("location"):
            header += f", {x['location']}"
        header += f" ({x['period']})"
        jobs.append({"header": header, "bullets": list(x["bullets"])})
    return jobs


def build_new_format_context(cv):
    return {
        "full_name": cv["full_name"],
        "years_experience": cv.get("years_experience"),
        "summary": cv["summary"],
        "education_items": build_education_items(cv["education"]),
        "experience_jobs": build_experience_jobs(cv["experience"]),
        "certifications_items": cv.get("certifications", []),
        "skills_items": cv["skills"],
    }


def build_bd_format_context(cv):
    return {
        "full_name": cv["full_name"],
        "town": cv.get("town"),
        "summary": cv["summary"],
        "skills_items": cv["skills"],
        "experience_jobs": build_experience_jobs(cv["experience"]),
        "education_certifications_items": build_education_items(cv["education"])
        + list(cv.get("certifications", [])),
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
