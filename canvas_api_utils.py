def build_course_api_url(canvas_domain_url, course_id, resource_path):
    """Build a Canvas course-scoped API URL from a domain or base path."""
    base = canvas_domain_url.rstrip('/')
    if not base.startswith('http'):
        base = f"https://{base}"

    if '/api/v1/courses' not in base:
        base = f"{base}/api/v1/courses"

    return f"{base}/{course_id}/{resource_path.lstrip('/')}"
