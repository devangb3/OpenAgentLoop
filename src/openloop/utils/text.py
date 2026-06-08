from __future__ import annotations

import re
import textwrap

HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(?P<title>.+?)\s*$")


def normalize_lines(text: str) -> list[str]:
    return [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]


def clean_bullet(line: str) -> str:
    cleaned = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line.strip())
    return cleaned.strip()


def first_non_empty_line(text: str) -> str:
    for line in normalize_lines(text):
        stripped = line.strip()
        if stripped:
            return clean_bullet(stripped.lstrip("#").strip())
    return "Complete the requested engineering task."


def compact(text: str, limit: int = 1200) -> str:
    collapsed = re.sub(r"\n{3,}", "\n\n", text.strip())
    if len(collapsed) <= limit:
        return collapsed
    return f"{collapsed[: limit - 20].rstrip()}\n...[truncated]"


def sentence_summary(text: str, limit: int = 220) -> str:
    stripped = re.sub(r"\s+", " ", text.strip())
    if len(stripped) <= limit:
        return stripped
    boundary = stripped.rfind(".", 0, limit)
    if boundary >= 80:
        return stripped[: boundary + 1]
    return f"{stripped[: limit - 3].rstrip()}..."


def extract_label_value(text: str, labels: tuple[str, ...]) -> str | None:
    label_pattern = "|".join(re.escape(label) for label in labels)
    pattern = re.compile(rf"^\s*(?:{label_pattern})\s*:\s*(?P<value>.+?)\s*$", re.I | re.M)
    match = pattern.search(text)
    if match:
        return match.group("value").strip()
    return None


def extract_section_items(text: str, headings: tuple[str, ...]) -> list[str]:
    lines = normalize_lines(text)
    wanted = {heading.lower() for heading in headings}
    items: list[str] = []
    in_section = False

    for line in lines:
        heading_match = HEADING_RE.match(line)
        if heading_match:
            title = heading_match.group("title").strip().lower().rstrip(":")
            if in_section and title not in wanted:
                break
            in_section = title in wanted
            continue

        label = line.strip().rstrip(":").lower()
        if label in wanted:
            in_section = True
            continue

        if in_section:
            stripped = line.strip()
            if not stripped:
                continue
            if re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", line):
                items.append(clean_bullet(line))
            elif len(stripped) < 180:
                items.append(stripped)

    return dedupe(items)


def extract_matching_lines(text: str, patterns: tuple[str, ...]) -> list[str]:
    regexes = [re.compile(pattern, re.I) for pattern in patterns]
    matches = []
    for line in normalize_lines(text):
        stripped = clean_bullet(line)
        if stripped and any(regex.search(stripped) for regex in regexes):
            matches.append(stripped)
    return dedupe(matches)


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = re.sub(r"\s+", " ", item.strip()).lower()
        if item.strip() and normalized not in seen:
            seen.add(normalized)
            result.append(item.strip())
    return result


def markdown_list(items: list[str], fallback: str) -> str:
    values = items or [fallback]
    return "\n".join(f"- {item}" for item in values)


def fenced_block(text: str, language: str = "text") -> str:
    body = text.strip()
    if "```" in body:
        body = body.replace("```", "'''")
    return f"```{language}\n{body}\n```"


def indent_block(text: str, prefix: str = "> ") -> str:
    return textwrap.indent(text.strip(), prefix)
