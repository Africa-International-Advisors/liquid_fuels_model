# Six week model and infrastructure delivery plan

Proposed window: 2 October to 12 November 2026. Manish is available 100%; Nigel leads and Henry reviews. Resources are shared across workstreams. Dates, review timing and breadth remain planning targets.

| Week | Fuel model | WS5 infrastructure | Client analysis and storyboard | Acceptance evidence |
|---|---|---|---|---|
| 1 | Reproduce fuel baseline; map sources to calculations; investigate exact data flags; define levers | Secondary: evidence needed for a specific fuel integration or lever question | Frame decision questions and draft exhibits tied to the fuel baseline | Reproducible baseline, reviewed source-to-model mapping, defined levers and owned integration gaps |
| 2 | Reconcile history and opening fleet | Reconcile working capacity, shared pools and access | Competitors and market access; revise storyboard | Explained differences and reviewed route evidence |
| 3 | Review demand and production drivers | Build first-route flow and inventory checks | Walvis Bay assessment and regional screening | Manual case ties; conservation, capacity and unknown-data tests |
| 4 | Implement independent nine-scenario matrix | Integrate flows and evidenced priority routes | Accessible volumes and storage opportunities; draft pack | Product/geography mapping and unmet/unassessed demand reported |
| 5 | Validate history and sensitivities | Henry reviews constraints and access | Challenge opportunity claims and narrative | Review findings, sensitivity explanations and limitations |
| 6 | Reproducible outputs and refresh | Bottleneck map, capacity tables and provenance | Board pack and handover | Reproduction evidence and passed or outstanding release gates |

## Delivery controls

WS0 resolves priorities against shared capacity. Complete one defensible route before claiming national infrastructure coverage. WS1 sources evidence; WS2 calculates fuel demand and production; WS5 calculates infrastructure feasibility; WS3 integrates reporting. WS4 supports practical delivery tasks.

Nigel clarified on 5 October that fuel-model integration takes priority over the
broader infrastructure inventory and first-corridor work. Infrastructure is not
a Week 1 gate. Later route milestones remain planning targets and depend on
capacity after the fuel baseline and input mappings are coherent.

The core client analysis is the South African petrol/diesel outlook: national
import requirements, feasible regional flows/catchments, and Vopak's current
throughput and addressable commercial envelope. Jet remains tracked separately
in the underlying model and is excluded from client petrol/diesel totals.
Infrastructure supports catchment and flow feasibility; detailed storage/service
sizing is optional. The kickoff appendix pp. 31-38 supplies the infrastructure
starting geography, not verified route capacities or customer flows.

The analytical data-shape example is
`pptx/output/delivered/Vopak_market_envelope_illustrative_2026_10_06.html`.
It links national fuel balances, regional demand/access and terminal route rows.
Every volume is illustrative; current Vopak actuals are not supplied. Keep facility
receipt throughput separate from unique demand served, subtracting shared Durban-
Lesedi transfers when aggregating the latter. Retain actual/modelled/illustrative/
unknown status on each future input; unknown commercial access is not zero.

## Manish handoff for 6 October: use diagnostics to start integration

Use the [6 October feedback checklist and ordered focus](feedback_focus_2026-10-06.md)
for today's discussion. Nigel clarified that 6 October is data-first: source and
reconcile observations for provincial demand, the national fuel balance and all
driver pages before quantifying levers or adopting replacements. Nigel works on
main; Manish uses a named branch. The priorities below remain the Week 1 framework,
not a requirement to quantify scenarios or deliver an integration today.

Pull `origin/main` before working. The source audit and profile provide the starting
inventory; do not rebuild them manually. Manish investigates and proposes changes;
Nigel reviews the evidence and modelling choices. No existing input has been approved
by the diagnostic runs. Keep extraction corrections separate from deliberate
changes to modelling assumptions.

Start with [source profile](../../../output/delivered/source_profile_2026_10_05.html)
and the Direction tab in [source audit](../../../output/delivered/Liquid_fuels_source_audit_2026_10_05.xlsx).

