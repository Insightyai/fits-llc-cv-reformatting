from docxtpl import RichText


def _append_break(rt, is_first):
    if not is_first:
        rt.xml += "<w:r><w:br/></w:r>"


def build_experience_block(experience):
    rt = RichText()
    for i, x in enumerate(experience):
        _append_break(rt, i == 0)
        header = f"{x['title']} — {x['company']}"
        if x.get("location"):
            header += f", {x['location']}"
        header += f" ({x['period']})"
        rt.add(header, bold=True)
        for b in x["bullets"]:
            rt.xml += "<w:r><w:br/></w:r>"
            rt.add("• " + b)
    return rt


def build_education_block(education):
    rt = RichText()
    for i, e in enumerate(education):
        _append_break(rt, i == 0)
        item = f"{e['degree']}, {e['institution']}"
        if e.get("period"):
            item += f" ({e['period']})"
        rt.add("• " + item)
    return rt


def build_certifications_block(certifications):
    rt = RichText()
    for i, c in enumerate(certifications):
        _append_break(rt, i == 0)
        rt.add("• " + c)
    return rt


def build_skills_block(skills):
    rt = RichText()
    for i, s in enumerate(skills):
        _append_break(rt, i == 0)
        rt.add("• " + s)
    return rt


def build_education_certifications_block(education, certifications):
    rt = RichText()
    first = True
    for e in education:
        _append_break(rt, first)
        first = False
        item = f"{e['degree']}, {e['institution']}"
        if e.get("period"):
            item += f" ({e['period']})"
        rt.add("• " + item)
    for c in certifications:
        _append_break(rt, first)
        first = False
        rt.add("• " + c)
    return rt


def build_summary_skills_block(summary, town, skills):
    rt = RichText()
    rt.add(summary)
    if town:
        rt.xml += "<w:r><w:br/></w:r>"
        rt.add(f"Resides in {town}.")
    for s in skills:
        rt.xml += "<w:r><w:br/></w:r>"
        rt.add("• " + s)
    return rt


def build_new_format_context(cv):
    return {
        "full_name": cv["full_name"],
        "years_experience": cv.get("years_experience"),
        "summary": cv["summary"],
        "education_block": build_education_block(cv["education"]),
        "experience_block": build_experience_block(cv["experience"]),
        "certifications_block": build_certifications_block(cv.get("certifications", [])),
        "skills_block": build_skills_block(cv["skills"]),
    }


def build_bd_format_context(cv):
    return {
        "full_name": cv["full_name"],
        "town": cv.get("town"),
        "summary_skills_block": build_summary_skills_block(
            cv["summary"], cv.get("town"), cv["skills"]
        ),
        "experience_block": build_experience_block(cv["experience"]),
        "education_certifications_block": build_education_certifications_block(
            cv["education"], cv.get("certifications", [])
        ),
    }


CONTEXT_BUILDERS = {
    "new_format": build_new_format_context,
    "non_template": build_new_format_context,
    "bd_format": build_bd_format_context,
}
