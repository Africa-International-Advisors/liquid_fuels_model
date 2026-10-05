# Analyst kickoff: slide copy and layout mockup

Status: 12-page outline approved in chat. User subsequently instructed generation
of the actual pages. Implemented in scripts/build_kickoff.py, with final spacing
and cover adjustments following PowerPoint rendering.
Template: ../templates/AIA_Vopak_Template.pptx. Preserve original master and logos.
Audience: analyst onboarding and working discussion. Proposed plan, not a client commitment.
No new model results are claimed. No changes to model scope or project canon.

## 1. Liquid fuels model: analyst kickoff

Layout: template Title. Editable text placeholders/shapes, no table.

Liquid fuels model: analyst kickoff

Development priorities and the six-week working plan

2 October 2026

Internal working discussion

Speaker note: The engagement provides the immediate questions. The reusable model
is the analytical foundation. Confirm the analyst's familiarity with the workbook.

## 2. The question anchoring this engagement

Layout: Header only. Large question in editable text shape, two supporting text sections.

How will changing fuel demand and domestic production affect import requirements,
and what could that mean for storage opportunities in markets relevant to Vopak?

Model contribution
Estimate demand, production and the resulting supply balance under explicit scenarios.

Commercial interpretation
Assess how market balances interact with logistics, competition and customer access.

Speaker note: This question was agreed in the planning discussion. A national supply
gap needs additional evidence before it can support a terminal investment conclusion.

## 3. Where the model fits into the wider assignment

Layout: Header only. Native PowerPoint table with four rows.

| Proposal area | Contribution and additional work |
| --- | --- |
| Fuel demand and supply outlook | Core model contribution: demand drivers, production scenarios and balances |
| Competition and storage dynamics | Combine model outputs with competitor and logistics research |
| Walvis Bay opportunity | Add local demand, corridor, infrastructure and customer evidence |
| Wider African opportunities | Screen markets separately and agree any detailed model expansion |

Footer: The proposal is broader than the current model implementation.

Source note: AIA proposal, August 2026, PDF pages 7-12. The repo currently contains
South African inputs within an intended SACU model scope. Wider coverage needs agreement.

## 4. What we inherit from the previous work

Layout: Header only. Native PowerPoint table, closing text shape.

| Starting point | What it gives us | What we must establish |
| --- | --- | --- |
| Excel workbook | Calculation history and scenario assumptions | Source lineage and intended formulas |
| 2025 intermediary report | Previous findings and the business narrative | Which evidence and assumptions need updating |
| Python implementation | Repeatable calculations and structured inputs | Reconciliation, methodology and validation |

Footer: Explain differences between the workbook, report and Python outputs.

Speaker note: Do not assume these files represent an identical vintage. The report
contains evolving supply scenarios. For example, its Natref page includes different
descriptions of continued operation, export-only operation and shutdown.
Sources: external/sources workbook; intermediary report PDF page 28; CLAUDE.md.

## 5. A reusable model, applied to a specific question

Layout: Header only. Three numbered editable text sections, no table.

1. Reusable calculations
Fuel demand, domestic production, supply balances and sensitivity calculations.

2. Engagement configuration
Market coverage, evidence vintage, forecast period and scenario assumptions.

3. Commercial application
Interpretation for Vopak's terminals, competitors and investment questions.

Footer: Keep client-specific choices in inputs and reporting. Keep calculations reusable.

Speaker note: Agnostic means reusable and transparent. It does not imply unlimited
products or geographies. Geographic expansion remains a deliberate scope decision.

## 6. How the model works

Layout: Header only. Editable numbered process text, no table. Native connectors
may be added only if approved as an editable process diagram.

1. Evidence and assumptions
Historical observations, economic drivers and scenario settings.

2. Demand calculations
Vehicles, aviation, power generation, industry, marine and agriculture.

3. Domestic supply
Production capacity, utilisation and operating scenarios.

4. Supply balance and outputs
Compare demand with domestic supply by fuel and period.

Footer: The resulting gap informs import analysis. Trade and stock treatment need validation.

