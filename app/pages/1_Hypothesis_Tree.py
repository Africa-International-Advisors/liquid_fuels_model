"""Hypothesis Tree page.

Renders the per-segment driver decomposition from
``docs/demand_hypothesis_tree.md`` with expandable sections so readers
can browse by segment rather than scrolling a 300-line file.
"""
from __future__ import annotations

import streamlit as st

from shared.markdown_loader import read_doc, split_into_sections


st.set_page_config(page_title="Hypothesis Tree", layout="wide")

st.title("Demand hypothesis tree")
st.caption(
    "McKinsey-style decomposition: each demand segment's drivers, sub-drivers, "
    "down to quantifiable leaves. Status tags: `[Q]` quantified · "
    "`[P]` provisional · `[N]` not modelled."
)

doc = read_doc("docs/demand_hypothesis_tree.md")
sections = split_into_sections(doc)

# --------------------------------------------------------------------------- #
# Preamble (status legend + summary table) at the top.

preamble = sections.get("_preamble")
if preamble:
    st.markdown(preamble.body)

status_tags = sections.get("Status tags")
if status_tags:
    body = "\n".join(status_tags.body.splitlines()[1:])
    with st.expander("Status tags — what [Q], [P], [N] mean", expanded=False):
        st.markdown(body)

summary = sections.get("At-a-glance summary")
if summary:
    body = "\n".join(summary.body.splitlines()[1:])
    st.header("At a glance")
    st.markdown(body)

st.divider()

# --------------------------------------------------------------------------- #
# Per-segment expanders.
#
# The doc's segment sections start with a leading number ("1. Vehicles", etc.).
# We match prefixes to pick out which sections belong in the segment browser.

SEGMENT_PREFIXES = [
    ("0. Total", False),
    ("1. Vehicles", True),
    ("2. Aviation", True),
    ("3. Generation", True),
    ("4. Industrial", True),
    ("5. Marine", True),
    ("6. Agriculture", True),
    ("7. Supply", True),
    ("8. Balance", True),
    ("9. Pricing", False),
]

st.header("Browse by segment")

for prefix, default_open in SEGMENT_PREFIXES:
    matched = next(
        (sec for heading, sec in sections.items() if heading.startswith(prefix)),
        None,
    )
    if matched is None:
        continue
    # Strip the heading line from the body so the expander label avoids duplication.
    lines = matched.body.splitlines()
    label = lines[0].lstrip("# ").strip()
    body = "\n".join(lines[1:])
    with st.expander(label, expanded=default_open):
        st.markdown(body)

# --------------------------------------------------------------------------- #
# Footer: how-to-use, pulled from the doc.

how_to = sections.get("How to use this doc")
if how_to:
    st.divider()
    body = "\n".join(how_to.body.splitlines()[1:])
    st.subheader("How to update this tree")
    st.markdown(body)
