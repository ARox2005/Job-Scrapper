from services.llm import call_llm_json

def extract_job_metadata(job) -> dict:
    """
    Route to the correct company-specific extractor.
    Returns: {location, education_levels, min_experience, max_experience}
    """
    extractor = EXTRACTORS.get(job.company)
    if not extractor:
        return {}
    return extractor(job)


def _extract_microsoft_metadata(job) -> dict:
    """Microsoft-specific extraction."""
    # Location — directly from raw_data (no LLM needed)
    locations = job.raw_data.get("locations", []) if job.raw_data else []
    location = locations[0] if locations else None

    # Education & Experience — from JD text via LLM
    jd_text = job.qualifications or job.description or ""
    if not jd_text:
        return {
            "location": location,
            "education_levels": [],
            "min_experience": None,
            "max_experience": None,
        }

    prompt = f"""Analyze this job description and extract the following:

1. education_levels: A JSON array of ALL accepted education levels for this role.
   Use ONLY these values: "high_school", "ug", "pg", "phd"

   Rules:
   - If the JD says "Bachelor's or Master's" → ["ug", "pg"]
   - If the JD says "Master's required" → ["pg"] (ONLY pg, not ug)
   - If the JD says "PhD preferred, Master's acceptable" → ["pg", "phd"]
   - If the JD says "Bachelor's degree required" → ["ug", "pg", "phd"] (higher also qualifies)
   - If nothing is mentioned → []

2. min_experience: Minimum years of experience required (integer). 0 if entry-level or not mentioned.
3. max_experience: Maximum years mentioned (integer or null if not mentioned).

Return ONLY valid JSON:
{{"education_levels": [...], "min_experience": X, "max_experience": X}}

Job Description:
{jd_text[:3000]}"""

    try:
        result = call_llm_json(prompt)
    except Exception as e:
        print(f"LLM extraction failed for job {job.id}: {e}")
        result = {}

    return {
        "location": location,
        "education_levels": result.get("education_levels", []),
        "min_experience": result.get("min_experience"),
        "max_experience": result.get("max_experience"),
    }


# Registry — add new companies here
EXTRACTORS = {
    "Microsoft": _extract_microsoft_metadata,
}
