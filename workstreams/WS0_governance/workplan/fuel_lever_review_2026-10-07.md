# Diesel, jet and petrol: input review and model handoff

Nigel requested one main-story page per fuel with explicit lever values, L/M/H
settings and rationale. The confirmed horizons are **2030 and 2035**, within the
existing model horizon. Convergence pages 12–14 contain the draft tables.

The numeric source is `assumptions/2026/timeseries/fuel_lever_design_2026_10_07.csv`:
120 registered proposed observations across 20 fuel/lever rows, two years and
three input levels. Definitions, reference anchors, rationale and primary-source
URLs are in `pptx/story/fuel_lever_design_2026_10_07.json`. EXC-FUEL-LEVER-DESIGN
remains open until review and integration, with expiry 12 November 2026.
No forecast calculation or current production input has been replaced.

## How to use the settings

L/M/H orders the **input**, not the resulting demand. Higher freight activity,
mileage and OCGT generation increase demand; higher efficiency, BEV sales and
rail diversion reduce it. Higher utilisation and product yield increase domestic
output. Imports follow the matched demand/output/export/stock balance.

M is a proposed reference, not an agreed baseline. Build coherent baseline,
ample-supply and tight-supply cases by selecting compatible settings; do not
select every H input and label that high fuel demand. The 400 thousand bbl/day
restart is the existing conditional refinery illustration, not sanctioned output.

Percentages are stored as display percentages (e.g. 75 means 75%); convert to
fractions at the input adapter. Index reference is 2024=100, except OCGT which
uses FY2024. Define annual paths from matched opening observations to 2030 and
2035 before model use; no interpolation rule is implied by these snapshots.

## Acceptance tasks and client touchpoints

| Task | Proposed lead | Acceptance evidence | Touchpoint |
|---|---|---|---|
| Reconcile opening fuel demand, trade, output and stocks | Manish; Nigel source selection | Matched product/year balance and explicit residuals | Week 1 baseline review |
| Challenge each range and select a reference | Nigel; Henry technical review | Source-backed or explicitly accepted ranges; recorded client decisions | Week 1 assumptions discussion |
| Fit jet to aircraft movements | Manish | Matched ACSA movements/jet deliveries, airport coverage, aircraft/route mix, residual and back-test | Week 3 model review |
| Map fleet levers to cohort engine | Manish | BEV new-sales basis resolved; mileage and efficiency wired without changing old cohorts retroactively | Week 3 model review |
| Fit freight, rail and OCGT fuel effects | Manish | Calibrated activity-to-litres; one rail adjustment and one generation pathway | Week 3 model review |
| Resolve plant status, utilisation, product slates and restart | Manish; Henry | Product/year output bridge, downtime basis, compatible yields, FID/timing/ramp-up evidence | Week 3 model review |
| Implement coherent scenario mapping and sensitivity attribution | Manish; Nigel | Registered annual inputs, constraints, reproducible runs and litre changes by lever | Week 5 scenario review |
| Accept customer access and usable-capacity conclusions | Nigel; client | Cost/service/rights gates, unique flows and spare-space evidence | Week 6 decision review |

Weeks 1/3/5/6 are the existing proposed touchpoints, not confirmed meetings.
The three fuel pages do not complete customer access or operational L/M/H design.
Price elasticity, agricultural/mining fuel intensity, international/cargo mix,
non-ACSA traffic, plant eligibility and regional allocation remain owned review
tasks; no quantified sensitivity ranking is claimed before model runs.

## Dependency rules

- Utilisation and added refinery capacity are shared across fuels: count them once.
- Selected petrol, diesel, jet and other-product yields must form a feasible slate
  at each plant; conventional and synthetic plants cannot share an assumed yield.
- Jet yield applies only to capable plants; restart jet capability is unresolved.
- SAF changes fossil share; it does not by itself reduce total jet litres. ICAO's
  global 2030 emissions aspiration is not a South African volume mandate.
- Activity paths and GDP-driven demand are alternative driver constructions until
  calibrated; do not multiply overlapping growth effects without a tested model.
- Rail diversion is deducted once; coastal-to-inland transfers are counted once.

## Manish's input retained

The jet table follows the registered 5 October aircraft-movement driver decision,
rather than presenting the legacy passenger regression as the agreed future model.
The 2% post-2028 GDP continuation is identified as a team proposal; new cohort
efficiency endpoints come from the existing diesel/gasoline input CSVs. Other
numeric bands are authored sensitivity proposals and require review. Feedback
should identify the lever, year, input level, replacement value and evidence.
