# Engagement workstreams

This repository uses the project-canon **model plus engagement** profile, with the
optional `pptx/` workspace. Work is organised here by delivery responsibility; model
code, inputs and outputs retain their canonical homes.

| Workstream | Purpose | Proposed delivery owner | Accountable lead |
|---|---|---|---|
| WS0_governance | Scope, workplan, meetings, risks, decisions and release gates | Nigel | Nigel |
| WS1_data_validation | Sources, assumption quality and historical reconciliation | Manish | Nigel |
| WS2_model_development | Demand, supply, scenarios and agreed regional coverage | Manish, paired on complex changes | Nigel |
| WS3_reporting_delivery | Excel outputs, presentation story and handover artifacts | Manish, with builder support | Nigel |
| WS4_analyst_enablement | Excel-to-Python learning and independent refresh capability | Manish | Nigel |
| [WS5_infrastructure_logistics](WS5_infrastructure_logistics/README.md) | Transport, terminal and storage capacity; feasible flows and infrastructure gaps | Manish | Nigel |

These are responsibilities across one team: Manish (analyst, available 100%), Nigel (modelling lead) and Henry (reviewer). Review dates and capacity remain proposed.

## Start here

- [Current Week 1 progress and next handbacks](WS0_governance/workplan/six_week_plan.md#current-progress--7-october-2026-week-1)

- [6 October stand-up transcript](WS0_governance/meetings/2026-10-06_vopak_standup.docx)
- [6 October feedback checklist and Manish focus](WS0_governance/workplan/feedback_focus_2026-10-06.md)
- [Historical pre-kickoff cockpit](WS0_governance/workplan/reflection_2026-10-01_internal.html)
- [Six-week plan](WS0_governance/workplan/six_week_plan.md)
- [Scope and roles](WS0_governance/workplan/scope_and_roles.md)
- [2 October kickoff agenda](WS0_governance/meetings/2026-10-02_kickoff_agenda.md)

## Weekly pulse

Refresh on Fridays after the review. Save a new dated `reflection_<YYYY-MM-DD>_internal.html`
under WS0's `workplan/`, preserving prior snapshots. Start from the preceding snapshot or
`../external/templates/TEMPLATE_cockpit.html`; update facts, dates and the browser storage
key. Record decisions, issues, risks, next actions and resource/budget information only
when known. The proposed review dates are 2, 9, 16, 23 and 30 October, 6 November,
with the final review on 12 November. No reminders or scheduled automation have been created.

The cockpit is the dated management record. Its browser-local delivery-board edits are
personal working notes until copied back into the next committed snapshot. Copy buttons
prepare draft communications; they do not send messages. Record actual meeting outcomes
separately in `meetings/`, reviews in `retros/`, and evidence links in `evidence/`.

## Filing rules

- `governance/` at the repo root is the **model audit trail**, not the PM workplan.
- WS0 is **engagement governance**, with links to that audit trail and the release gate.
- Model code stays in `src/lfm/`; presentation builders stay in `pptx/scripts/`.
- Received material stays in `external/` (presentation templates: `pptx/templates/`).
- Model assumptions stay in `assumptions/`; results in `runs/`; built artifacts in
  `output/` or `pptx/output/`, with delivered copies in the relevant `delivered/` folder.
- Workstreams contain briefs, decisions, acceptance evidence and links, not duplicate code or data.
- Cross-cutting methodology stays in `docs/`. Personal scratch, if needed, uses `_scratch_<INITIALS>/`.
