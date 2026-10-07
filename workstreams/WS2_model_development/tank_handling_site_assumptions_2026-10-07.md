# Tank handling: site assumptions for Lesedi and Durban, 7 October 2026

Priority 4 on Manish's focus page (Convergence pack p24). Proposed operating
ranges for Nigel to agree; nothing here is accepted. The values, one per row
and each marked **evidence** or **estimate**, are in
`assumptions/2026/infrastructure/terminal_site_assumptions.csv`. The source
documents are kept in `external/data/raw/vopak_storage_20261006/`.

No operating data from Vopak has been used. Realised outbound volumes, tank
occupancy and downtime are still needed and are listed at the end.

## Vopak Lesedi (Jameson Park)

| Item | Value | Basis | Source |
|---|---|---|---|
| Design capacity | 140,000 m3: petrol 40,000; diesel 80,000; one 20,000 tank for diesel or petrol | Evidence | NERSA licence amendment, 6 August 2025, tank table |
| Operational capacity, six original tanks | 88,000 m3 of 100,000: petrol 34,000; diesel 54,000 | Evidence | Vopak's licence application to NERSA (2020), p.8-9 |
| Operational capacity, two new tanks | 18,000 m3 each | Estimate | Licence leaves it blank; taken as equal to the identical original tanks |
| Operational capacity, whole site | 124,000 m3 | Evidence plus estimate | Sum of the two rows above |
| Receipts | Pipeline only, 2 x 16 inch lines from Transnet; at most 1,500 m3 an hour | Evidence | Licence application, p.9 |
| Dispatch | At most 1,500 m3 an hour; 80% road and 20% pipeline by design | Evidence | Licence application, p.9 |
| Road loading | Eight bays at 125 m3 an hour each; unchanged with the new tanks | Evidence | Licence application, p.9; NERSA 2025, paragraph 9 |
| Practical road dispatch | About 300,000 m3 a month | Estimate | Eight bays, pumping half the time, 20 hours a day |
| Monthly turns of operational capacity | Low 1; base 2; high 2.4 | Estimate | Base uses Vopak's Durban target as an analogue; high is the road dispatch estimate over 124,000 m3 |

Annual handling on these assumptions: 1.5 (low), 3.0 (base) and 3.6 (high)
million m3. The pack's current sensitivity, 1, 2 and 3 turns of the 140,000 m3
gross figure, gives 1.68, 3.36 and 5.04. The high case falls because eight
loading bays cannot plausibly dispatch three turns a month.

The two new tanks were licensed in August 2025 with commercial operation
scheduled for early January 2026; the dates of actual commissioning are
redacted. Vopak's terminal page now shows 140,000 m3.

## Vopak Durban (Island View)

| Item | Value | Basis | Source |
|---|---|---|---|
| Gross capacity, all products | 360,246 m3 | Evidence | Vopak terminal page, checked 6 October 2026 |
| Design capacity built for petrol and diesel | 162,000 m3 in ten tanks | Evidence | Vopak news release, 17 February 2017 |
| Operational capacity for petrol and diesel | 146,000 m3 | Estimate | 90% of design, as at Lesedi's 20,000 m3 tanks |
| Receipts and dispatch | Vessel (five berths), pipeline, rail and truck | Evidence | Vopak terminal page |
| Receipt and dispatch rates | Not published for any mode | Not found | |
| Pipeline to Gauteng | 148,000 m3 a week for all shippers and products | Evidence | Transnet Pipelines, 24 inch trunk line |
| Monthly turns of operational capacity | Low 1; base 2; high 3 | Evidence of intent | Vopak told NERSA it was "targeting 2-3 throughputs in Durban"; a target, not a realised rate |

Annual handling for petrol and diesel on these assumptions: 1.75, 3.5 and 5.25
million m3. The pack's current sensitivity applies 1, 2 and 3 turns to the
gross 360,246 m3, giving 4.3, 8.6 and 13.0, which counts chemical and other
tanks as fuel capacity.

The high case needs 438,000 m3 a month, which is 68% of the whole trunk line
if it all went inland by pipeline. Vopak's share of pipeline capacity is not
published, so the high case holds only if a large part leaves by road, rail or
sea, or if Vopak holds most of the line.

Fuel may also be held in Durban's older tanks. Those are not counted, so
162,000 m3 is a floor for fuel-compatible capacity, not a measured total.

## Counting

Product moved from Durban to Lesedi by pipeline is handled at both sites.
Unique deliveries to customers are Lesedi's dispatch plus Durban's dispatch to
destinations other than Lesedi. The two sites' figures above must not be
added.

## Other sites in the inventory

No site-specific evidence was found for the Bidvest, VTTI, Sasol or Transnet
sites in `pptx/story/storage_operator_inventory_2026_10_06.csv`. They keep the
generic 1, 2 and 3 turns in `terminal_handling.yaml`. Sasol and Transnet
capacities are still unquantified.

## Still needed from Vopak

| Item | Why |
|---|---|
| Twelve months of outbound volume by site, product and mode | Realised turns and seasonality; replaces every turns estimate above |
| Operational capacity of the two new Lesedi tanks and of Durban's fuel tanks | Replaces two estimates |
| Fuel held in Durban's older tanks, and tank occupancy | Fuel-compatible capacity is a floor today |
| Durban berth, pipeline, rail and road rates; loading hours at Lesedi | Receipt and dispatch limits are unpublished or estimated |
| Volumes moved Durban to Lesedi | To remove the double count |
| Allocated pipeline capacity | Tests the Durban high case |

## Decisions for Nigel

1. Agree the provisional ranges: Lesedi 1 / 2 / 2.4 and Durban 1 / 2 / 3
   turns a month, on operational capacity.
2. Apply turns to operational, fuel-compatible capacity (124,000 and 146,000
   m3) instead of gross capacity (140,000 and 360,246 m3) on the pack's
   handling page.
3. Whether to ask Vopak for the items above now.
