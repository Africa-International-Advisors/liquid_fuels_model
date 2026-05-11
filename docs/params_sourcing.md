# Provisional parameter sourcing log

This is the audit trail for parameters carried as **literature-range placeholders**
across the demand segments. The original xlsx fits demand at the product level
(gasoline / diesel / jet); the rebuild uses a segment-axis decomposition
(vehicles / aviation / generation / industrial / marine / agriculture) which
needs parameters the xlsx never recorded.

Two segments — vehicles and the three HELD segments (industrial / marine /
agriculture) — carry placeholder values flagged `provisional: true`.
Aviation, generation, and the macro layer are sourced from the xlsx and
verified against it (see `scripts/verify_against_xlsx.py`).

## How to use this doc

For each parameter below:

1. Source the value from the candidate sources listed (or another authoritative
   source — note it in the table).
2. Update the corresponding entry in `assumptions/2026/vehicles.yaml`.
3. Set `provisional: false` and fill in `last_updated:` and `source:` on that
   entry. Move the parameter's row in the **Status** table here from PROVISIONAL
   to VERIFIED.
4. Re-run `python scripts/verify_against_xlsx.py` (it should still pass — these
   parameters aren't in the xlsx, but verifier shouldn't regress) and re-run
   `pytest`.

Once all six parameters are VERIFIED for ZAF, the segment outputs can be considered
decision-grade and the "PROVISIONAL" banner can be dropped from any model output.

BLNS values stay null until a separate sourcing pass for those countries.

## Granularity

All six parameters are split by **three vehicle segments**:

| Code | Name | Notes |
|---|---|---|
| `passenger` | Passenger LDV | Cars, SUVs, smaller bakkies driven personally |
| `lcv` | Light commercial | Working bakkies, small delivery vans up to ~3.5t GVM |
| `hcv` | Heavy commercial | Trucks above 3.5t GVM, including buses |

Per-country values land in `by_country.<ISO3>.<segment>` slots already laid out
in the YAML.

---

## 1. `annual_km_per_vehicle`

Average distance each vehicle of a given segment travels per year, used together
with `fuel_consumption` to derive total fuel burnt.

**Why it matters:** drives the per-vehicle fuel-burn calc end-to-end. Halve the
km, halve the fuel demand for that segment.

**Provisional values (ZAF)** — placeholders sufficient for engine implementation,
not for decisions:

| Segment | Provisional (km/yr) | Literature range |
|---|---|---|
| passenger | 17,000 | 15,000–20,000 |
| lcv       | 28,000 | 25,000–35,000 |
| hcv       | 70,000 | 50,000+ (varies enormously by haul type) |

**Candidate authoritative sources** (priority order):

1. **eNaTIS** — odometer reading queries on de-registered vehicles by segment.
   The cleanest empirical signal but access-controlled.
2. **GreenCape** sector reports (transport / mobility) — they publish SA-specific
   averages periodically.
3. **NAAMSA** statistical guide — fleet-utilisation summary tables.
4. **IEA Mobility Model (MoMo)** — international benchmark, less SA-specific
   but widely used for cross-country comparability.

---

## 2. `fuel_consumption`

Litres per 100 km, by segment and powertrain (`ice_petrol`, `ice_diesel`).
HCV petrol is intentionally null — heavy commercial vehicles are essentially
all diesel in SACU.

**Why it matters:** with `annual_km`, this is the second multiplier turning
vehicle stock into fuel volume.

**Provisional values (ZAF)**:

| Segment | Petrol (L/100km) | Diesel (L/100km) | Notes |
|---|---|---|---|
| passenger | 9.5 | 7.5 | SA fleet runs higher than EU due to age and SUV/bakkie skew |
| lcv       | 10.5 | 9.0 | LCV petrol assumes light bakkies; LCV diesel covers working vans/bakkies |
| hcv       | — | 35.0 | Heavy trucks; ranges 25–50 depending on haul, load factor |

**Interaction with the xlsx (locked):** the values here are the BASELINE for
new-sale entries. `efficiency_improvement_diesel/gasoline` annual paths apply
to new entries only — each cohort's L/100km is fixed at year-of-manufacture
baseline × cumulative efficiency improvement, then held for that cohort's life.
Fleet-average L/100km in a given year is a stock-weighted sum across cohorts.
Implies the vehicles compute must track vehicle stock by cohort (year of first
registration), not as a single bulk number.

**Candidate authoritative sources:**

1. **DMRE / DoE** Energy Balances + Vehicle Statistics — fleet-average L/100km
   often derived backward from total fuel sales / fleet size.
2. **IEA MoMo** — consumption by vehicle class.
3. **OEM published values** weighted by NAAMSA segment sales-mix — bottom-up
   approach if the team has time for it.
4. **GreenCape** — sector reports occasionally publish SA-specific averages.

---

## 3. `petrol_diesel_split`

Fraction of new ICE sales that are petrol vs diesel, per segment. Used to
allocate the new-vehicle stream from `new_vehicle_regression` between petrol
and diesel before applying consumption.

**Why it matters:** without this, you can't go from "X new vehicles per year"
to "Y litres of gasoline + Z litres of diesel."

**Provisional values (ZAF)**:

| Segment | Petrol | Diesel |
|---|---|---|
| passenger | 0.83 | 0.17 |
| lcv       | 0.30 | 0.70 |
| hcv       | 0.00 | 1.00 |

