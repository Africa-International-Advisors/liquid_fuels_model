# WS5 Infrastructure and logistics

Build a reusable model of the infrastructure needed to move and store liquid fuels. Combine fuel availability and market demand from WS2 with transport, terminal and storage constraints to identify bottlenecks, unmet volumes and capacity gaps. Keep Vopak ownership, access rights and commercial interpretation in engagement inputs and reporting.

This workstream was authorised in the kickoff-deck discussion. The specification and backlog below are established; an infrastructure calculation engine is **not yet implemented**. The current fuel engine calculates demand and domestic production balances, not feasible route allocation or storage sufficiency.

Manish develops the data and implementation; Nigel leads methodology and prioritisation; Henry reviews. Manish's 100% availability is shared across workstreams, not additional staffing. Week dates and review capacity remain proposed.

## First deliverable

An auditable South Africa asset and capacity baseline, plus one traced Durban-to-inland-Gauteng product route using a selected terminal. Confirm physical connectivity, product compatibility and access before selecting a specific terminal pairing. Explain annual fuel volume, route capacity, terminal throughput, required inventory and usable storage separately. Every unknown must remain unknown, not zero or unlimited capacity.

Start with petrol, diesel and jet. Include refineries and synfuel plants as source nodes, ports and inland terminals as transfer/storage nodes, and markets as demand nodes. The regional screening scope remains SACU, including Namibia/Walvis Bay, and East, West, North Africa and SADC excluding SACU; detailed network expansion follows evidence and priorities. Gas pipelines are production-dependency context in this first version, not liquid-fuel transport links.

## Calculation design

1. Import demand, domestic production and scenario identifiers from WS2. Source feasible import availability separately; a national deficit is not proof of available imports.
2. Load a directed network of locations and compatible product routes. Track physical capacity and commercially accessible capacity separately.
3. Test a specified route allocation first. Enforce supply bounds, market demand, node conservation, route capacity and shared facilities. Report infeasible or unassessed flows explicitly. Automatic least-cost allocation follows only when comparable costs and solver requirements are agreed.
4. Calculate terminal throughput from handled volumes, counting a receipt and subsequent dispatch consistently rather than doubling one flow. Check receipt, dispatch and shared handling limits independently.
5. Calculate required working inventory from annual throughput and sourced stock-cover days: `required_storage_m3 = annual_throughput_m3 / days_in_year * stock_cover_days`. This is a screening calculation; separately assess parcel sizes, segregation and peak demand before claiming detailed tank adequacy.
6. Compare required storage with compatible usable capacity. Track gross capacity, working capacity, outage effects, existing commitments and client access without subtracting the same deduction twice. A shared diesel/petrol tank pool is counted once.
7. Report route bottlenecks, unmet demand, storage deficits and the assumptions binding each result. Show physical opportunity before applying client-specific rights, competitors and commercial terms.

An alternative tank-turn screening calculation is `annual_throughput / annual_turns`. Do not apply both tank turns and stock cover as independent deductions; reconcile their implied inventory policy. Pipeline throughput is a flow, measured in m3/year; tank capacity is a stock, measured in m3. Convert litres to m3 explicitly. Refineries' kbpd and gas PJ/year are separate quantities.

## Input contract to implement

| Dataset | Required fields and controls |
|---|---|
| Nodes | Stable node ID, asset/site name, type, country, market, coordinates, operator, operating status, effective dates |
| Links | Link ID, origin/destination node IDs, mode, direction, compatible products, capacity pool ID, physical throughput limit, period, availability, access status |
| Terminals | Node ID, product or shared pool, gross and working capacity, basis of deductions, commitments, receipt and dispatch rates, operating calendar |
| Inventory policy | Product/site, stock-cover days or tank turns, parcel/segregation constraints where known, basis and scenario |
| Fuel and market flows | Country/market, product, period, scenario, production availability, feasible imports, demand; national-to-market allocation requires declared evidence |
| Engagement access | Operator/client, asset or link ID, access entitlement and validity, contracted commitments, commercial restrictions |
| Evidence fields on every input | Source file/URL and cell/page, units, observation year, effective dates, register ID, owner, confidence, review status and expiry trigger |

Store future inputs under `assumptions/<vintage>/` and declare them in the root governance register before use. File adapters belong in `src/lfm/assumptions/`; pure calculations in `src/lfm/model/infrastructure/`; shared reporting in `src/lfm/reporting/`; model scripts in `src/lfm/scripts/`. These are intended module locations, not claims of existing code. Store generated results in `runs/`; keep source files in `external/`. No workstream-local engine or duplicated dataset.

## Evidence already held

