"""Reads repo markdown docs and parses them into ``## ``-level sections.

The Streamlit app stays a thin viewer: every page reads the underlying
docs at runtime so the repo's `docs/*.md`, `README.md`, and `CLAUDE.md`
remain the single source of truth. Editing those files updates the app
on next reload.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


# The app lives at <repo>/app/; docs and top-level READMEs are one level up.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = REPO_ROOT / "docs"


@dataclass(frozen=True)
class Section:
    heading: str         # The `## ` heading text (without the leading hashes)
    body: str            # Section body INCLUDING the heading line, for rendering
    level: int           # Heading level (always 2 for top-level sections)


def read_doc(relative_path: str) -> str:
    """Return the full text of a markdown file relative to the repo root."""
    path = REPO_ROOT / relative_path
    if not path.exists():
        return f"_(missing file: {relative_path})_"
    return path.read_text(encoding="utf-8")


def split_into_sections(markdown: str) -> dict[str, Section]:
    """Split a markdown document into ``## ``-level sections.

    Returns a dict keyed by heading text. The preamble before the first
    ``## `` is stored under the key ``"_preamble"``. Each Section's body
    includes its heading line so callers can render the section as-is.
    """
    lines = markdown.splitlines(keepends=True)
    sections: dict[str, Section] = {}

    current_heading: str | None = None
    current_buf: list[str] = []
    preamble_buf: list[str] = []
    in_preamble = True

    h2_pattern = re.compile(r"^##\s+(.+?)\s*$")

    for line in lines:
        match = h2_pattern.match(line)
        if match:
            # Flush the previous buffer.
            if in_preamble:
                if preamble_buf:
                    sections["_preamble"] = Section(
                        heading="_preamble", body="".join(preamble_buf), level=0,
                    )
                in_preamble = False
            elif current_heading is not None:
                sections[current_heading] = Section(
                    heading=current_heading,
                    body="".join(current_buf),
                    level=2,
                )
            current_heading = match.group(1).strip()
            current_buf = [line]
        else:
            if in_preamble:
                preamble_buf.append(line)
            else:
                current_buf.append(line)

    # Flush the final section (or preamble if no headings exist).
    if in_preamble and preamble_buf:
        sections["_preamble"] = Section(
            heading="_preamble", body="".join(preamble_buf), level=0,
        )
    elif current_heading is not None:
        sections[current_heading] = Section(
            heading=current_heading, body="".join(current_buf), level=2,
        )

    return sections


def section(markdown: str, heading_prefix: str) -> str:
    """Return the section whose heading starts with ``heading_prefix``, or empty.

    Matches case-insensitively on the start of the heading text so callers can
    reference e.g. ``"Why this exists"`` without worrying about numbering or
    trailing whitespace.
    """
    sections = split_into_sections(markdown)
    target = heading_prefix.strip().lower()
    for heading, sec in sections.items():
        if heading.lower().startswith(target):
            return sec.body
    return ""
