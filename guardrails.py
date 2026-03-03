FORBIDDEN_KEYWORDS = [
    "bypass",
    "avoid aml",
    "fake kyc",
    "launder money",
    "hack payment",
    "fraud method",
    "skip verification",
    "how to cheat",
    "exploit",
    "circumvent compliance",
]

def is_forbidden(query: str) -> bool:
    query_lower = query.lower()
    return any(word in query_lower for word in FORBIDDEN_KEYWORDS)