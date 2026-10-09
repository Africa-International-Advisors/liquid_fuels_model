# DR07 Demand evidence, 8 October 2026

For Nigel's review. Answers request DR07: the evidence that calibrates the
demand levers. Petrol and diesel only.

Status: **51 facts read from sources, 10 calculated, 7 not available.**

**Where to look:** the workbook `output/delivered/Demand_baseline_workshop_2026_10_08_history.xlsx`.

- Sheet **DR07 evidence**: every fact with its source and open gap.
- Sheet **DR07 power diesel**: Eskom's reported litres beside its generation.
- Sheet **DR07 fleet by province**: registered vehicles by province and class,
  and petrol and diesel vehicles by province.
- Sheet **DR07 efficiency and rail**: new-vehicle fuel use 2005 to 2019, and
  Transnet's rail volumes 2018 to 2025.

Table behind the first sheet: `dr07_demand_evidence_2026-10-08.csv`, rebuilt by
`python -m lfm.scripts.build_dr07_demand_evidence --vintage 2026`.

## Reported Eskom diesel litres

Eskom reports the fuel burned at its turbines as one total, not by station.
Years to 31 March:

| Year to March | Eskom fuel burned, bn litres | Eskom generation, GWh | Litres per kWh | Independent plants, GWh | Independent plants, bn litres (estimated) | Total, bn litres |
|---|---|---|---|---|---|---|
| 2023 | 0.94 | 3,018 | 0.311 | 1,098 | 0.34 | 1.28 |
| 2024 | 1.13 | 3,634 | 0.311 | 1,509 | 0.47 | 1.60 |
| 2025 | 0.68 | 2,176 | 0.312 | 662 | 0.21 | 0.88 |

Source: Eskom Integrated Report 2025, PDF p.141, checked against the page.
The sheet has all ten years, 2016 to 2025.

- Reported litres over reported generation gives 0.311 to 0.312 litres per
  kWh, which confirms the 0.31 used on the Power fleet sheet.
- Eskom reports diesel and kerosene together. Two of its four stations burn
  kerosene, but they are 342 of 2,426 MW, so nearly all of it is diesel.
- Avon and Dedisa do not report litres; theirs are estimated from generation.

## Plant commissioning and shutdown

From the system operator's Medium-Term System Adequacy Outlook 2026-2030
(30 October 2025):

| Event | When | Size |
|---|---|---|
| Dedisa and Avon contracts expire | August and September 2030 | 1.01 GW |
| Acacia and Port Rex shut down | 2030 | 0.34 GW |
| Coal units shut down | 2029 | 5.26 GW |
| Coal units shut down | By March 2030 | 3.14 GW |
| New gas plant assumed commercial (3 GW Eskom, 3 GW independent) | 2030 | 6 GW |

The outlook expects the diesel turbines to run little (below 6% in most
cases), more in 2029, and much more in 2030 if the gas plant is late.

**Input changed on this evidence.** `power_fleet_diesel.csv` had Avon's
agreement ending in July 2031, which I had worked out from its start date.
The system operator states both contracts end in 2030, so Avon's last full
year is now 2029. Effect: the low power case for 2030 falls from 86 to 20
million litres. The medium and high cases do not change.

## Coal station shutdown dates

| Stations | Date | Source |
|---|---|---|
| Komati | Shut down October 2022 | Eskom, coal-fired power stations page |
| Camden, Hendrina, Grootvlei, Arnot, Kriel | By 31 March 2030; run to the end of 2028, then phased from 2029 | Eskom Integrated Report 2025; system operator outlook |
| Duvha | February 2034 | System operator outlook, PDF p.19 |
| Matla | July 2034 | Same |
| Tutuka | "Scheduled for closure by 2030" under Eskom's Generation 2035 plan | Eskom, coal-fired power stations page; possibly an older plan |
| Kendal, Lethabo, Majuba, Matimba, Medupi | No shutdown date; emissions exemption to 31 March 2030 | System operator outlook |

Eskom's own reports give the dates by group, not by station. The station dates
for Duvha and Matla come from the system operator, which is an Eskom company.
Eskom's 2022 plan was nine stations, about 22 GW, by 2035; the delays since
then have not been restated station by station.

## Vehicle efficiency history

Average fuel use of new cars and light commercial vehicles, litres of petrol
equivalent per 100 km (IEA and Global Fuel Economy Initiative):

| 2005 | 2008 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2019 |
|---|---|---|---|---|---|---|---|---|
| 8.8 | 8.6 | 8.6 | 8.2 | 7.9 | 7.7 | 7.8 | 7.8 | 7.4 |

The IEA states a fall of 1.3% a year from 2005 to 2019. The model assumes 0.5
to 1.5% a year, so the observed rate sits inside the model's range. Nothing
after 2019 was found, so the 2019 figure (7.4) is used for later years.

## Rail

Freight carried by Transnet Freight Rail, million tonnes, years to March
(Transnet annual results 2025):

| 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| 226.3 | 215.1 | 212.4 | 183.3 | 173.1 | 149.5 | 151.7 | 160.1 |

Transnet "aims to grow its capacity to handle 250 million tons". That is 90
million tonnes above 2025, about 9% of road freight tonnes. Not all of it
would come from road. Nigel pointed to this source in the 6 October check-in.

## Electric vehicles

1,088 battery electric vehicles were sold in 2025, 0.18% of new vehicles
(naamsa). The low, medium and high cases are benchmarked on other countries on
the HML response sheet. No South African forecast was found.

