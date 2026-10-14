"""Petrol and diesel demand outlook to 2030 for the market of interest (six provinces), Low / Base / High demand cases.

Starting point: market of interest 2025E (moi_2025.json from s13_2025.py: 2022 district shares x 2025 national demand), split into
uses with the analytical workbook v02's 2025 segments (national), scaled to the market of interest. Power is placed by location:
Avon (KZN) is the only diesel peaker in the area.
Drivers (Henry Gilfillan, 13 October 2026; Manish Ramjeawon, 14 October 2026):
  GDP: flat 1.0 / 2.0 / 3.0% a year (IMF Oct 2026 for 2026 / Treasury 2026 Budget Review / MTDP 3% target). Diesel non-power uses grow
    1:1 with GDP; petrol grows 0.36% per 1% of GDP (Akinboade, Ziramba and Kumo 2008).
  Petrol price: real price index vs 2025 (2026 = Jan-Oct actual, Nov-Dec at October, less 3.4% CPI = +14.8%). Low holds it; base eases
    back to 2025 by 2030; high mirrors low (1/1.148 by 2030). Long-run elasticity -0.47, ~40% felt per year (Brons et al. 2008).
  Efficiency (road fleet, p9 of the pack): petrol 0.8 / 0.65 / 0.5% a year; diesel 0.7 / 0.55 / 0.4% (Low / Base / High demand).
  EVs: logistic S-curves of EV share of new light-vehicle sales (High demand: ceiling 30%, midpoint 2040, slope 3; Low demand: 90%, 2036,
    2; Base = average); new sales grow with GDP from eNaTIS 2025; fleet grows 1.95% a year (eNaTIS 2023-25); new vehicles drive 1.45x the
    fleet average (Stone et al. 2018). Displaces road petrol and light-vehicle diesel.
  Rail: road freight moved to rail against 2025 mode shares, phased evenly to 2030; rail 262 / 250 / 215m t (rail master plan / Transnet
    target / 5% a year). Rail's own diesel is excluded (REBOUND = 0; evidence ~17.5% computed for reference).
  Peakers: Avon diesel = 670 MW x load factor x 8 760 h x 0.31 L/kWh; load factor 1.4% (Eskom turbines, 1 Apr-8 Oct 2026) / 4.5% /
    10%, phased evenly to 2030.
  Backup generators: excluded (no published installed capacity; PRIV = 0).
Usage: python moi_forecast.py REPO_ROOT OUT.json
"""
import collections, csv, json, math, sys
from pathlib import Path

REPO, OUT = Path(sys.argv[1]), Path(sys.argv[2])
HERE = Path(__file__).parent
rows = lambda rel: list(csv.DictReader(open(REPO / rel, encoding="utf-8-sig", newline="")))
M = json.loads((HERE / "moi_2025.json").read_text(encoding="utf-8"))
an = json.loads((REPO / "output/delivered/sa_analytics_2026_10_11_v02/analytics.json").read_text(encoding="utf-8"))
seg = {r[0]: r[3]["value"] for r in an["sheets"]["Segments"]["rows"] if isinstance(r, list) and r and isinstance(r[3], dict)}
A = {r[0]: r[1] for r in an["sheets"]["Assumptions"]["rows"] if isinstance(r, list) and r and not isinstance(r[1], dict)}
ev = {r[0]: r[1] for r in an["sheets"]["Evidence"]["rows"] if isinstance(r, list) and r}
nat = M["national"]                                                 # 2025 national demand, production + imports - exports
moi_p, moi_d = M["moi"]["petrol"], M["moi"]["diesel"]
sh_p, sh_d = moi_p / nat["petrol"], moi_d / nat["diesel"]

# ---- 2025 uses, national (workbook) ----
pet_road_n, pet_oth_n = seg["Petrol road use"], seg["Other petrol"]
pet_unal_n = nat["petrol"] - pet_road_n - pet_oth_n
D = {"freight": seg["Road freight diesel"], "light": seg["Other road diesel"], "mining": seg["Mining"], "agri": seg["Agriculture"],
     "manuf": seg["Manufacturing"], "other": seg["Other diesel / unallocated"]}
power_n = seg["Utility and private power"]
D["unal"] = nat["diesel"] - sum(D.values()) - power_n
LPK = 0.31                                                          # L/kWh; Eskom FY2024 and FY2025 ratios both 0.31
assert abs(1129.5 / 3634 - LPK) < 0.005 and abs(679 / 2176 - LPK) < 0.005
AVON_MW, IPP_MW = 670, 670 + 335
avon25 = ev["ipp_gwh_2025"] * AVON_MW / IPP_MW * LPK / 1000        # bn L
priv25_n = 0.0                                                      # backup generators removed (user, 14 October 2026): no reputable
                                                                    # installed-capacity source; 2025 diesel stays in general use
