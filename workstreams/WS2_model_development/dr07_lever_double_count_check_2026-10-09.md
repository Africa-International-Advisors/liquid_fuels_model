# DR07 levers: do any pairs count the same saving twice? 9 October 2026

For Nigel. Task 3 of `manish_next_steps_2026-10-09.md`.

**Short answer:** no pair is counted twice in the engine today, because only one lever
of each pair is wired into it. Two pairs will double-count if the second lever is added
without care. A test now pins the one combination the engine does make.

## How the engine works

`src/lfm/model/demand/vehicles.py` builds road fuel as

    vehicles in each cohort x kilometres a year x litres per 100 km

- **Electric share** removes vehicles: new petrol and diesel vehicles are new sales
  times (1 - electric share).
- **Efficiency** lowers litres per 100 km for each new cohort.
- Kilometres a year is one fixed figure per segment. There is no freight activity
  input, no rail input and no hybrid vehicle class.

## The three pairs

| Pair | In the engine today | Counted twice? | Risk when wired |
|---|---|---|---|
| Battery electric share and new-vehicle efficiency | Both wired. Multiplied: fuel is (1 - share) x efficiency factor | No | Low, see below |
| Hybrids and efficiency | Efficiency wired; hybrids not modelled | No | High |
| Road activity and rail diversion | Neither wired; kilometres are fixed | No | High |

### 1. Battery electric share and efficiency

The two act on different things, so the savings multiply and do not add. A 10% electric
share and a 10% efficiency gain save 19%, not 20%. Test:
`tests/test_vehicle_lever_combination.py`.

The remaining risk is in the efficiency figure itself. The observed history (8.8 to
7.4 litres per 100 km, 2005 to 2019, IEA) is an average over all new light vehicles,
electric and hybrid included. In South Africa those were under 0.1% of sales to 2019,
so the history is clean. Any forward rate taken from a country with many electric
vehicles would already hold part of the electric saving.

**Rule:** the efficiency lever is for petrol and diesel vehicles only.

### 2. Hybrids and efficiency

The lever sheet has conventional hybrids at 2 to 11% of new sales and plug-in hybrids
at 0.5 to 3.7% by 2035. The engine has no hybrid class, so hybrids can only enter
through the efficiency rate. If they are added that way while the efficiency lever is
also set from an all-vehicle average, the hybrid saving is counted twice.

Size: 11% of new cars using about 30% less fuel is 3.4% off the new cohort by 2035, or
about 0.3% a year. The efficiency cases are 0.25% a year apart, so this is as large as
the difference between two cases.

**Rule:** give hybrids their own term (share x saving per vehicle), multiplied in, and
keep the efficiency lever for conventional vehicles.

### 3. Road activity and rail diversion

The lever sheet has road activity at 95 to 150 (2024 = 100) and rail diversion at 0 to
13% by 2035. Both describe road freight diesel. If the road activity index is built
from road freight after rail has taken its share, taking rail diversion off again
counts the same tonnes twice.

The cases are also not independent. Transnet's target of 250 million tonnes (from 160)
is the source of the rail lever; the same recovery would lower road activity.

**Rule:** define road activity as freight demand on all modes, then apply rail diversion
once: road diesel = base x activity x (1 - diversion). Do not pair the high activity
case with the high diversion case without saying why.

## What is tested

`tests/test_vehicle_lever_combination.py` runs the engine four ways (neither lever,
electric only, efficiency only, both) and checks that fuel with both equals
(1 - electric share) x fuel with efficiency only. It fails if a later change makes the
two additive.

Hybrids and rail cannot be tested in the engine because they are not in it. The two
rules above are for whoever wires them.
