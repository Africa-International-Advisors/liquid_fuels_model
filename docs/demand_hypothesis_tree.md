# Demand hypothesis tree

McKinsey-style decomposition of "what drives demand" for each segment in the
SACU liquid fuels model. The tree exists to:

1. Make the structural commitments visible — at a glance, you can see whether
   a segment is bottom-up (deep tree) or driver-tied (shallow tree).
2. Audit which leaves are quantified vs guessed vs not-yet-modelled.
3. Identify sourcing priorities — provisional leaves that drive a lot of
   demand are where the next data hunt should go.

## Status tags

Every leaf is tagged:

- **[Q] quantified** — value lives in `assumptions/<vintage>/*.yaml` or a
  CSV under `timeseries/`, sourced from the xlsx (or whatever future provider
  takes over) and visible to `scripts/verify_against_xlsx.py`.
- **[P] provisional** — placeholder pending sourcing. Carries a
  `provisional: true` flag in the YAML; the `lfm run` PROVISIONAL banner
  lists every parameter still in this state. Sourcing log: `docs/params_sourcing.md`.
- **[N] not modelled** — declared in the tree for completeness; not a v1
  input. Either narrative-only (drivers behind drivers) or a v1 simplification
  that a future MODELLED upgrade would absorb.

## At-a-glance summary

| Segment | Status | [Q] | [P] | [N] | Tree depth |
|---|---|---:|---:|---:|---:|
| vehicles    | MODELLED | 7  | 5  | many | 5 |
| aviation    | MODELLED | 5  | 0  | 5    | 3 |
| generation  | MODELLED | 6  | 0  | 6    | 3 |
| industrial  | HELD     | 1  | 2  | many | 2 |
| marine      | HELD     | 1  | 7  | 5    | 3 |
| agriculture | HELD     | 1  | 2  | many | 2 |
| supply (sketch) | stub | 4  | 0  | —    | 2 |

The depth column is a proxy for "how richly modelled" a segment is. Industrial,
marine, and agriculture are intentionally shallow (HELD pattern). Vehicles is
the richest because the methodology required cohort tracking + scrappage +
S-curve composition.

---

## 0. Total ZAF liquid fuel demand

```
ZAF total liquid fuel demand (litres / year)
├── petrol_95          ← vehicles
├── diesel_50ppm       ← vehicles + generation + industrial + agriculture
├── jet_a1             ← aviation
├── fuel_oil           ← marine
└── diesel_500ppm      ← marine
```

History reconciliation (`scripts/compare_history.py`) compares this against
the xlsx's RSA Demand totals.

---

## 1. Vehicles (MODELLED)

```
ZAF vehicles fuel demand (litres / yr, split by petrol_95 / diesel_50ppm)
└── Σ over (segment × powertrain × cohort)[ICE stock × annual km × L/100km]
    ├── ICE stock by (segment, powertrain, cohort)
    │   ├── New ICE entries per year
    │   │   ├── Total new-vehicle demand
    │   │   │   ├── Regression on GDP/capita                  [Q] xlsx RegEV, R² 0.51
    │   │   │   │   ├── Slope (37.31)                         [Q]
    │   │   │   │   └── Intercept (-2,387,744)                [Q]
    │   │   │   └── GDP/capita driver                         [Q] xlsx scenario CSV
    │   │   │       ├── GDP path                              [Q] xlsx scenario CSV
    │   │   │       └── Population path                       [Q] xlsx scenario CSV
    │   │   ├── EV penetration share (1 - share = ICE share)
    │   │   │   ├── Logistic S-curve params (per scenario)
    │   │   │   │   ├── Max penetration (0.30 / 0.90)         [Q] xlsx
    │   │   │   │   ├── Midpoint year (2040 / 2036)           [Q] xlsx
    │   │   │   │   └── Slope (3 / 2)                         [Q] xlsx
    │   │   │   └── Underlying narrative drivers
    │   │   │       ├── Charging infrastructure rollout       [N]
    │   │   │       ├── EV price parity vs ICE                [N]
    │   │   │       ├── Policy / fleet mandates               [N]
    │   │   │       ├── Brand availability in SACU            [N]
    │   │   │       └── Grid reliability                      [N]
    │   │   ├── Segment split (passenger / LCV / HCV)         [P] placeholder
    │   │   └── Petrol/diesel split per segment               [P] placeholder
    │   └── Cohort scrappage
    │       ├── Annual flat rate per segment                  [P] placeholder
    │       └── Age-survival curve (Weibull/logistic)         [N] post-v1
    ├── Annual km per vehicle (per segment)                   [P] placeholder
    │   └── Underlying drivers
    │       ├── Fuel price (consumer substitution)            [N]
    │       ├── Congestion / urbanisation                     [N]
    │       └── Freight cycle intensity (HCV)                 [N]
    └── L/100km (per cohort × segment × powertrain)
        ├── Baseline at year of manufacture                   [P] placeholder
        │   └── Underlying drivers
        │       ├── Fleet age distribution                    [N]
        │       ├── SUV/bakkie skew vs sedans                 [N]
        │       └── OEM mix in SACU                           [N]
        └── Cumulative efficiency improvement                 [Q] xlsx scenario CSV
            └── Locked rule: applies to new-sale cohorts only
```

