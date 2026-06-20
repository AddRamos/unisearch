import re


TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


def tokenize(text: str) -> list[str]:
    if not text:
        return []

    return [
        token.lower()
        for token in TOKEN_RE.findall(text)
    ]