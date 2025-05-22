import re
import hashlib

def email_to_tenant(email: str) -> str:
    """
    Converts an email into a sanitized Azure container name (tenant).
    Ensures compliance with Azure naming rules.
    """
    if '@' not in email:
        raise ValueError("Invalid email address")

    local_part, domain = email.lower().split('@', 1)

    # Basic alphanumeric slug, replace dots with hyphens, remove other non-alphanum
    slug = re.sub(r'[^a-z0-9-]', '-', f"{local_part}-{domain}")
    slug = re.sub(r'-+', '-', slug).strip('-')  # Remove repeated and leading/trailing hyphens

    # Ensure valid length (max 63), fallback to hash if too long
    if len(slug) > 63:
        hash_suffix = hashlib.sha1(email.encode()).hexdigest()[:8]
        slug = slug[:54] + "-" + hash_suffix  # 54 + 1 + 8 = 63

    # If too short (e.g., "a@b.co" → "a-b-co"), ensure min length
    if len(slug) < 3:
        slug += "-" + hashlib.sha1(email.encode()).hexdigest()[:3]

    return slug.lower()