**Sourcing priorities for vehicles:** the five [P] leaves are the
decision-grade unlock. See `docs/params_sourcing.md` for candidate sources
(eNaTIS, NAAMSA, GreenCape, IEA MoMo, DMRE).

---

## 2. Aviation (MODELLED)

```
ZAF aviation fuel demand (litres / yr, jet_a1)
└── Two-variable regression: jet = intercept + b_gdp × GDP/cap + b_pax × pax_dep
    ├── Regression coefficients (xlsx fit, R² 0.946)
    │   ├── Intercept (-14,746,408,795.77)                    [Q] xlsx fJetFuel
    │   ├── GDP/capita coefficient (196,334.93)               [Q] xlsx fJetFuel
    │   └── Passenger departures coefficient (79.79)          [Q] xlsx fJetFuel
    ├── GDP/capita driver                                     [Q] xlsx scenario CSV
    └── Passenger departures driver                           [Q] stitched (xlsx)
        ├── Observed 2017-2024 (Jet-DS sheet)                 [Q]
        ├── Baseline forecast 2025-2050 (PaxBaseScenario)     [Q]
        └── Underlying narrative drivers
            ├── Inbound tourism                               [N]
            ├── Business travel                               [N]
            ├── Airline capacity / route availability         [N]
            ├── Aircraft fuel efficiency                      [N] absorbed in residual
            └── Freight (paraffin / avgas excluded)           [N]
```

**Known limitation:** the regression goes negative in pandemic-magnitude
years (2020 input gives ~-95M litres, clamped to 0). Out-of-distribution
input space, not a model bug.

---

## 3. Generation (MODELLED)

```
ZAF OCGT diesel demand (litres / yr, diesel_50ppm)
└── Σ stations[MW × hrs × load_factor] / efficiency × (3600 / MJ_per_L)
    ├── OCGT capacity (MW, operational fleet only in v1)
    │   ├── Ankerlig (1327)                                   [Q] xlsx PowerGen_Capacity
    │   ├── Gourikwa (740)                                    [Q]
    │   ├── Avon (670)                                        [Q]
    │   ├── Dedisa (335)                                      [Q]
    │   └── New 1, New 2 (notional 3000 MW)                   [N] no commissioning year
    ├── Operating hours (24 × 365)                            [Q] xlsx (Operational_days)
    ├── Load factor (per year × scenario)                     [Q] xlsx scenario CSV
    │   └── Underlying drivers
    │       ├── Eskom EAF (Energy Availability Factor)        [N]
    │       ├── Total system demand growth                    [N]
    │       ├── Renewables build-out pace                     [N]
    │       └── Transmission constraints                      [N]
    ├── Thermal efficiency (0.4)                              [Q] xlsx PowerGen_Efficiency
    │   └── Underlying drivers
    │       ├── Fleet age                                     [N]
    │       └── Maintenance regime                            [N]
    └── Diesel energy density (36.9 MJ/L)                     [Q] xlsx MJ_Litres_Conversion
```

**Out-of-scope additive term:** `LoadShedding_*` named ranges (xlsx) are
loaded into `generation.yaml` but unused — the units in the xlsx are
unclear and the load_factor already captures dispatched OCGT generation.

---

## 4. Industrial (HELD)

```
ZAF industrial diesel demand (litres / yr, diesel_50ppm)
└── base × (gdp_pc(t) / gdp_pc(base))^elasticity
    ├── Base-year volume (single aggregate bucket, ZAF 2024)  [P] 2.5 BL placeholder
    ├── GDP/capita ratio driver                               [Q] xlsx scenario CSV
    └── Elasticity (1.0)                                      [P] placeholder

Future MODELLED decomposition (sub-segments lumped in v1)
└── Sub-segments
    ├── Mining haul fleet                                     [N]
    │   ├── Tonnes mined by commodity (coal, iron, PGM)       [N]
    │   ├── Diesel L / tonne ore                              [N]
    │   └── Haul-truck fleet size & efficiency                [N]
    ├── Manufacturing                                         [N]
    │   ├── Industrial GVA (steel, cement, chemicals)         [N]
    │   └── Diesel L / ZAR output (energy intensity)          [N]
    ├── Construction equipment                                [N]
    └── Stationary engines (small industry, rural)            [N]
```

