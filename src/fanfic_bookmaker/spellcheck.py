from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
import re
from typing import Iterable

try:
    from spellchecker import SpellChecker
except ImportError:  # pragma: no cover - optional dependency fallback
    SpellChecker = None

SPELLCHECK_AVAILABLE = SpellChecker is not None


WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")
CODE_FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`]+`")
HTML_TAG_RE = re.compile(r"<[^>]+>")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
COMMENT_RE = re.compile(r"<!--.*?-->")

BRITISH_OVERRIDES = {
    "color": "colour",
    "colors": "colours",
    "colored": "coloured",
    "coloring": "colouring",
    "organize": "organise",
    "organized": "organised",
    "organizing": "organising",
    "organizes": "organises",
    "honor": "honour",
    "honored": "honoured",
    "honoring": "honouring",
    "favorite": "favourite",
    "favorites": "favourites",
    "favor": "favour",
    "favored": "favoured",
    "favoring": "favouring",
    "center": "centre",
    "centers": "centres",
    "centered": "centred",
    "centering": "centring",
    "meter": "metre",
    "meters": "metres",
    "theater": "theatre",
    "theaters": "theatres",
    "analyze": "analyse",
    "analyzed": "analysed",
    "analyzing": "analysing",
    "realize": "realise",
    "realized": "realised",
    "realizing": "realising",
    "traveler": "traveller",
    "travelers": "travellers",
    "traveling": "travelling",
    "canceled": "cancelled",
    "canceling": "cancelling",
    "labeling": "labelling",
    "modeling": "modelling",
    "dialog": "dialogue",
}

COMMON_IGNORE = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "had",
    "has",
    "have",
    "he",
    "her",
    "him",
    "his",
    "i",
    "in",
    "is",
    "it",
    "its",
    "me",
    "my",
    "of",
    "on",
    "or",
    "our",
    "she",
    "that",
    "the",
    "their",
    "them",
    "there",
    "they",
    "this",
    "to",
    "was",
    "we",
    "were",
    "with",
    "you",
    "your",
}


@dataclass(slots=True)
class SpellcheckConfig:
    enabled: bool = True
    ignore_words: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SpellcheckFinding:
    chapter: str
    scene: str
    line: int
    written: str
    suggestion: str
    context: str


@dataclass(slots=True)
class SpellcheckReport:
    enabled: bool
    available: bool
    findings: list[SpellcheckFinding] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_json_text(self) -> str:
        return json.dumps(
            {
                "enabled": self.enabled,
                "available": self.available,
                "notes": self.notes,
                "findings": [asdict(item) for item in self.findings],
            },
            indent=2,
            ensure_ascii=False,
        ) + "\n"

    def to_markdown(self) -> str:
        lines = ["# Spellcheck Report", ""]
        if self.notes:
            lines.append("## Notes")
            lines.extend(f"- {note}" for note in self.notes)
            lines.append("")
        if not self.enabled:
            lines.append("Spellcheck was disabled in the project config.")
            return "\n".join(lines).rstrip() + "\n"
        if not self.available:
            lines.append("Spellcheck is unavailable because the checker dependency was not installed.")
            return "\n".join(lines).rstrip() + "\n"
        if not self.findings:
            lines.append("No spelling issues were found.")
            return "\n".join(lines).rstrip() + "\n"

        lines.extend(
            [
                "| Chapter | Scene | Line | Written | Should be | Context |",
                "| --- | --- | ---: | --- | --- | --- |",
            ]
        )
        for finding in self.findings:
            lines.append(
                "| "
                + " | ".join(
                    [
                        escape_pipe(finding.chapter),
                        escape_pipe(finding.scene),
                        str(finding.line),
                        escape_pipe(finding.written),
                        escape_pipe(finding.suggestion),
                        escape_pipe(finding.context),
                    ]
                )
                + " |"
            )
        return "\n".join(lines).rstrip() + "\n"


def run_spellcheck(
    *,
    chapter_name: str,
    scene_name: str,
    text: str,
    ignore_words: Iterable[str] = (),
) -> list[SpellcheckFinding]:
    if SpellChecker is None:
        return []

    checker = SpellChecker(language="en")
    ignore = {word.lower() for word in COMMON_IGNORE}
    ignore.update(word.lower() for word in ignore_words)
    checker.word_frequency.load_words(ignore)

    findings: list[SpellcheckFinding] = []
    in_fence = False
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if CODE_FENCE_RE.match(stripped):
            in_fence = not in_fence
            continue
        if in_fence or not stripped:
            continue

        cleaned = COMMENT_RE.sub(" ", raw_line)
        cleaned = INLINE_CODE_RE.sub(" ", cleaned)
        cleaned = MARKDOWN_LINK_RE.sub(r"\1", cleaned)
        cleaned = HTML_TAG_RE.sub(" ", cleaned)
        cleaned = cleaned.replace("—", " ").replace("–", " ")

        for word in WORD_RE.findall(cleaned):
            if is_ignored(word):
                continue
            lowered = word.lower()
            if lowered in ignore:
                continue
            if lowered in BRITISH_OVERRIDES:
                suggestion = BRITISH_OVERRIDES[lowered]
                if lowered != suggestion:
                    findings.append(
                        build_finding(
                            chapter_name,
                            scene_name,
                            line_number,
                            raw_line,
                            word,
                            suggestion,
                        )
                    )
                continue
            if word[0].isupper() and not word.isupper():
                continue
            if lowered in checker:
                continue

            correction = checker.correction(lowered)
            if correction and correction != lowered:
                suggestion = preserve_case(word, correction)
                findings.append(
                    build_finding(
                        chapter_name,
                        scene_name,
                        line_number,
                        raw_line,
                        word,
                        suggestion,
                    )
                )

    return findings


def build_finding(
    chapter_name: str,
    scene_name: str,
    line_number: int,
    raw_line: str,
    written: str,
    suggestion: str,
) -> SpellcheckFinding:
    context = context_snippet(raw_line, written)
    return SpellcheckFinding(
        chapter=chapter_name,
        scene=scene_name,
        line=line_number,
        written=written,
        suggestion=suggestion,
        context=context,
    )


def context_snippet(line: str, needle: str, limit: int = 120) -> str:
    compact = " ".join(line.strip().split())
    if len(compact) <= limit:
        return compact
    index = compact.lower().find(needle.lower())
    if index < 0:
        return compact[: limit - 1] + "..."
    start = max(0, index - 40)
    end = min(len(compact), index + len(needle) + 40)
    snippet = compact[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(compact):
        snippet = snippet + "..."
    return snippet


def is_ignored(word: str) -> bool:
    return len(word) <= 2 or "'" in word or "-" in word and word.count("-") > 1


def preserve_case(original: str, suggestion: str) -> str:
    if original.isupper():
        return suggestion.upper()
    if original[:1].isupper():
        return suggestion[:1].upper() + suggestion[1:]
    return suggestion


def escape_pipe(text: str) -> str:
    return text.replace("|", "\\|")
