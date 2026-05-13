"""SACU Liquid Fuels Model — Streamlit documentation site.

Home page. Other pages auto-discovered under ``app/pages/``:
  - Hypothesis Tree  (per-segment driver decomposition)
  - Architecture     (load-bearing design decisions + scenario notes)

Every page reads the underlying repo docs at runtime so the markdown
files under ``docs/`` and the repo-root READMEs remain the single
source of truth.
"""
from __future__ import annotations

import streamlit as st

from shared.markdown_loader import read_doc, section


st.set_page_config(
    page_title="SACU Liquid Fuels Model",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("SACU Liquid Fuels Model")
st.caption(
    "Python rebuild of the Vopak/Reatile liquid fuels supply–demand model · "
    "v1 scope: SACU (ZAF, BWA, LSO, NAM, SZW) · monthly to 2050 · "
    "high_demand / low_demand scenarios"
)

# --------------------------------------------------------------------------- #
# Why this exists — pulled live from README.md

readme = read_doc("README.md")
why_section = section(readme, "Why this exists")
if why_section:
    st.markdown(why_section)
else:
    st.warning("Couldn't find the 'Why this exists' section in README.md.")

st.divider()

# --------------------------------------------------------------------------- #
# Segment status — pulled live from docs/demand_hypothesis_tree.md

st.header("At a glance")
st.caption(
    "Each demand segment's modelling status. **MODELLED** = full bottom-up logic; "
    "**HELD** = base-year anchor scaled by GDP elasticity; **DEFERRED** = stub."
)

status_section = section(
    read_doc("docs/demand_hypothesis_tree.md"),
    "At-a-glance summary",
)
if status_section:
    # Re-render skipping the heading line so it doesn't compete with our header.
    body_without_heading = "\n".join(status_section.splitlines()[1:])
    st.markdown(body_without_heading)
else:
    st.warning("Couldn't find the summary table in demand_hypothesis_tree.md.")

st.divider()

# --------------------------------------------------------------------------- #
# Navigation hint

st.subheader("Where to go next")
st.markdown(
    """
- **Hypothesis Tree** — driver decomposition per demand segment, with status tags
  (`[Q]` quantified · `[P]` provisional · `[N]` not modelled).
- **Architecture** — the load-bearing design decisions behind the rebuild and
  the v1 build-out priorities.

Use the sidebar on the left to navigate.
"""
)

# --------------------------------------------------------------------------- #
# Footer / provenance

st.sidebar.divider()
st.sidebar.caption(
    "Documentation is rendered live from the repo's markdown files. "
    "Edits to `README.md`, `CLAUDE.md`, and `docs/*.md` flow through to "
    "this app on the next reload."
)