moi_power25 = avon25 + priv25_n * sh_d
nonpower_n = sum(D.values())
nonpower_moi = moi_d - moi_power25
base = {"petrol_road": pet_road_n * sh_p, "petrol_other": pet_oth_n * sh_p, "petrol_unal": pet_unal_n * sh_p}
base.update({f"diesel_{k}": v / nonpower_n * nonpower_moi for k, v in D.items()})
base["diesel_avon"], base["diesel_private"] = avon25, priv25_n * sh_d
assert abs(sum(v for k, v in base.items() if k.startswith("petrol")) - moi_p) < 1e-9
assert abs(sum(v for k, v in base.items() if k.startswith("diesel")) - moi_d) < 1e-9

# ---- 1 peakers: load factors ----
LF_THIS = 152 / (191 / 365) / (2426 * 8.76)                        # Eskom turbines (diesel + kerosene, 2 426 MW), 1 Apr-8 Oct 2026 (p6)
LF = {"Low": LF_THIS, "Base": 0.045, "High": 0.10}
# ---- 2 private generators (national bn L in 2030) ----
PRIV = {"Low": 0.0, "Base": 0.0, "High": 0.0}                     # removed: no reputable source (WITS/Comtrade gives unit counts only)
# ---- 3 rail ----
road25, rail25 = ev["freight_road_2025"], ev["freight_rail_2025"]
GDP = [0.016, 0.018, 0.020, 0.020, 0.020]                          # Treasury, 2026 Budget Review Table 2.2 (2029-30 held)
tot30 = (road25 + rail25) * math.prod(1 + g for g in GDP)
rail_cs = tot30 * rail25 / (road25 + rail25)                        # rail at its 2025 share
road_cs = tot30 - rail_cs
RAIL30 = {"Low": 262.0, "Base": 250.0, "High": rail25 * 1.05 ** 5}
SHIFT = {k: (v - rail_cs) / road_cs for k, v in RAIL30.items()}
road_lpt = seg["Road freight diesel"] * 1e3 / road25
rail_lpt = 105 * 2 * 0.692 / 167.9                                  # Transnet: 105 ML in 6 months to Sep 2025; traction 69.2% (FY2025); 167.9m t
REBOUND_EVIDENCE = rail_lpt / road_lpt                              # about 17.5%; reported only
REBOUND = 0.0                                                       # rail's own diesel excluded (user, 14 October 2026); evidence ~17.5% kept above
# ---- 4 EVs ----
SC = {"High": (0.30, 2040, 3), "Low": (0.90, 2036, 2)}
pen = lambda c, t: c[0] / (1 + math.exp((c[1] - t) / c[2]))
P = collections.defaultdict(float)
for r in rows("assumptions/2026/timeseries/vehicle_population_natis.csv"):
    if r["period"] == "2025-12" and r["province"] != "ZAF" and r["vehicle_class"] in ("cars", "light_commercial"):
        P["parc"] += float(r["value"])
newlv = sum(float(r["value"]) for r in rows("assumptions/2026/timeseries/new_vehicle_registrations_natis_annual.csv")
            if r["period"] == "2025" and r["vehicle_class"] in ("cars", "light_commercial"))
st = {r["vehicle_type"]: r for r in rows("assumptions/2026/reference/vehicle_parameters_stone2018.csv")}
KMF = float(st["CarGasoline"]["km_per_year_new"]) / float(st["CarGasoline"]["km_per_year_fleet_average"])   # new cars drive more
EFF = {"Low": (0.008, 0.007), "Base": (0.0065, 0.0055), "High": (0.005, 0.004)}
ACT = {"Low": 0.005, "Base": 0.015, "High": 0.025}                 # superseded by GDP paths below (user, 14 October 2026); kept for reference
YEARS = list(range(2025, 2031))
# ---- GDP and petrol price (user, 14 October 2026) ----
GDPP = {"Low": [0.010] * 5,                                        # IMF WEO October 2026: 1.0% for 2026, held (symmetric around base)
        "Base": [0.020] * 5,                                       # National Treasury, 2026 Budget Review Table 2.2: 2.0% by 2028
        "High": [0.030] * 5}                                       # MTDP 2024-2029 target: 3%
                                                                    # flat at the higher target in each case (user, 14 October 2026)
INC_PETROL, PRICE_EL = 0.36, -0.47                                  # Akinboade, Ziramba and Kumo (2008), Energy Economics: SA petrol demand
INC_DIESEL = 1.0                                                    # diesel grows in line with GDP (Henry Gilfillan, 13 October 2026)
pr = {r["period"]: float(r["value"]) for r in rows("assumptions/2026/timeseries/fuel_prices_department.csv") if r["series"] == "petrol_95_inland_retail"}
p25 = sum(pr[f"2025-{m:02d}"] for m in range(1, 13)) / 12
p26 = (sum(pr[f"2026-{m:02d}"] for m in range(1, 11)) + 2 * pr["2026-10"]) / 12      # Nov-Dec 2026 held at October
CPI26 = 0.034                                                       # Treasury 2026 Budget Review Table 2.2
r26, roct = p26 / p25 / (1 + CPI26), pr["2026-10"] / p25 / (1 + CPI26)               # real price relative to 2025
ease = lambda n: [1, r26] + [r26 + (1 - r26) * min(k / n, 1) for k in range(1, 5)]   # real price eases back to 2025 over n years
PRICE = {"Low": [1, r26, r26, r26, r26, r26],                       # stays at the 2026 average, in real terms
         "Base": ease(4),                                           # back to the 2025 level by 2030
         "High": [1, r26] + [r26 + (1 / r26 - r26) * k / 4 for k in range(1, 5)]}   # mirror of low: 1/1.15 of 2025 by 2030 (user, 14 Oct 2026)


