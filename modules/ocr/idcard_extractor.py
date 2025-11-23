# modules/ocr/idcard_extractor.py
import re
from rapidfuzz import fuzz

def extract_fields(text):
    """
    Extracts common ID fields: Name, DOB, ID number, Gender.
    Uses regex + fuzzy search.
    """

    fields = {
        "name": None,
        "dob": None,
        "id_number": None,
        "gender": None
    }

    # DOB
    dob_patterns = [
        r"\b\d{2}[\/\-]\d{2}[\/\-]\d{4}\b",
        r"\b\d{4}[\/\-]\d{2}[\/\-]\d{2}\b"
    ]
    for p in dob_patterns:
        match = re.search(p, text)
        if match:
            fields["dob"] = match.group(0)
            break

    # Gender
    if "male" in text.lower():
        fields["gender"] = "Male"
    elif "female" in text.lower():
        fields["gender"] = "Female"

    # ID Number (12–16 digits)
    id_match = re.search(r"\b[A-Z0-9]{10,18}\b", text)
    if id_match:
        fields["id_number"] = id_match.group(0)

    # Name extraction using fuzzy logic
    lines = text.split("\n")
    for line in lines:
        if fuzz.partial_ratio("name", line.lower()) > 70:
            fields["name"] = line.replace("Name", "").replace(":", "").strip()

    return fields