Speaker note: Demand currently runs monthly and supply annually. Annual reporting
aligns the two. Current inputs cover South Africa. Do not equate the gap mechanically
with gross imports without treating exports, stock changes and other balance items.
Source: CLAUDE.md and model architecture.

## 7. From import requirements to storage opportunity

Layout: Header only. Four numbered editable text sections, closing text shape.

Market requirement
Which products, volumes and locations require additional supply?

Route and infrastructure
Which ports, corridors and terminals can serve that demand?

Commercial access
Which customers and volumes are available after competing supply and contracts?

Storage requirement
What capacity and utilisation follow from throughput, inventory and turnaround assumptions?

Footer: The current model supports the market balance. The remaining steps need additional analysis.

Speaker note: Throughput is a flow and storage capacity is a stock. Avoid using them
interchangeably. This page describes the analytical bridge, not a new build commitment.
Source: proposed analytical approach informed by the August 2026 proposal, pages 8-12.

## 8. What works today and what needs development

Layout: Header only. Native PowerPoint table with two columns.

| Implemented | Development and validation priorities |
| --- | --- |
| Python demand and supply calculations | Reconcile historical outputs and explain differences |
| High and low demand scenarios | Review scenario definitions and how inputs connect |
| Structured assumptions and provenance | Verify sources, ownership and review status |
| South African inputs | Validate opening vehicle stock and sector baselines |
| Documentation and automated checks | Agree geographic coverage and complete independent review |

Footer: Current outputs are provisional. Passing software checks does not establish model validity.

Source: CLAUDE.md; GATE_CHECKLIST.md. No new execution results are asserted here.

## 9. Learning Python through the model

Layout: Header only. Native PowerPoint mapping table and a separate exercise text shape.

| Familiar Excel concept | Python equivalent in this project |
| --- | --- |
| Input cells | Assumption files |
| Formulas | Functions |
| Worksheets | Modules |
| Scenario switches | Scenario configuration |
| Reconciliation checks | Tests and comparison reports |

First exercise: trace one agriculture calculation from evidence to input, function and result.
Change one assumption, predict the effect and explain the observed difference.

Speaker note: Agriculture is a proposed manageable starting point, subject to the
analyst's experience. Success means explaining the calculation and checking a change.

## 10. What we will deliver over six weeks

Layout: Header only. Native PowerPoint table, six rows.

| Week | Focus | Proposed deliverable |
| --- | --- | --- |
| 1 | Understand and reproduce | Run the model and explain one calculation |
| 2 | Reconcile | Document differences against Excel and historical data |
| 3 | Improve priority drivers | Review selected assumptions and calculations |
| 4 | Integrate scenarios | Check demand, supply and scenario consistency |
| 5 | Validate and interpret | Historical comparisons and sensitivity results |
| 6 | Document and hand over | Repeatable workflow, limitations and remaining backlog |

Footer: Proposed model workplan. Confirm capacity and priorities at kickoff.

Speaker note: This is the model-development stream within the wider proposal.
Competitor research, Namibia work and Africa screening require their own resourcing.
Validation may expose issues that change the sequence or final deliverable scope.

## 11. How we will work and review progress

Layout: Header only. Two editable text sections, no table.

Working rhythm
The analyst develops small, traceable changes and records questions.
The modelling lead reviews methodology, assumptions and interpretation.
A weekly walkthrough explains what changed, why it changed and what remains unresolved.

A completed task includes
An identified source and assumption owner.
A calculation another person can follow.
A relevant check with an explained result.
Documented limitations and a recorded review.

Footer: Roles and review cadence are proposed for agreement.

Speaker note: Keep reviews supportive. The analyst brings Excel and analytical
experience immediately and learns Python through actual modelling tasks.

## 12. What we agree today and do first

Layout: Header only. Two editable text sections, no table.

Decisions for this session
Priority business questions and first model improvements.
Analyst availability, data access and review cadence.
The first calculation to own and the evidence needed to check it.

First deliverable
Run one scenario, trace one calculation and explain its differences from Excel.

Acceptance check
The analyst can explain the inputs, change an assumption and verify the result.

Speaker note: End by recording actual agreements, owners and dates. Do not treat
the proposed plan or the presentation itself as evidence of agreement.