ADJ = 0.34 / 0.84                                                   # share of the long-run price effect felt within a year
                                                                    # (Brons et al. 2008 meta-analysis: short run -0.34, long run -0.84)


def run(case):
    g, (ep, ed), shift = ACT[case], EFF[case], SHIFT[case]
    out = {}
    pe = [0.0]                                                      # log price effect, adjusting gradually to its long-run level
    for i in range(1, len(YEARS)):
        pe.append(pe[-1] + ADJ * (PRICE_EL * math.log(PRICE[case][i]) - pe[-1]))
    cum_ev, parc = 0.0, P["parc"]
    for i, y in enumerate(YEARS):
        if y > 2025:
            sales = newlv * math.prod(1 + x for x in GDPP[case][:i])
            p = (pen(SC["Low"], y) + pen(SC["High"], y)) / 2 if case == "Base" else pen(SC[case], y)
            cum_ev += sales * p
            parc *= 1.0195                                         # eNaTIS 2023-25 net growth of cars + LCVs
        evd = cum_ev / parc * KMF                                   # share of light-vehicle fuel displaced
        gp = GDPP[case][:i]
        a = math.prod(1 + INC_DIESEL * x for x in gp)               # diesel activity
        ap = math.prod(1 + INC_PETROL * x for x in gp) * math.exp(pe[i])             # petrol: income and (phased) price
        f = i / 5                                                   # rail shift and power ramp linearly to 2030
        v = {"petrol_road": base["petrol_road"] * ap * (1 - ep) ** i * (1 - evd),
             "petrol_other": base["petrol_other"] * ap, "petrol_unal": base["petrol_unal"] * ap,
             "diesel_freight": base["diesel_freight"] * a * (1 - ed) ** i * (1 - shift * f * (1 - REBOUND)),
             "diesel_light": base["diesel_light"] * a * (1 - ed) ** i * (1 - evd)}
        for k in ("mining", "agri", "manuf", "other", "unal"):
            v[f"diesel_{k}"] = base[f"diesel_{k}"] * a
        avon30 = AVON_MW * LF[case] * 8.76 * LPK / 1000
        v["diesel_avon"] = base["diesel_avon"] + (avon30 - base["diesel_avon"]) * f
        v["diesel_private"] = base["diesel_private"] + (PRIV[case] * sh_d - base["diesel_private"]) * f
        out[y] = {"petrol": sum(x for k, x in v.items() if k.startswith("petrol")), "diesel": sum(x for k, x in v.items() if k.startswith("diesel")),
                  "parts": v, "ev_fleet_share": cum_ev / parc}
    return out


res = {c: run(c) for c in ("Low", "Base", "High")}
inside = M["inside"]["petrol"] + M["inside"]["diesel"]
print(f"MOI shares petrol {sh_p:.1%} diesel {sh_d:.1%} | MOI power 2025 {moi_power25:.3f} (Avon {avon25:.3f}) | this year's LF {LF_THIS:.2%}")
print(f"rail: const-share 2030 {rail_cs:.1f} Mt; shifts { {k: round(v, 4) for k, v in SHIFT.items()} }; Nigel 15% -> {rail_cs + 0.15 * road_cs:.0f} Mt, "
      f"7.5% -> {rail_cs + 0.075 * road_cs:.0f} Mt | rebound {REBOUND:.1%} | KMF {KMF:.2f}")
for c, r in res.items():
    y = r[2030]
    print(f"{c}: 2030 petrol {y['petrol']:.2f} diesel {y['diesel']:.2f} total {y['petrol'] + y['diesel']:.2f} | EV fleet {y['ev_fleet_share']:.2%} | "
          f"import need {y['petrol'] + y['diesel'] - inside:.2f}")
json.dump({"years": YEARS, "base2025": base, "shares": {"petrol": sh_p, "diesel": sh_d}, "inside": inside,
           "assumptions": {"gdp": GDPP, "petrol_income_el": INC_PETROL, "petrol_price_el": PRICE_EL, "price_index": PRICE,
                           "p25": p25, "p26": p26, "poct": pr["2026-10"], "efficiency": EFF, "rail_2030_mt": RAIL30, "rail_shift": SHIFT, "rebound": REBOUND,
                           "ev_curves": SC, "load_factor": LF, "private_national_bn": PRIV, "lpk": LPK, "avon_mw": AVON_MW,
                           "rail_const_share_2030": rail_cs, "road_const_share_2030": road_cs, "lf_this_year": LF_THIS},
           "cases": {c: {str(y): {k: v for k, v in d.items() if k != "parts"} | {"parts": d["parts"]} for y, d in r.items()} for c, r in res.items()}},
          open(OUT, "w", encoding="utf-8"), indent=1)
print("saved", OUT)
