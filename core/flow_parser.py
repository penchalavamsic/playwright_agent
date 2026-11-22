"""Small explicit flow grammar. Unknown instructions are retained, never guessed away."""
import re


VERBS = r"click|tap|open|press|select|choose|check|uncheck|fill|type|enter|search|verify|assert|ensure|login|log\s+in|navigate|go\s+to|visit|wait"


def parse_flow(text, target_url="", profile=""):
    steps = []

    def add(action, target="", value="", codes=None):
        steps.append(dict(step_order=len(steps) + 1, action_type=action,
                          target_keyword=target, input_value=value,
                          expected_status_codes=codes or []))

    if target_url:
        add("NAVIGATE", target_url, target_url)
    # Protect punctuation and conjunctions inside quoted labels and values.
    quoted = []

    def protect(match):
        quoted.append(match.group(1) if match.group(1) is not None else match.group(2))
        return f"__Q{len(quoted)-1}__"

    protected = re.sub(r'"([^"\n]*)"|\x27([^\x27\n]*)\x27', protect, text.replace('“', '"').replace('”', '"'))
    protected = re.sub(r'(?m)^\s*\d+[.)]\s+', '', protected)

    def restore(value):
        value = value.strip().rstrip('.')
        return re.sub(r"__Q(\d+)__", lambda m: quoted[int(m[1])], value).strip()

    clauses = re.split(rf"\n+|;|\.(?=\s)|,\s*(?=(?:{VERBS})\b)|\s+(?:and\s+then|then|and)\s+(?=(?:{VERBS})\b)", protected, flags=re.I)
    selected = profile and profile not in ("PUBLIC", "NONE", "None (Public URL)")
    if selected and not re.search(r"\b(?:login|log\s+in)\b", protected, re.I):
        add("LOGIN", profile)
    for raw in clauses:
        clause = re.sub(r"^\s*(?:\d+[.)]\s*|[-*]\s+)", "", raw).strip()
        clause = re.sub(r"^as\s+.+?\s+(?=" + VERBS + r"\b)", "", clause, flags=re.I)
        if not clause:
            continue
        if re.fullmatch(r'as\s+' + re.escape(profile).replace('_', r'[\s_-]+'), clause, re.I):
            continue
        match = re.match(r"^(?:login|log\s+in)(?:\s+as\s+(.+))?$", clause, re.I)
        if match:
            role = re.sub(r'[\s.-]+', '_', restore(match[1] or profile)).upper()
            add("LOGIN", role)
            continue
        match = re.match(r"^(?:verify|assert|ensure)\s+(.+)$", clause, re.I)
        if match:
            body = match[1]
            codes = [int(c) for c in re.findall(r"\b[1-5]\d{2}\b", body)]
            if re.search(r"\b(?:api|status\s+code|http|endpoint|response)\b", body, re.I):
                endpoint = re.search(r"__Q\d+__|/[^\s]+", body)
                add("VERIFY_API", restore(endpoint[0]) if endpoint else "", codes=codes or [200, 201, 204])
            else:
                body = re.sub(r"^(?:that\s+)?", "", body, flags=re.I)
                body = re.sub(r"\s+(?:is\s+)?(?:visible|displayed|present|shown)$", "", body, flags=re.I)
                add("VERIFY_UI", restore(body))
            continue
        match = re.match(r"^(?:fill)\s+(.+?)\s+with\s+(.+)$", clause, re.I)
        if match:
            add("FILL", restore(match[1]), restore(match[2]))
            continue
        match = re.match(r"^(?:type|enter)\s+(.+?)\s+(?:into|in)\s+(.+)$", clause, re.I)
        if match:
            add("FILL", restore(match[2]), restore(match[1]))
            continue
        match = re.match(r"^search\s+(?:for\s+)?(.+)$", clause, re.I)
        if match:
            add("SEARCH", "search", restore(match[1]))
            continue
        match = re.match(r"^(?:select|choose)\s+(.+?)\s+(?:from|in)\s+(.+)$", clause, re.I)
        if match:
            add("SELECT", restore(match[2]), restore(match[1]))
            continue
        match = re.match(r"^(click|tap|open|check|uncheck|press)\s+(?:on\s+)?(.+)$", clause, re.I)
        if match:
            action = {"check": "CHECK", "uncheck": "UNCHECK", "press": "PRESS"}.get(match[1].lower(), "CLICK")
            target = re.sub(r"^(?:the\s+)", "", match[2], flags=re.I)
            target = re.sub(r'^(?:button|link|tab)\s+(?=__Q)', '', target, flags=re.I)
            target = re.sub(r'(?<=__)\s+(?:button|link|tab)$', '', target, flags=re.I)
            add(action, restore(target))
            continue
        match = re.match(r"^(?:navigate\s+to|go\s+to|visit)\s+(.+)$", clause, re.I)
        if match:
            add("NAVIGATE", restore(match[1]), restore(match[1]))
            continue
        add("UNSUPPORTED", restore(clause))
    if not text.strip():
        add("UNSUPPORTED", "No flow specified. Enter explicit actions and assertions.")
    return steps
