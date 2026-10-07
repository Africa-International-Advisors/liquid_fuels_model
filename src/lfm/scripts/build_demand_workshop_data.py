"""Export current-engine evidence for the demand-method workshop workbook."""
import csv
import hashlib
import json
import subprocess
from pathlib import Path
import pandas as pd

from lfm.assumptions import YamlDirectoryProvider
from lfm.assumptions.snapshot import SnapshotProvider
from lfm.config import Paths
from lfm.model.demand import agriculture, aviation, generation, industrial, marine, vehicles
from lfm.run import Run


def main():
    paths = Paths.default()
    root = paths.repo_root
    out = root / "output" / "workshop_2026_10_07"
    out.mkdir(parents=True, exist_ok=True)
    run = Run(vintage="2026", scenario="high_demand")
    provider = SnapshotProvider(YamlDirectoryProvider(paths), run)
    diagnostics = []
    vehicle = vehicles.compute_country_annual(provider, run, "ZAF", start_year=2022, diagnostics=diagnostics)
    agri = agriculture.compute_country_annual(provider, run, "ZAF", start_year=2022)
    industry = industrial.compute_country_annual(provider, run, "ZAF", start_year=2022)
    years = list(range(2022, 2036))
    def values(domain, key):
        return provider.get(domain, key, run).value
    def series(domain, key):
        df = values(domain, key)
        df = df[df.country == "ZAF"]
        return {int(row.period): float(row.value) for row in df.itertuples()}
    result = {
        "years": years, "scenario": run.scenario, "vintage": run.vintage,
        "executed_at": run.executed_at.isoformat(),
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "diagnostics": [d for d in diagnostics if d["year"] in years],
        "vehicle": {int(y): {k: float(v) for k, v in row.items()} for y, row in vehicle.loc[years].iterrows()},
        "agriculture": {int(y): float(row.diesel_50ppm) for y, row in agri.loc[years].iterrows()},
        "industry_combined": {int(y): float(row.diesel_50ppm) for y, row in industry.loc[years].iterrows()},
        "industry_base": values("industrial", "base_year_volume")["ZAF"],
        "industry_elasticity": values("industrial", "elasticity")["ZAF"],
        "common_ev_share": {y: vehicles._ev_penetration(values("vehicles", "ev_scurve")["ZAF"], y) for y in years},
        "gdp": series("macro", "gdp_per_capita"),
        "eff_petrol": series("vehicles", "efficiency_improvement.gasoline"),
        "eff_diesel": series("vehicles", "efficiency_improvement.diesel"),
        "vehicle_scalars": {key: values("vehicles", key)["ZAF"] for key in ["annual_km_per_vehicle", "fuel_consumption", "petrol_diesel_split", "scrappage_rate", "new_vehicle_segment_split", "ev_scurve", "new_vehicle_regression"]},
        "agri_base": values("agriculture", "base_year_volume")["ZAF"],
        "agri_elasticity": values("agriculture", "elasticity")["ZAF"],
        "lever_design": json.loads((root / "pptx/story/fuel_lever_design_2026_10_07.json").read_text(encoding="utf-8")),
        "lever_rows": list(csv.DictReader((root / "assumptions/2026/timeseries/fuel_lever_design_2026_10_07.csv").open(encoding="utf-8"))),
        "input_hashes": {str(p.relative_to(root)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths.vintage_dir("2026").rglob("*")) if p.suffix in {".yaml", ".csv"}},
    }
    result["other_model"] = {}
    for mod in (aviation, generation, marine):
        frame = mod.compute_country_annual(provider, run, "ZAF", start_year=2022)
        result["other_model"][mod.name] = {
            product: {int(y): float(v) for y, v in frame[product].items() if y in years}
            for product in frame.columns
        }
    result["generation_inputs"] = {
        "load_factor": series("generation", "load_factor"),
        "efficiency": values("generation", "efficiency")["ZAF"],
        "mj_per_litre": values("generation", "mj_per_litre"),
    }
    result["passenger_departures"] = series("aviation", "passenger_departures")
    result["aviation_regression"] = values("aviation", "regression")["ZAF"]
    result["marine_inputs"] = {
        "ports": values("marine", "base_year_volume"),
        "elasticity": values("marine", "elasticity")["ZAF"],
        "product_split": values("marine", "product_split"),
    }
    result["evidence"] = build_evidence(root)
    # Independent aggregation check on the engine's diagnostic output.
    for y in years:
        for product in ["petrol_95", "diesel_50ppm"]:
            total = sum(d["litres"] for d in diagnostics if d["year"] == y and d["product"] == product)
            assert abs(total - result["vehicle"][y][product]) < 1e-4
    (out / "workshop_data.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Exported {len(years)} years of current-engine evidence; diagnostic totals reconcile.")


