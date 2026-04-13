import hashlib
import re

from user_agents import parse


def parse_user_agent(ua_string):
    ua = parse(ua_string)
    return {
        "browser": f"{ua.browser.family} {ua.browser.version_string}".strip(),
        "operating_system": f"{ua.os.family} {ua.os.version_string}".strip(),
        "device_type": "mobile" if ua.is_mobile else ("tablet" if ua.is_tablet else "desktop"),
        "is_bot": ua.is_bot,
    }


def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain lowercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain a digit"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain a special character"
    return True, "Strong password"


def generate_device_fingerprint(data):
    fingerprint_data = f"{data.get('user_agent', '')}-{data.get('screen_resolution', '')}-{data.get('timezone', '')}"
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