| Evidence | Source and first action |
|---|---|
| Six refinery/synfuel capacities and yields | Original workbook `Assumptions M93:R97`; link to WS2 production, avoiding capacity double counting |
| Durban terminal capacity | Workbook `Market share C5:C6`, labelled 2024; reconcile usable capacity, product definitions and owner/access |
| Lesedi terminal capacity | Workbook `Market share C79:C80`, labelled 2026; confirm operational date and route connectivity |
| Provincial fuel storage | Workbook `Deficit Calculations AL1:AQ11`; reconcile to sites, retaining shared diesel/petrol category once |
| Ports and transport routes | Existing sourced appendix maps and their notes in `pptx/story/analyst-kickoff-scr.md`; schematic geometry is not evidence of capacity or access |
| Namibia and commercial context | Intermediary report, PDF pp. 33-40 and 42-45; update dated evidence before using it as current capacity |

## Six week backlog and acceptance

| Week | Deliverable | Acceptance evidence |
|---|---|---|
| 1 | Asset inventory, data dictionary, source register and selected first route | Every capacity has unit, vintage and source; missing connectivity/access exposed; Nigel reviews route selection |
| 2 | Reconciled storage and route data for the first corridor | Gross versus working versus available capacity explained; no duplicated provincial/site or shared-product capacity |
| 3 | Pure functions checking allocation and storage for one route | Hand-calculated case ties; meaningful tests for conservation, binding capacity, shared tanks and unknown data |
| 4 | Connect WS2 scenarios and priority network routes | Product/period/geography mappings reconcile; feasible, infeasible and unassessed cases remain distinct |
| 5 | Constraint and sensitivity review with Henry | Higher demand or lost capacity produces explainable results; review access assumptions and double counting |
| 6 | Reproducible infrastructure outputs and handover | Bottleneck map, capacity tables, storage gap, provenance and recorded limitations; reviewer findings resolved or explicitly outstanding |

The schedule is proposed and depends on data access and shared team capacity. WS0 prioritises the first corridor if evidence is insufficient for a complete national network; no national completeness claim follows from a corridor demonstration.

## Open inputs and stop conditions

| Gap | Owner | Due or expiry trigger | Consequence while unresolved |
|---|---|---|---|
| Usable and committed tank capacities, product segregation | Manish; Nigel reviews | Before week-2 baseline acceptance | Inventory evidence only; no commercially available storage claim |
| Route limits, connectivity and commercial access | Manish; Nigel reviews | Before first allocation result | Route is unassessed; no feasible served-volume claim |
| Market allocation of national demand and feasible imports | Nigel with WS1/WS2 | Before week-4 integration | No regional flow allocation or imported-volume availability claim |
| Stock-cover basis, parcels and handling constraints | Manish; Henry challenges | Before storage gap interpretation | Screening sensitivities only, explicitly labelled |
| Gas constraints and production dependencies | Nigel with WS2 | Before changing refinery/synfuel production | Gas remains context, not a liquid-capacity conversion |

These planning gaps are not new engine inputs or closed model exceptions. Formal use still requires the root `GATE_CHECKLIST.md`, independently reviewed evidence and recorded approval.

## Network inventory follow up

Manish must reconcile the fuller pipeline inventory and national-road coverage before week-2 route acceptance. The appendix now shows major national roads and documented Transnet liquid connections, alongside the gas map. Witbank, Tarlton and Rustenburg branch topology, effective operating dates, private terminal pipes, remaining national routes and last-mile roads are not yet a complete routing dataset. Nigel reviews completeness and route access before an allocation is described as feasible. Map waypoints must not be used to calculate transport distance or capacity.

## Explicit infrastructure coverage

The agreed asset scope includes **rail, ports, roads, pipelines, power lines, power stations and airports**, alongside storage and terminal handling. The assumptions exhibit in the Analytical Requirements section defines the input families; no capacity values are assumed by adding an asset class.

| Asset class | Required baseline inputs |
|---|---|
| Ports | Berths, vessel and parcel limits, discharge rates, windows, terminal links and access |
| Airports | Jet-fuel demand allocation, supply routes, tankage, receipt and hydrant limits, stock cover |
| Rail | Product-compatible links, train paths, wagons, payload, turnaround, reliability and access |
| Roads | Routes, tankers, payload, trip times, fleet availability and access restrictions |
| Pipelines | Product or gas type, direction, connections, throughput, shared pools and availability |
| Power lines | Relevant grid nodes and connections, transfer limits, outage assumptions and reliability |
| Power stations | Technology/fuel, MW, commissioning, availability, dispatch, efficiency and supply links |
| Tanks and storage | Gross and working tank capacities, segregation, commitments, receipt/dispatch limits and inventory policy |

Manish sources the asset inventory; Nigel owns WS2/WS5 interface methodology; Henry reviews before integrated use. Complete the relevant dependency assessment before the first corridor passes its gate. Missing data remains unassessed. Grid MW and electricity MWh are not fuel throughput. Power networks inform asset availability and backup demand via a reviewed mapping; full electrical load-flow and dispatch optimisation are not implied. WS2 owns power-sector fuel calculations; WS5 owns asset/network constraints. Airport-level demand is allocated from the aviation total, never added again. Record grid-related outages consistently with other availability deductions to avoid double counting. New inputs require assumption-register entries before use.
