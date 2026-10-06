# Partner South Africa story: evidence and gap closure

The Situation-Complication-Resolution story organises the work. Existing analysis establishes historical demand and storage context; current imports, driver forecasts, Vopak share and investment conclusions still need evidence. Petrol/diesel is the client scope; jet remains separate. Partner propositions are hypotheses to test.

| Story | Existing work | Required conclusion |
|---|---|---|
| Situation | Historical sales, regions and operator geography (pp2-3,7-8). | Recent matched-year demand/production/finished imports, entry ports and economic market boundary. |
| Complication | Provisional demand/supply engines and staged sources; pp4-6 illustrations. | Quantified driver reversals, dated refinery cases and comparable route costs. |
| Resolution | Competitor footprint and storage stocks. | Actual Vopak-served demand and commercial envelope; investment after flow/access evidence. |

## Detailed gaps

Owners and week windows are analytical responsibilities and planning targets, not confirmed commitments. Source leads are retrieval routes, not newly validated observations. Every record stays open until its closure evidence is reviewed.

### SA01 - SA demand history and regional market size

**Situation | P0 | Open; existing evidence does not establish closure**

Existing: Pack pp2-3,7: quarterly provincial sales 2013-2022; national series 2005-2023; 2023 incomplete.

Gap: Later complete year; six provincial/national annual differences; historical driver contributions not quantified.

Action: Review 2013/14/15/17/18/21 against original workbooks; source later full years. Preserve 2022 historical label.

Close when: Old value, proposed value, source cell and reason for each correction; all province/product quarters; national tie.

Owner: Manish; Nigel review

Timing: W1 investigate; W2 reconcile

Source lead: fuel_sales_department_by_province_quarterly.csv; fuel_sales_department.csv; DMPR index

Refresh: Manual workbook download and parser rerun; completeness and revisions checked.

Model connection: pptx/scripts/provincial_demand_map.py::sales; reporting evidence, not approved model calibration.

### SA02 - Economically reachable eastern/inland market

**Situation | P0 | Open; existing evidence does not establish closure**

Existing: Working province groups p2; illustrative road-cost map p5; storage footprint.

Gap: Actual customer destinations, cost threshold, route capacity and commercial rights.

Action: Use delivered transport cost R/litre for actual destinations; qualify physical reach and customer access separately.

Close when: Reachable and commercially accessible volume by product/destination/year; sourced costs and explicit unassessed residual.

Owner: Manish route evidence; Nigel client access

Timing: W1 define contract; W2-W4 integrate

Source lead: Regional membership CSV; client destinations; route tariffs and quotations

Refresh: Manual client/route evidence; refresh tariff, access or destination changes.

Model connection: Illustrative accessibility module is presentation only; no operational routing engine.

### SA03 - Domestic production versus finished imports

**Situation | P0 | Open; existing evidence does not establish closure**

Existing: Energy balance 2007-2021 staged; provisional supply engine; p4 provincial source illustration.

Gap: Matched recent demand, output, imports, exports and stocks; actual provincial origin unavailable.

Action: Reconcile national petrol/diesel first; retain provincial origin as unknown without evidence; separate crude and finished products.

Close when: Production + imports - exports - stock build = consumption by fuel/year; unit/coverage bridge and residual explained.

Owner: Manish; Nigel review

Timing: W1 mapping; W2 historical balance

Source lead: energy_balance_department.csv; DMPR commodity flow; SARS trade data

Refresh: Manual annual energy workbook and monthly customs download; preserve revisions.

Model connection: src/lfm/model/supply/flows.py::compute_balance currently demand less supply; exports/stocks not explicit.

### SA04 - Import entry ports and origin

**Situation | P1 | Open; existing evidence does not establish closure**

Existing: Ports and schematic corridors from kickoff appendix.

Gap: Product-specific finished imports by port/year and source country; liquid bulk is not all fuel.

Action: Bridge SARS product/quantity data to TNPA port cargo; check port identifier availability and density conversion.

Close when: National finished imports tied to evidenced port allocations; unallocated remainder explicit.

Owner: Manish; Nigel source access

Timing: W2-W3

Source lead: https://tools.sars.gov.za/tradestatsportal/data_download.aspx ; https://www.transnetnationalportsauthority.net/Commercial%20and%20Marketing/Pages/Port-Statistics.aspx

Refresh: Manual portal downloads; check HS coverage, revisions, tonnes/litres and crude/nonfuel exclusions.

Model connection: No imported-volume allocation by port/destination in current engine.

### SA05 - Power-generation diesel and potential reversal

**Situation / Complication | P0 | Open; existing evidence does not establish closure**

Existing: Eskom OCGT observations 2022-2026 staged; engine capacity/load factor/efficiency path.

Gap: Eskom/IPP coverage, fiscal/calendar alignment, fuel conversion and forecast dispatch. No loadshedding does not mean no OCGT diesel.

Action: Reconcile generation and fuel burn by plant set; calibrate dispatch alternatives; avoid additive double-counting.

Close when: Historical GWh-to-litres tie; baseline/alternative dispatch, units, dates and incremental demand effect.