def build_evidence(root):
    """Summarise staged observations without adopting or extrapolating model inputs."""
    observations = {}
    files = {}
    def read(relative):
        path = root / relative
        files[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        return pd.read_csv(path)
    ts = "assumptions/2026/timeseries/"
    reporting = "pptx/story/evidence_2026_10_06/"
    def annual(key, df, path, unit, note, scale=1):
        sub = df[df.period.between(2022, 2026)].copy()
        if sub.period.duplicated().any():
            raise ValueError(f"Competing annual observations for {key}")
        observations[key] = {"annual": {int(r.period): float(r.value) / scale for r in sub.itertuples()}, "unit": unit, "source": path, "note": note, "latest": None}
    def monthly(key, df, path, unit, note, method="mean", scale=1, snapshot=False):
        sub = df.copy().sort_values("period")
        if sub.period.duplicated().any():
            raise ValueError(f"Competing monthly observations for {key}")
        out = {}
        for year in range(2022, 2027):
            g = sub[sub.period.str.startswith(str(year))]
            if snapshot:
                g = g[g.period == f"{year}-12"]
                if len(g) == 1:
                    out[year] = float(g.iloc[0].value) / scale
            elif len(g) == 12:
                out[year] = float(g.value.sum() if method == "sum" else g.value.mean()) / scale
        latest = None
        g = sub[sub.period.str.startswith("2026")]
        if len(g):
            value = g.iloc[-1].value if snapshot else (g.value.sum() if method == "sum" else g.value.mean())
            latest = {"value": float(value) / scale, "period": str(g.iloc[-1].period) if snapshot else f"{g.iloc[0].period} to {g.iloc[-1].period}", "basis": "snapshot" if snapshot else f"{len(g)} months; {method}; not annualised"}
        observations[key] = {"annual": out, "unit": unit, "source": path, "note": note, "latest": latest}
    for product in ("petrol", "diesel", "jet", "fuel_oil"):
        path = ts + "fuel_sales_fiasa.csv"
        df = read(path)
        annual("sales_" + product, df[df["product"] == product], path, "million L/year", "FIASA staged reported sales; latest edition selected by existing extract. 2024 revisions unresolved; not verified consumption.", 1e6)
        path = ts + "fuel_sales_department.csv"
        df = read(path)
        annual("dept_" + product, df[(df["product"] == product) & (df.quarters_reported == 4)], path, "million L/year", "Department sales with four reported quarters. Preserve differences from FIASA; no automatic source selection.", 1e6)
    path = ts + "new_vehicle_market_naamsa.csv"
    df = read(path)
    for segment in ("cars", "light_commercial", "medium_heavy_commercial", "total"):
        annual("sales_vehicles_" + segment, df[(df.segment == segment) & (df.basis == "actual")], path, "vehicles/year", "NAAMSA actual new sales. Published 2026/27 projections excluded from observed rows.")
    path = ts + "nev_sales_naamsa.csv"
    df = read(path)
    for drive in ("battery_electric", "plug_in_hybrid", "traditional_hybrid"):
        annual("nev_" + drive, df[df.drivetrain == drive], path, "vehicles/year", "All-market drivetrain sales; passenger/truck split is not supplied. Do not assign all to passenger or freight.")
    path = ts + "vehicle_population_natis.csv"
    df = read(path)
    for vehicle_class in ("cars", "light_commercial", "trucks", "buses", "minibuses"):
        monthly("stock_" + vehicle_class, df[(df.vehicle_class == vehicle_class) & (df.province == "ZAF")], path, "vehicles", "eNaTIS December snapshots; latest June 2026 kept separately. No fuel/drivetrain split.", snapshot=True)
    path = reporting + "macro_statssa.csv"
    df = read(path)
    for key in ("gdp_per_capita", "agriculture_forestry_and_fishing", "manufacturing", "mining_and_quarrying", "construction"):
        percap = key == "gdp_per_capita"
        annual("macro_" + key, df[(df.series == key) & (df.basis == "actual")], path, "2015 ZAR/person" if percap else "bn 2015 ZAR", "Stats SA annual actual in staged reporting copy. Sector value added is an activity proxy, not measured fuel use.", 1 if percap else 1e9)
    path = reporting + "activity_statssa_monthly.csv"
    df = read(path)
    for key in ("manufacturing_volume_total", "mining_volume_total", "freight_payload_road", "freight_payload_rail"):
        freight = key.startswith("freight")
        monthly(key, df[df.series == key], path, "thousand tonnes" if freight else "index 2019=100", "Complete calendar years only; 2026 Jan–Jul shown separately. Tonnes do not measure tonne-km." if freight else "Arithmetic mean of all 12 monthly production indices; 2026 Jan–Jul mean shown separately.", method="sum" if freight else "mean")
    path = ts + "ocgt_generation_eskom.csv"
    df = read(path)
    for key in ("eskom_ocgt", "ipp_ocgt", "eskom_and_ipp_ocgt"):
        annual(key, df[df.series == key], path, "GWh / financial year", "Full financial year ending 31 March in the column year. Not calendar-year generation; fuel-burn bridge still required.")
    path = ts + "air_traffic_acsa.csv"
    df = read(path)
    for measure in ("passengers", "aircraft_movements"):
        monthly("acsa_" + measure, df[(df.measure == measure) & (df.flight_type == "total") & (df.direction == "departure")], path, "departures", "ACSA departures only; sums monthly total-flight rows without double counting flight categories. 2026 is Jan–Aug, not annualised.", method="sum")
    path = ts + "energy_balance_department.csv"
    df = read(path)
    anchors = {}
    for key in ("agriculture", "mining", "industry", "construction"):
        sub = df[(df.period == 2021) & (df["product"] == "diesel") & (df.flow_key == key)]
        assert len(sub) == 1
        anchors[key] = {"value": float(sub.iloc[0].value) / 1e6, "year": 2021, "unit": "million L/year", "source": path, "note": "Staged 2021 energy-balance extract, not adopted. Industry is a parent total including mining/construction; do not sum parent and children."}
    path = ts + "fuel_sales_department_by_province_quarterly.csv"
    df = read(path)
    provinces = []
    for product in ("petrol", "diesel"):
        for province in ("EC", "FS", "GP", "KZN", "LP", "MP", "NC", "NW", "WC"):
            sub = df[(df["product"] == product) & (df.province == province)]
            hist = {}
            for year in range(2022, 2027):
                g = sub[sub.period.str.startswith(str(year))]
                if len(g) == 4 and g.period.nunique() == 4:
                    hist[year] = float(g.value.sum()) / 1e6
            latest = sub[sub.period == "2023-Q1"]
            provinces.append({"province": province, "product": product, "annual": hist, "latest": float(latest.iloc[0].value) / 1e6 if len(latest) == 1 else None, "source": path})
    for key, entry in observations.items():
        assert all(2022 <= y <= 2026 for y in entry["annual"]), key
    assert 2026 not in observations["manufacturing_volume_total"]["annual"]
    assert 2026 not in observations["sales_vehicles_cars"]["annual"]
    return {"observations": observations, "anchors": anchors, "provinces": provinces, "source_hashes": files}


def reorder_workbook():
    """Reorder sheet metadata only; Artifact Tool does not expose this operation."""
    import zipfile
    from lxml import etree
    out = Paths.default().repo_root / "output" / "workshop_2026_10_07"
    metadata_name = "trace_qa.json" if "--linked" in sys.argv else "baseline_qa.json"
    if "--compact" in sys.argv:
        metadata_name = "compact_qa.json"
    metadata = json.loads((out / metadata_name).read_text(encoding="utf-8"))
    path = out / metadata.get("workbook", "Demand_baseline_workshop_2026_10_07.xlsx")
    namespace = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as archive:
        original = archive.read("xl/workbook.xml")
        doc = etree.fromstring(original)
        sheets = doc.find("s:sheets", namespace)
        old = list(sheets)
        by_name = {s.get("name"): s for s in old}
        assert set(by_name) == set(metadata["order"])
        new = [by_name[name] for name in metadata["order"]]
        index_map = {str(i): str(new.index(s)) for i, s in enumerate(old)}
        for node in doc.findall("s:definedNames/s:definedName", namespace):
            if node.get("localSheetId") is not None:
                node.set("localSheetId", index_map[node.get("localSheetId")])
        for view in doc.findall("s:bookViews/s:workbookView", namespace):
            for attr in ("activeTab", "firstSheet"):
                if view.get(attr) in index_map:
                    view.set(attr, index_map[view.get(attr)])
        for node in old:
            sheets.remove(node)
        sheets.extend(new)
        payload = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)
        temp = path.with_suffix(".reorder.tmp")
        with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED) as target:
            for info in archive.infolist():
                target.writestr(info, payload if info.filename == "xl/workbook.xml" else archive.read(info.filename))
    with zipfile.ZipFile(temp) as revised, zipfile.ZipFile(path) as original_archive:
        for name in revised.namelist():
            if name != "xl/workbook.xml":
                assert revised.read(name) == original_archive.read(name), name
        final = etree.fromstring(revised.read("xl/workbook.xml"))
        names = [s.get("name") for s in final.find("s:sheets", namespace)]
        assert names[-1] == "HML"
    temp.replace(path)
    print("Sheet order: " + " | ".join(names))


if __name__ == "__main__":
    import sys
    if "--reorder-workbook" in sys.argv:
        reorder_workbook()
    else:
        main()