## Eight gaps searched on 8 October

| Gap | Result | Source |
|---|---|---|
| Diesel used by rail locomotives | **Found.** Transnet used 199 million litres of fuel in the year to March 2025, 69.2% of it for diesel traction: about 138 million litres, roughly 1% of diesel sales | Transnet Integrated Report 2025, PDF p.73 |
| Vehicles by fuel, by province | **Found.** Petrol and diesel vehicles for all nine provinces at December 2023; on the fleet sheet | Department of Transport, Transport Statistics Bulletin 2023, Table 2.8 |
| Vehicles by fuel within each class | Not published | The bulletin splits fuel by province; the register splits class by province |
| Fuel use of trucks | **Found for one year.** 17.3 to 51.6 litres per 100 km from the lightest to the heaviest class, 2010 fleet | Stone et al. (2018), already held |
| Fuel use of new vehicles after 2019 | Not found | The IEA's 2021 edition is the latest with South Africa |
| Road freight in tonne-kilometres | **Found for 2019 only.** All freight 446 bn tonne-km; rail-friendly 181; carried by rail 141; general freight rail should carry but does not, 30 | Havenga et al., SA-TIED road-to-rail strategy report |
| Road freight in tonne-kilometres, by year | Not published as numbers | The research group shows yearly charts only |
| Vehicles by age | **Average only.** 10.5 years in 2022, up from 9 years 4 months in 2014-2015 | Lightstone, April 2022. It sells the age profile; the register does not publish it |
| Gas plant dates by project | **Found, but no firm date exists.** Eskom's 3,000 MW Richards Bay plant was determined for connection "not beyond 2028"; the independent 2,000 MW round was issued in December 2023 with no bidder appointed. The system operator now assumes 2030 | NERSA reasons for decision, November 2024; gas programme site |
| Electric trucks and light commercial vehicles sold | Not published | naamsa reports by drivetrain, not segment (fourth-quarter 2025 review checked) |
| Private backup generator diesel | Not measured by anyone. A ceiling only: load-shedding was 10.6 TWh in 2023 and 2.5 in 2024, which at 0.31 litres per kWh is at most 3.3 and 0.8 bn litres | CSIR power statistics 2024. Reserve Bank, Eskom and the system operator checked; none gives litres |

The ceiling is not an estimate. Much of the electricity shed was replaced by
solar and batteries or not replaced at all.

## Gas plant by project (added 9 October)

No project has a firm commissioning date. What is published:

| Project | Size | Status | Date | Source |
|---|---|---|---|---|
| Eskom, Richards Bay | 3,000 MW | Gas supply agreement signed with Zululand Energy Terminal on 5 June 2026; environmental assessment to be redone | Eskom plans to produce from 2031 | Eskom statement; Engineering News, 5 June 2026 |
| Khanyazwe Flexpower (FlexED), Mpumalanga | 440 MW | Bid, 29 May 2026 | None | Official bid list |
| Pictor consortium, KwaZulu-Natal | 990 MW | Bid, 29 May 2026 | None | Official bid list |
| Kelvin Redevelopment, Gauteng | 600 MW | Bid, 29 May 2026 | None | Official bid list |
| Komatipoort Power (Vutomi Energy), Mpumalanga | 800 MW | Bid, 29 May 2026 | None | Official bid list |
| New determination | 5,000 MW | Announced 7 October 2026; bidding rounds to follow | None | Engineering News, 7 October 2026 |

The four bids total 2,830 MW against 2,000 MW sought. No preferred bidder had been named by 7 October 2026.
The programme allows more than a year to financial close and then 36 months to build, so on its own timetable no
plant from this round runs before about 2031 (my reading, not a published date). The system operator's outlook
assumes 6 GW of gas in 2030; nothing found supports that date.

Not found: any gas project for ACWA Power, the members of the Pictor consortium, or a dated gas conversion for Avon.

## Still not available

| What | Why |
|---|---|
| Diesel burned in private backup generators | No source measures it: checked the Reserve Bank, the CSIR, Eskom and the system operator. It is inside recorded diesel sales and cannot be separated. |
| New gas plant: firm commissioning date for any project | No project has a preferred bidder, financial close or construction start. See the gas plant table above. |
| Vehicles by fuel within each class | The bulletin splits fuel by province and the register splits class by province; nothing published crosses fuel with class. |
| Vehicles by year of age | Lightstone holds the age profile and sells it; the register does not publish it. Only apparent retirements can be calculated. |
| Electric trucks and electric light commercial vehicles sold | naamsa reports electric sales by drivetrain, not by segment (checked its fourth-quarter 2025 review). Benchmarks from other countries are on the HML response sheet. |
| Fuel use of trucks, by year | Only the 2010 fleet figures above exist. No truck series by year was found. |
| Road freight in tonne-kilometres, by year | The research group that models it (GAIN, Stellenbosch) shows yearly charts but publishes figures for single years only. |

## Checks

- The evidence table is rebuilt from registered inputs, and a test checks the
  committed file equals a fresh build and that every fact has a source.
- Eskom's ten fuel figures and every figure typed from a document were read
  against the page named.
- The provinces on the fleet sheet add to the national register (tested).
- FIASA and JODI are not used.
- `python -m pytest -q`: 233 passed, 1 skipped. The message on commit `1c5c64d` says 234; that is wrong.
- One input changed (Avon's last full year); the engine does not read it, so
  model results are unchanged.
