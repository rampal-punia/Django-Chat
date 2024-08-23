import hashlib


def generate_pdf_hash(pdf_content):
    """
    Generate a SHA-256 hash for the given PDF content.
    """
    return hashlib.sha256(pdf_content).hexdigest()
