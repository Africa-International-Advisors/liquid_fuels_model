"""Profile data shapes/model access and probe key publisher/document URLs.

Reads an existing source audit. GET probes sample at most 16 KiB and do not
replace inputs. A successful probe is connectivity evidence, not full extraction,
freshness or accuracy verification. No scheduler or background refresh is created.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import re
import time
import urllib.error
import urllib.request

import yaml

from lfm.config import Paths
from lfm.governance import assumption_blocks
from lfm.scripts.audit_source_inputs import source_records, write_csv
from lfm.sources import acsa, economy, energy_dept, eskom, fiasa, naamsa, natis


def shape(node, rows=None):
    if "csv" in node:
        if rows and "period" in rows[0]:
            return "Time series" if len({r.get("period") for r in rows}) > 1 else "Dated snapshot"
        return "Reference / infrastructure table"
    if "value" in node and not isinstance(node["value"], (dict, list)):
        return "Scalar"
    return "Structured parameters / assumptions"


def probe(target):
    started = time.monotonic()
    result = {**target, "tested_at_utc": datetime.now(timezone.utc).isoformat(), "http_status": "",
              "final_url": "", "content_type": "", "sample_bytes": 0, "result": "", "detail": ""}
    try:
        request = urllib.request.Request(target["url"], headers={"User-Agent": "Mozilla/5.0 (lfm source connectivity check)"})
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read(16384)
            result.update(http_status=response.status, final_url=response.url,
                          content_type=response.headers.get("Content-Type", ""), sample_bytes=len(body))
        text = body.decode("utf-8", errors="replace").lower()
        challenge = any(marker in text for marker in ("cf-chl-", "just a moment", "verify you are human", "checking your browser"))
        expected = target["expected"]
        matched = {"PDF": body.lstrip().startswith(b"%PDF"),
                   "Excel": body.startswith(b"PK") or body.startswith(bytes.fromhex("d0cf11e0")),
                   "JSON": body.lstrip().startswith((b"[", b"{")),
                   "HTML": "html" in result["content_type"].lower() or b"<html" in body.lower()}.get(expected, True)
        result["result"] = "Browser challenge" if challenge else ("Reachable; expected sample" if matched else "Reachable; unexpected content")
        result["detail"] = "Sample only; full download and table extraction not tested"
    except urllib.error.HTTPError as exc:
        result.update(http_status=exc.code, final_url=exc.url, result="HTTP error", detail=str(exc))
    except Exception as exc:
        result.update(result="Connection failed", detail=str(exc))
    result["seconds"] = round(time.monotonic() - started, 2)
    return result


def probe_with_retry(target):
    first = probe(target)
    if first["result"] == "Reachable; expected sample":
        first["attempts"] = 1
        return first
    second = probe(target)
    first_detail = f"First attempt: {first['result']} (HTTP {first['http_status'] or 'none'})."
    second["detail"] = first_detail + " " + second["detail"]
    second["attempts"] = 2
    second["seconds"] = round(first["seconds"] + second["seconds"], 2)
    if second["result"] == "Reachable; expected sample":
        second["result"] = "Reachable after retry; intermittent response"
    return second


def expected_type(url):
    lower = url.lower()
    if ".pdf" in lower or "getfile.ashx" in lower: return "PDF"
    if re.search(r"\.xls[xm]?(?:$|[?&#])", lower): return "Excel"
    if "api.worldbank.org" in lower: return "JSON"
    return "HTML"


def refresh_route(csv_path):
    for marker, route in [("department", "Excel/PDF download: fetch_energy_dept"),
                          ("fiasa", "PDF download: fetch_fuel_sales"), ("eskom", "PDF download: fetch_eskom"),
                          ("natis", "PDF download: fetch_natis"), ("naamsa", "PDF download: fetch_naamsa"),
                          ("acsa", "PDF download: fetch_acsa"), ("macro_worldbank", "World Bank API: fetch_economy"),
                          ("macro_statssa", "Manual Stats SA Excel download, then fetch_economy"),
                          ("treasury", "PDF download: fetch_economy"), ("fleet_fuel_split", "Derived estimate: derive_fleet_fuel_split"),
                          ("reference/", "Manual source review/transcription"), ("infrastructure/", "Manual source review/transcription")]:
        if marker in csv_path: return route
    return "Original model workbook extraction" if csv_path else "Controlled YAML assumption update; source review required"


def period_profile(rows):
    periods = sorted({str(r["period"]) for r in (rows or []) if r.get("period")})
    kinds = set()
    for period in periods:
        kinds.add("Monthly" if re.fullmatch(r"\d{4}-\d{2}",period) else ("Quarterly" if re.fullmatch(r"\d{4}-Q[1-4]",period) else ("Annual" if re.fullmatch(r"\d{4}",period) else "Other period format")))
    return {"first_period": periods[0] if periods else "", "last_period": periods[-1] if periods else "", "period_frequency": "; ".join(sorted(kinds)) or "Not time-indexed"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True, help="audit.json from audit_source_inputs")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--prior-pass", type=Path, help="Earlier profile.json; preserve earlier failures alongside current results")
    parser.add_argument("--reuse-connectivity", type=Path, help="Rebuild the profile using recorded URL results; do not make network requests")
    args = parser.parse_args(argv)
    paths = Paths.default()
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    vintage = audit["summary"]["vintage"]
    base = paths.vintage_dir(vintage)
    out = (args.output_dir or paths.runs_dir / ("source_profile_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))).resolve()
    out.mkdir(parents=True, exist_ok=False)
    indexed = {r["block"]: r for r in audit["assumption_blocks"]}
    profiles = []
    for path in sorted(base.glob("*.yaml")):
        if path.stem.startswith("_"): continue
        for key, node in assumption_blocks(yaml.safe_load(path.read_text(encoding="utf-8")) or {}):
            block = f"{path.stem}.{key}"
            rows = None
            if "csv" in node:
                with (base / node["csv"]).open(encoding="utf-8-sig", newline="") as stream:
                    rows = list(csv.DictReader(stream))
            record = indexed[block]
            profiles.append({"block": block, "data_shape": shape(node, rows), "csv": node.get("csv", ""),
                             **period_profile(rows), "refresh_route":refresh_route(node.get("csv", "")),
                             "observations_or_leaves": record["input_count"], "units": node.get("units", ""),
                             "source": node.get("source", ""), "model_access": record["model_access"],
                             "calculation_locations": record["callers"], "owner": node.get("owner", ""),
                             "accuracy_status": "Independent verification not recorded" if record["verified_rows"] < record["input_count"] else "Review recorded; inspect evidence"})
    declared_csvs = {p["csv"] for p in profiles if p["csv"]}
    for file in audit["data_files"]:
        if file["file"] in declared_csvs: continue
        with (base / file["file"]).open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        profiles.append({"block": "Undeclared CSV: " + file["file"], "data_shape": shape({"csv":file["file"]},rows),
                         **period_profile(rows), "refresh_route":refresh_route(file["file"]),
                         "csv":file["file"], "observations_or_leaves": len(rows), "units": "Source declaration missing",
                         "source": "Not declared; inspect original extraction and validation script",
                         "model_access": "Not requested by engine; check validation/reference use", "calculation_locations": "",
                         "owner": "Not declared", "accuracy_status": "Independent verification not recorded"})

    targets = []
    def add(label, url, purpose, expected=None):
        if url.startswith("https://") or url.startswith("http://"):
            if url not in {t["url"] for t in targets}:
                targets.append({"source": label, "purpose": purpose, "url": url, "expected": expected or expected_type(url)})
    for label, url in [("Energy sales", energy_dept.SALES_INDEX), ("Energy balances", energy_dept.BALANCE_INDEX),
                       ("Fuel prices", energy_dept.PRICE_INDEX), ("FIASA", fiasa.INDEX_URL), ("Eskom", eskom.INDEX_URL),
                       ("NaTIS", natis.HOME_URL), ("NAAMSA", naamsa.INDEX_URL)]:
        add(label, url, "Publisher discovery page", "HTML")
    for label,url in acsa.URLS.items(): add("ACSA " + label, url, "Fixed download endpoint", "PDF")
    add("World Bank GDP", economy.world_bank_url(economy.SERIES["gdp"][0],1990,datetime.now(timezone.utc).year), "API endpoint", "JSON")
    # Inspect most recent refresh metadata when available; recorded originals may have offline URLs.
    documents = list(audit["source_evidence"])
    refresh_dirs = list(paths.runs_dir.glob(f"*/assumptions/{vintage}/timeseries"))
    refreshed = max(refresh_dirs, key=lambda p:p.stat().st_mtime) if refresh_dirs else None
    if refreshed is not None:
        for path in sorted(refreshed.glob("*.sources.yaml")):
            documents.extend(source_records(yaml.safe_load(path.read_text(encoding="utf-8")),path.name))
    groups = {}
    for record in documents:
        if str(record.get("url", "")).startswith("http"):
            group = Path(record["metadata"]).name
            groups.setdefault(group,[]).append(record)
            if record.get("evidence") == "Original not found locally":
                add(group, record["url"], "Missing local original", "PDF" if record.get("file", "").lower().endswith(".pdf") else None)
    for group,records in sorted(groups.items()):
        latest = max(records, key=lambda r: (r.get("file", ""),r["url"]))
        add(group,latest["url"],"Representative document/API endpoint", "PDF" if latest.get("file", "").lower().endswith(".pdf") else None)
    for label, marker in [("Treasury forecast", "budget-review"), ("NaTIS vehicle population", "LiveVehPopPerClassProv"),
                          ("NaTIS registrations", "NewVehicleRegistration"), ("NAAMSA market", "Industry"),
                          ("NAAMSA NEV", "Review-of-Business"), ("Energy national sales", "Fuel-Sales-Volume"),
                          ("Energy provincial sales", "Disaggregated"), ("Energy balance workbook", "Commodity-Flow")]:
        candidates=[r for r in documents if marker.lower() in r.get("file", "").lower() and str(r.get("url", "")).startswith("http")]
        if candidates:
            document=max(candidates,key=lambda r:(max(re.findall(r"20\d{2}",r.get("file", "")),default=""),r.get("file", "")))
            add(label,document["url"],"Direct dataset download", "PDF" if document.get("file", "").lower().endswith(".pdf") else None)
    # Unreadable metadata remains an audit issue; only literal URLs are extracted for connectivity.
    for error in audit.get("metadata_errors", []):
        text = (paths.repo_root / error["file"]).read_text(encoding="utf-8")
        for url in re.findall(r"https?://[^\s\"'<>]+", text): add(error["file"],url,"URL in unreadable metadata")
    add("Stats SA", "https://www.statssa.gov.za/", "Manual-source website; does not test the missing workbook download", "HTML")
    if args.reuse_connectivity:
        results = json.loads(args.reuse_connectivity.read_text(encoding="utf-8"))["connectivity"]
        if {r["url"] for r in results} != {t["url"] for t in targets}:
            raise ValueError("Recorded connectivity targets differ; run a new live test")
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(probe_with_retry, targets))
    if args.prior_pass:
        earlier = {r["url"]:r for r in json.loads(args.prior_pass.read_text(encoding="utf-8"))["connectivity"]}
        for row in results:
            prior = earlier.get(row["url"],{})
            if prior.get("result") in {"HTTP error","Connection failed","Browser challenge"}:
                row["detail"] = f"Earlier pass {prior.get('tested_at_utc')}: {prior['result']} HTTP {prior.get('http_status')}. " + row["detail"]
                if row["result"] == "Reachable; expected sample": row["result"] = "Reachable now; earlier failure recorded"
    write_csv(out / "source_profile.csv", profiles, list(profiles[0]))
    write_csv(out / "connectivity.csv", results, list(results[0]))
    data = {"tested_at_utc": max(r["tested_at_utc"] for r in results), "profiles": profiles, "connectivity": results}
    (out / "profile.json").write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8")
    def table(rows, fields):
        def cell(value):
            escaped = html.escape(str(value),quote=True)
            return '<a href="'+escaped+'">'+escaped+'</a>' if str(value).startswith(('https://','http://')) else escaped
        return '<table><thead><tr>'+''.join('<th>'+html.escape(f.replace('_',' '))+'</th>' for f in fields)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+cell(r.get(f,''))+'</td>' for f in fields)+'</tr>' for r in rows)+'</tbody></table>'
    report = '<!doctype html><html><meta charset="utf-8"><title>Source profile and connectivity</title><style>body{font:15px Arial;margin:32px;color:#172b3a}table{border-collapse:collapse;margin-bottom:30px;width:100%}th{background:#243c54;color:white}td,th{padding:10px;text-align:left;vertical-align:top;border-bottom:1px solid #ddd;overflow-wrap:anywhere}tr:nth-child(even){background:#edf3f7}h1{font-size:26px}</style><h1>Source profile and connectivity</h1><p>The model reads saved local inputs. URL reachability is separate from model use and data accuracy.</p><p>Live URL samples do not verify freshness, extraction completeness or accuracy. The CSV profiles include calculation locations and source declarations.</p><h2>Key URL tests</h2>'+table(results,['source','purpose','http_status','result','seconds','url','detail'])+'<h2>Input profiles</h2><p>Time series vary by period. Scalars are single declared values. Structured assumptions contain scalar parameters by country, segment or scenario. A dated snapshot covers one period; reference tables are not necessarily time series.</p>'+table(profiles,['block','data_shape','units','first_period','last_period','refresh_route','model_access'])+'</html>'
    report = report.replace('<h2>Key URL tests</h2>', '<p>URL samples taken at '+html.escape(data["tested_at_utc"])+'.</p><h2>Key URL tests</h2>')
    (out / "source_profile.html").write_text(report,encoding="utf-8")
    print(json.dumps({"out":str(out),"targets":len(results),"results":dict(__import__('collections').Counter(r['result'] for r in results)),"shapes":dict(__import__('collections').Counter(r['data_shape'] for r in profiles))},indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