**Sourcing priorities:** just two numbers (base-year volume + elasticity)
unlock decision-grade industrial. Candidate sources: DMRE energy balances,
Minerals Council SA reports, Stats SA manufacturing energy series.

---

## 5. Marine (HELD)

```
ZAF + NAM marine bunkering (litres / yr, fuel_oil + diesel_500ppm)
└── Σ ports[base × (gdp_pc(t) / gdp_pc(base))^elasticity] × product_split
    ├── Per-port base-year volumes (2024)
    │   ├── Durban (ZAF)                                      [P] 1.5 BL placeholder
    │   ├── Cape Town (ZAF)                                   [P] 0.5 BL placeholder
    │   ├── Saldanha (ZAF)                                    [P] 0.2 BL placeholder
    │   ├── Walvis Bay (NAM)                                  [P] 0.25 BL — blocked on NAM GDP
    │   └── Lüderitz (NAM)                                    [P] 0.05 BL — blocked on NAM GDP
    ├── GDP/capita ratio driver (placeholder; should be trade)[Q] xlsx scenario CSV
    ├── Elasticity to GDP (0.4)                               [P] placeholder
    └── Product split (HFO / MGO)
        ├── Default split (0.65 / 0.35)                       [P] placeholder
        └── Underlying driver: IMO 2020 sulphur cap shift     [N]

Future MODELLED decomposition (real driver = global trade, not GDP)
└── Per-port:
    ├── Throughput driver
    │   ├── TEU throughput                                    [N]
    │   ├── DWT throughput (bulk / tankers)                   [N]
    │   └── Vessel call counts                                [N]
    ├── Bunker hub competitiveness (vs Singapore / Rotterdam) [N]
    └── Bunker price differential                             [N]
```

**Sourcing priorities:** per-port observed volumes (Transnet, Namport, IBIA
bunker reports) is the immediate gap. NAM GDP/capita is a separate unlock
that activates the NAM ports.

---

## 6. Agriculture (HELD)

```
ZAF agricultural diesel demand (litres / yr, diesel_50ppm)
└── base × (gdp_pc(t) / gdp_pc(base))^elasticity
    ├── Base-year volume (single aggregate bucket, ZAF 2024)  [P] 0.7 BL placeholder
    ├── GDP/capita ratio driver                               [Q] xlsx scenario CSV
    └── Elasticity (0.2 — low because GDP isn't the right driver) [P] placeholder

Future MODELLED decomposition (real driver = hectares planted)
└── Sub-segments
    ├── Field operations (planting / harvest)
    │   ├── Hectares planted (per crop)                       [N]
    │   ├── Tractor fuel L / ha                               [N]
    │   └── Harvester fuel L / ha                             [N]
    ├── Irrigation pumping
    │   ├── Hectares irrigated                                [N]
    │   ├── Pump diesel vs electric mix                       [N]
    │   └── Pumping intensity (m³ / ha)                       [N]
    ├── On-farm transport                                     [N]
    └── Diesel rebate policy (consumer-side incentive)        [N]
```

**Sourcing priorities:** same as industrial — two numbers (base + elasticity).
Candidate sources: DALRRD (Department of Agriculture) energy use studies,
SA Grain Information Service.

---

## 7. Supply (sketch only — out of v1 scope)

Included for completeness; the supply compute is a stub.

```
ZAF domestic supply (litres / yr, by product)
└── Σ refineries[capacity × utilisation × product_split] × fleet_availability
    ├── Refinery capacity (kbpd, per refinery)               [Q] xlsx Refinery_capacity
    ├── Utilisation (per refinery × year × scenario)         [Q] xlsx scenario CSV
    ├── Product split (per refinery)                         [Q] xlsx SupplyFuelMix
    └── Fleet availability factor (0.9)                      [Q] xlsx Refinery_availability

Then: Deficit = total demand - domestic supply
└── Cross-border flows (BLNS imports via SA terminals)        [N]
└── Storage decisions (Vopak's role)                          [N]
```

The refinery data is fully quantified — what's missing is the compute
function in `src/lfm/supply/flows.py`. Implementing that closes the
demand-supply loop and produces the deficit/imports headline that
stakeholders consume.

---

## How to use this doc

When sourcing lands a real value:

1. Replace the [P] in the relevant YAML with the sourced value.
2. Set `provisional: false`, fill in `last_updated:` and `source:`.
3. Update this tree's tag from [P] to [Q] for that leaf.
4. Update the **At-a-glance** count at the top.
5. Re-run `pytest`, `verify_against_xlsx.py`, and `compare_history.py`.

When a segment graduates from HELD to MODELLED (e.g., industrial gets
sub-segment data):

1. Build the sub-segment compute in the segment's `.py` file.
2. Update the YAML schema to carry the new sub-segment inputs.
3. Update the tree here — the [N] sub-segment leaves become real branches.
4. Bump the segment status in `demand/__init__.py` and the segment file.
