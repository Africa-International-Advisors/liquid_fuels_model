# Outlook hierarchy feedback â€” 6 October 2026

User confirmed the three supplied Vopak screenshots apply to the Vopak source deck, separate from the Mozambique kickoff.

- Page 14: a dominant 5.5 figure, secondary units, proportional volume bridge, four access gates, shorter evidence points and distinct owner actions.
- Page 16: native editable icons over the four table columns; Matola and Walvis Bay explicitly labelled port/storage gateways for inland route comparisons. Priorities and timing remain conditional hypotheses.
- Page 17: full-width native inventory chart, direct data labels, explicit units and uniform-flow assumption. The 14-day example is highlighted; detailed calculations and operating checks stay in notes. Working stock is distinguished from new capacity.

Build: `python pptx/scripts/apply_outlook_hierarchy_feedback.py <original-deck> <new-version>`.
Full-build page sources were also updated, including bypass of the previous inventory sidebar and static title overrides.

Verification: native package and physical bounds checks pass; 19 unaffected slides retain identical XML; inventory values are unchanged; 22 PDF pages exported through PowerPoint. Governance coverage passes with 52 pre-existing open exceptions; this is a provisional illustrative presentation and records no customer capture or investment commitment.

Source and build hashes are recorded in `pptx/qa/outlook_hierarchy_feedback/provenance.json`. Source-level independent peer challenge passes; rendered visual review recorded below.

Independent rendered peer review passes pages 14, 16 and 17: hierarchy and labels are clear; no clipping, overlap or unsupported conclusions.