Owner: Manish; Nigel review

Timing: W1 lever; W2-W3 calibration

Source lead: ocgt_generation_eskom.csv; generation.yaml; primary Eskom operating reports

Refresh: Manual quarterly/annual operating reports; scope and period checks.

Model connection: src/lfm/model/demand/generation.py::compute_country_annual.

### SA06 - Road-to-rail freight shift

**Situation / Complication | P0 | Open; existing evidence does not establish closure**

Existing: Road vehicle cohort calculation and schematic rail context; no mode-shift source series found in current vintage.

Gap: Road/rail freight, tonne-km, distance, payload, empty running and feasible rail intervention.

Action: Use Stats SA P7162 and operator traffic evidence; distinguish tonnes/revenue/tonne-km; convert displaced truck work into diesel.

Close when: Specific intervention with baseline/alternative mode shares, dates and diesel-intensity bridge; no duplicate mileage reduction.

Owner: Manish; Nigel intervention; Henry review

Timing: W1 lever definition; W2-W4 integration

Source lead: https://www.statssa.gov.za/?PPN=P7162&SCH=74110&page_id=1854 ; Transnet freight traffic/access evidence

Refresh: Manual monthly survey and annual operator reports; coverage/revision checks.

Model connection: vehicles.py has no explicit rail-shift lever.

### SA07 - BEV, hybrid, efficiency and charging effects

**Situation / Complication | P0 | Open; existing evidence does not establish closure**

Existing: Naamsa NEV sales 2019-2025 staged; engine EV curve and efficiency parameters.

Gap: Sales versus stock, segment scope, BEV/HEV distinction, survival, mileage and charging intervention.

Action: Calibrate uptake and fleet turnover; retain hybrids as fuel users with separate efficiency; define charging policy/investment lever.

Close when: Opening-fleet/cohort tie; drivetrain-specific L/100km; dated uptake alternatives and litres effect.

Owner: Manish; Nigel review

Timing: W1 levers; W2-W3 calibration

Source lead: nev_sales_naamsa.csv; vehicles.yaml; official registration evidence

Refresh: Manual quarterly/annual data; reconcile drivetrain taxonomy and scope.

Model connection: src/lfm/model/demand/vehicles.py::compute_country_annual and _ev_penetration.

### SA08 - GDP, fuel prices and kilometres travelled

**Situation / Complication | P0 | Open; existing evidence does not establish closure**

Existing: Macro sources staged; price series 2011-2024-04; engine GDP/capita new-sales relationship.

Gap: Real-price basis, causal activity effect, elasticities and actual/forecast extension.

Action: Map GDP source into provider with population/base-price rules; propose price-to-km response separately from efficiency.

Close when: Explicit historical/forecast boundary and consuming function; calibrated sensitivity without duplicate activity reductions.

Owner: Manish; Nigel review

Timing: W1 mapping; W2-W3 validation

Source lead: macro_statssa.csv; macro_worldbank.csv; gdp_growth_treasury.csv; fuel_prices_department.csv

Refresh: Stats SA/Treasury/DMPR manual downloads; World Bank API; independent vintage and freshness checks.

Model connection: vehicles.py GDP new-sales path; no explicit fuel-price-to-mileage response.

### SA09 - Refinery closures, availability and SAPREF proposal

**Situation / Complication | P0 | Open; existing evidence does not establish closure**

Existing: Refinery assumptions and utilisation 2008-2050; provisional supply engine; duplicate-row diagnostics.

Gap: Current output/yields/status; dated closures/restarts; SAPREF project evidence; 558 extra refinery rows unresolved.

Action: Resolve repeated keys against original named ranges; build refinery-year status and output; treat proposals as conditional scenarios.

Close when: Unique country/year/scenario keys with source cells; actual/proposed distinction; per-refinery output tie and import sensitivity.

Owner: Manish; Nigel review; Henry challenge

Timing: W1 duplicates; W2-W3 scenarios

Source lead: supply.yaml; refinery_production.csv; original workbook; primary operator/CEF/PetroSA reports

Refresh: Manual reports; refresh outages, restart, ownership or sanctioned-project changes.

Model connection: src/lfm/model/supply/flows.py::compute_supply.

### SA10 - Secunda gas/MRG and Natref future

**Complication | P1 | Open; existing evidence does not establish closure**

Existing: Generic Sasol/Natref capacities, yields and utilisation; no plant-level gas-liquid linkage.

Gap: MRG timing and causal liquid-fuel effect; Natref future not established; partner propositions untested.

Action: Check latest primary Sasol disclosures; technical reviewer specifies mechanism before any fuel-output change.

Close when: Documented plant-level mechanism and dated scenario; no gas-to-liquid displacement inferred without evidence.

Owner: Manish sources; Henry technical review; Nigel scenarios

Timing: W2-W3

Source lead: https://www.sasol.com/sasol-suite-reports ; 2026 Sasol SEC 20-F

Refresh: Manual quarterly/annual operating guidance and plant/gas changes.

