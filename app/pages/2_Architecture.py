"""Architecture page.

Surfaces the load-bearing design decisions and the v1 build-out priorities
from CLAUDE.md (which exists primarily for future Claude sessions but is
useful general developer/joiner documentation).
"""
from __future__ import annotations

import streamlit as st

from shared.markdown_loader import read_doc, split_into_sections


st.set_page_config(page_title="Architecture", layout="wide")

st.title("Architecture")
st.caption(
    "Load-bearing design decisions, scenario mapping, and v1 build-out priorities. "
    "Source: `CLAUDE.md` in the repo."
)

doc = read_doc("CLAUDE.md")
sections = split_into_sections(doc)

# Sections to surface, in order. Heading prefixes (case-insensitive).
PRESENTATION_ORDER = [
    "What this repo is",
    "Architecture",
    "Three load-bearing design decisions",
    "v1 build-out priorities",
    "Working in this repo",
    "Scenarios",
    "What lives where for assumptions",
    "Commands",
]

for prefix in PRESENTATION_ORDER:
    target = prefix.strip().lower()
    matched = next(
        (sec for heading, sec in sections.items() if heading.lower().startswith(target)),
        None,
    )
    if matched is None:
        continue
    st.markdown(matched.body)
    st.divider()