These are forward-looking new-sale shares, not stock shares. They likely drift
over time as buyer preferences shift and emissions rules tighten — for v1 we
hold them flat. A future enhancement is a per-year split.

**Candidate authoritative sources:**

1. **NAAMSA** monthly new-vehicle sales reports — split by fuel type and
   segment. The authoritative source.
2. **eNaTIS** new-registration data as a cross-check.

---

## 4. `scrappage_rate`

Flat annual fraction of fleet retired, per segment. v1 simplification of what
is properly an age-survival curve.

**Why it matters:** the xlsx's biggest known limitation is omitting scrappage
entirely (the methodology note flags this), which causes fleet size to grow
unboundedly. Even a flat rate fixes the bias direction.

**Provisional values (ZAF)**:

| Segment | Provisional | Literature range |
|---|---|---|
| passenger | 0.04 | 0.03–0.05 (SA fleet older than EU/US) |
| lcv       | 0.05 | 0.04–0.06 |
| hcv       | 0.06 | 0.05–0.07 (commercial assets retire faster, but SA HCV fleet is also old) |

**Future upgrade (post-v1):** replace the flat rate with a Weibull/logistic
survival function parameterised by median fleet life and a shape parameter,
applied to age cohorts. Out of scope for v1 but the YAML schema can absorb it
when it lands (`scrappage_rate.curve: weibull` with curve params).

**Candidate authoritative sources:**

1. **eNaTIS** deregistration counts by year of first registration — gives the
   age-retirement empirical curve directly.
2. **Academic papers** on SA vehicle-stock turnover — a few solid ones exist
   (search "South Africa vehicle scrappage" / "fleet turnover") for parameter
   estimates.

---

## 5. `new_vehicle_segment_split`

Fraction of total new-vehicle demand falling into each segment. The xlsx's
new-vehicle regression yields a *total* number; we split that into passenger /
LCV / HCV to apply per-segment consumption.

**Why it matters:** without this, the segment decomposition can't be driven
from the new-vehicle regression — the regression gives "X total vehicles," we
need to know how those split.

**Provisional values (ZAF)**:

| Segment | Provisional |
|---|---|
| passenger | 0.78 |
| lcv       | 0.18 |
| hcv       | 0.04 |

**Candidate authoritative sources:**

1. **NAAMSA** annual sales summary — historical share by segment.
2. **eNaTIS** new-registration database — same cut.

A future enhancement could let this share evolve over time (e.g. as
e-commerce drives LCV growth); v1 holds it flat.

---

## Status

Update this table as parameters get sourced. PROVISIONAL = literature
placeholder; SOURCED = real value from a named source but not yet sanity-checked
by the team; VERIFIED = sourced + reviewed and signed off.

### Vehicles segment

| # | Parameter | ZAF | BWA | LSO | NAM | SWZ | Notes |
|---|---|---|---|---|---|---|---|
| V1 | `annual_km_per_vehicle`    | PROVISIONAL | — | — | — | — | |
| V2 | `fuel_consumption`         | PROVISIONAL | — | — | — | — | |
| V3 | `petrol_diesel_split`      | PROVISIONAL | — | — | — | — | |
| V4 | `scrappage_rate`           | PROVISIONAL | — | — | — | — | |
| V5 | `new_vehicle_segment_split`| PROVISIONAL | — | — | — | — | |

### HELD segments (industrial / marine / agriculture)

These segments compute demand as `base_year_volume × (gdp_pc(t) / gdp_pc(base))^elasticity`,
so each needs at minimum a sourced base-year volume and a sourced elasticity.

| # | Parameter | ZAF | BWA | LSO | NAM | SWZ | Notes |
|---|---|---|---|---|---|---|---|
| I1 | industrial `base_year_volume` | PROVISIONAL | — | — | — | — | derived as residual of xlsx total diesel; needs DMRE / sector reports |
| I2 | industrial `elasticity` (vs GDP/capita) | PROVISIONAL | — | — | — | — | placeholder ~1.0 |
| M1 | marine `base_year_volume` (per port) | PROVISIONAL | — | — | PROVISIONAL (Walvis Bay, Lüderitz) | — | bunker volume by port; Transnet, Namport, IBIA reports |
| M2 | marine `elasticity` | PROVISIONAL | — | — | PROVISIONAL | — | low (~0.4) since marine doesn't track national GDP |
| M3 | marine `product_split` | PROVISIONAL | — | — | PROVISIONAL | — | post-IMO 2020 fuel oil ↔ marine gasoil mix |
| A1 | agriculture `base_year_volume` | PROVISIONAL | — | — | — | — | DAFF/DALRRD energy use studies |
| A2 | agriculture `elasticity` | PROVISIONAL | — | — | — | — | low (~0.2) — driver should be hectares planted |

### Macro inputs (gating BLNS expansion)

| # | Parameter | Status | Notes |
|---|---|---|---|
| MA1 | `gdp_per_capita` for BWA / LSO / NAM / SWZ | NOT SOURCED | currently only ZAF in `timeseries/gdp_per_capita.csv`. Sourcing this unlocks every HELD segment for BLNS. Marine NAM ports already wired in YAML — they'll start emitting automatically once NAM macro lands. |

When all PROVISIONAL rows for ZAF reach VERIFIED, the v1 ZAF model output is
decision-grade for petrol / diesel / jet. The macro-layer BLNS sourcing is
the single biggest unlock for SACU-wide output.