Model connection: No gas-to-fuel mechanism; utilisation/yield changes need explicit sourced scenario.

### SA11 - Durban-NMPP-Lesedi versus road/rail, Matola and Walvis Bay

**Complication | P0 | Open; existing evidence does not establish closure**

Existing: Schematic appendix routes and illustrative Durban/Lesedi road-cost map.

Gap: Comparable route costs, NMPP capacity/tariff, actual rail service and cross-border feasibility.

Action: Choose first product/customer destination; compare full handling/transport/transfer cost, border/FX where relevant, same period and basis.

Close when: Comparable delivered R/litre with cost components, capacity/access limits and dated sources; no national optimisation claim.

Owner: Manish evidence; Nigel corridor choice; Henry review

Timing: W1 comparison contract; W2-W4 first route

Source lead: Client tariffs/quotes; current pipeline, port, road/rail and border operator evidence

Refresh: Manual published tariffs and dated quotes; tariff-year, FX and access refresh.

Model connection: No operational route allocation or delivered-cost engine.

### SA12 - Vopak market share at Durban and Lesedi

**Resolution | P0 | Open; existing evidence does not establish closure**

Existing: Sourced regional sales p7; published capacity p8; illustrative transfer arithmetic p6.

Gap: Unique customer deliveries, receipts, shared transfers, destinations and matched period.

Action: Nigel requests client flow extract; Manish reconciles receipt/transfer/final-delivery records and counts final demand once.

Close when: Separate terminal throughput and unique served-demand shares; matched-year/product denominator; traceable records, no capacity-as-share.

Owner: Nigel client request; Manish reconciliation

Timing: W1 request/schema; W2+ on receipt

Source lead: Vopak operational/customer data; public unique-throughput data not established

Refresh: Client-approved monthly/annual extract with product/destination coverage and transfer IDs.

Model connection: Current p6 flow volumes illustrative; future shared flow contract.

### SA13 - Additional commercially contestable market

**Resolution | P1 | Open; existing evidence does not establish closure**

Existing: Competitor footprint and partial published storage; lease sites explicitly conditional.

Gap: Usable product-compatible tanks, spare routes, contracts, switching, customer overlap and Northern Cape inventory.

Action: Combine customer destinations with evidenced routes and rights; separate physical reach, commercial envelope and potential capture.

Close when: Accessible demand by product/region/period; explicit assumptions and unassessed residual; competitors volume is not automatically capturable.

Owner: Manish evidence; Nigel commercial review

Timing: W2-W4

Source lead: Storage/competitor CSVs; NERSA licences; client contracts and operator notices

Refresh: Manual licences/notices; refresh contractual period, site changes and lease milestones.

Model connection: No validated commercial customer-flow allocation.

### SA14 - New storage and investment scope

**Resolution | P2 | Open; existing evidence does not establish closure**

Existing: Partial gross/lease stocks, without client handling/inventory profile.

Gap: Incremental accessible flows, turnover/peak inventory, product compatibility, cost and commercial return criteria.

Action: Establish flow/access case first; then test service requirements and a separately scoped investment case.

Close when: Throughput-to-usable-stock bridge with seasonality, inventory days and dispatch limits; downside sensitivity; no investment claim from import deficit alone.

Owner: Nigel commercial gate; Manish; Henry review

Timing: W4-W6 only if prioritised

Source lead: Client service/stock profiles and scoped cost evidence

Refresh: Manual client data; refresh on demand/access case changes.

Model connection: Detailed service sizing deferred; infrastructure secondary to fuel integration.

## Week 1 handback

1. Pull origin/main every morning and before pushing; both analysts use main. Preserve work, run governance and relevant checks.
2. Reproduce baseline; hand back source -> transformation -> consuming function -> output for used/staged inputs.
3. Investigate exact provincial and duplicate-row flags with old/proposed values, original cells and reasons; do not silently overwrite received data.
4. Define rail, BEV/HEV, efficiency/mileage, power dispatch and refinery levers: intervention, baseline, alternative, units, timing, equation, evidence and dependencies.
5. Nigel requests Vopak flows and agrees the first product/destination corridor; Manish prepares flow schema and cost-comparison contract. Broad infrastructure and investment sizing are secondary.
6. Present one reviewed integration candidate with before/after outputs and remaining gaps. Definitions and technical checks do not imply business approval.

## Consolidated pack

One summary page before closing: existing analytical pages 2-8 keep their numbers; summary is page 9 and closing becomes page 10. The summary is a roadmap, not a forecast or closed-gap assertion.

Primary retrieval leads checked: [Stats SA land transport](https://www.statssa.gov.za/?PPN=P7162&SCH=74110&page_id=1854), [SARS trade downloads](https://tools.sars.gov.za/tradestatsportal/data_download.aspx), [TNPA port statistics](https://www.transnetnationalportsauthority.net/Commercial%20and%20Marketing/Pages/Port-Statistics.aspx), [Sasol report suite](https://www.sasol.com/sasol-suite-reports).

Governance remains draft with 50 open exceptions. No peer review, exception closure or business approval is inferred.