| Diagnostic head start | Exact investigation | Required handback |
|---|---|---|
| Both scenarios reproduced; 29 of 66 blocks requested by the engine | Use the profile's calculation locations to map each current input and each staged replacement. Six requested CSVs cover GDP/capita, two efficiency series, OCGT load factor, passengers and refinery utilisation. | Current file/block -> proposed source -> transformation -> consuming function -> affected output. State time series, scalar, parameter group or dated snapshot. |
| All 24 sources.* blocks are staged | Begin the proposed macro mapping with `macro_worldbank.csv`, `macro_statssa.csv` and `gdp_growth_treasury.csv` against `macro.gdp_per_capita`. | Explain actual/forecast boundaries, constant-price basis and GDP/population consistency. A historical series ending in 2025 cannot replace a forecast through 2050 without an explicit extension rule. |
| Provincial gaps tab lists 26 exact province/product/year totals | Compare each listed annual row with its quarters in `fuel_sales_department_by_province_quarterly.csv` and the original workbook. See `_provincial()` in `src/lfm/scripts/fetch_energy_dept.py`. | Current annual value, observed quarters, source evidence and proposed corrected value or incomplete status. Do not assume missing quarters are zero. |
| Repeated keys tab identifies 558 extra refinery rows and 15 extra historical rows | Check `refinery_production.csv` against Production_High/Low named ranges; the supply engine currently takes the first repeated value. Check the five repeated jet year keys in `historical_demand.csv` against the actual RSA Demand table boundaries. | CSV row locations, all competing values, exact original cells and an explained proposed resolution. Do not sum or deduplicate automatically. |
| Twelve used provisional blocks identified | Check vehicle mileage, consumption, fuel split, retirement and segment split; industrial/agriculture baselines and elasticities; marine baseline, elasticity and product split. | Existing assumption -> source-backed proposal -> definition/units -> reason -> expected output effect. Stone reference parameters are calibrated estimates and are not automatically the correct replacement. |
| Source evidence lists five missing original records; DoT metadata fails parsing | Retrieve the referenced Stone and Stats SA originals and district workbook; fix the DoT YAML quoting and inspect its original. Wide table fields lists 489 fields not individually represented by register values. | Original evidence, extraction/transcription reconciliation and unresolved items with owners. Hash matches prove file identity, not numerical accuracy. |
| Key URL samples are reachable; World Bank had an earlier HTTP 502 | Use `source_connectivity_2026_10_05.csv` and refresh routes from the profile. Separate connectivity, full download, parser completeness and freshness. | Identify manual downloads and fallback behaviour. A successful website probe is not a successful data refresh. |

Define levers in Week 1: road freight to rail, BEV/hybrid uptake and charging access,
vehicle efficiency and mileage, OCGT utilisation, and domestic production availability.
For each, state the policy or investment intervention, baseline setting, alternative
settings, units, timing, affected equation/product, evidence and dependencies.
Distinguish interventions from observed input data; do not label a raw historical
time series a lever. Define demand and supply axes independently before implementing
the nine-scenario matrix. Gather infrastructure evidence only where a lever needs it.

6 October end-of-day review material: source-to-model mapping, row-level flag
investigations, verified newer provincial data or explicit missing coverage,
matched domestic production/import/export records, and sourced driver series
with periods, units and revisions. Collect the data underpinning lever choices
today; quantitative scenario settings and adoption follow evidence review.
Full history/fleet reconciliation continues into Week 2. Manish publishes his
named branch; Nigel reviews and integrates accepted changes into main after checks.

Preserve dated cockpit snapshots. Existing root governance exceptions and GATE_CHECKLIST.md remain in force; this plan does not close or extend them. New engine assumptions must be vintaged and registered before use. Passing tests does not establish approval.

See [WS5 brief](../../WS5_infrastructure_logistics/README.md) for input contracts, equations, owners and acceptance criteria.
