"""Source-to-file-to-function map for every input CSV of a vintage.

One row per CSV under ``assumptions/<vintage>/``: who publishes the data, where
the original sits, which command and parser produce the extract, and whether
the engine reads it. Coverage, units and row counts are read from the CSVs;
engine use is read from the delivered source profile; the publisher, original
and parser columns are the authored ``TRACE`` table below and must be updated
when a fetcher or source changes.

    python -m lfm.scripts.build_source_trace --vintage 2026 --out <file.csv>

A CSV with no entry in ``TRACE`` is still listed, marked "not traced", so a new
dataset cannot go unnoticed.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[3]
PROFILE = REPO / "output" / "delivered" / "source_profile_2026_10_05.csv"

MAIN = "on main"
BOTH_LOCAL = "local to Manish and Nigel; not on main"

WORKBOOK = "external/sources/Liquid Fuels Model - Supply Demand, 2025 - Reatile Copy.xlsx"
XLSX_CMD = "python -m lfm.scripts.extract_xlsx_to_assumptions"
DEPT = "Department of Mineral and Petroleum Resources (energy department)"
DEPT_URL = "https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/"
DEPT_CMD = "python -m lfm.scripts.fetch_energy_dept --vintage 2026"
ECON_CMD = "python -m lfm.scripts.fetch_economy --vintage 2026"
SARS_URL = "https://tools.sars.gov.za/tradestatsportal/data_download.aspx"
SARS_CMD = "python -m lfm.scripts.fetch_sars --vintage 2026"
MAIN_BRANCH = "on manish-branch (external/data/raw/sars/)"

# csv -> publisher, url, original, original_location, method, command, parser,
#        pack_use, latest_partial, issue, owner
TRACE: dict[str, tuple[str, ...]] = {
    # ---- read by the engine: all from the Reatile workbook -----------------
    "timeseries/gdp_per_capita.csv": (
        "Reatile workbook (AIA, March 2025)", "", WORKBOOK + " :: named ranges GDP per capita",
        MAIN, "manual (workbook extract)", XLSX_CMD, "extract_macro", "", "",
        "Not read from a publisher. Stats SA replacement is staged in macro_statssa.csv.",
        "Nigel: decide replacement"),
    "timeseries/passenger_departures.csv": (
        "Reatile workbook (AIA, March 2025)", "", WORKBOOK + " :: Jet - DemandSupply col K; PaxBaseScenario",
        MAIN, "manual (workbook extract)", XLSX_CMD, "extract_passenger_departures", "", "",
        "Forecast years are workbook assumptions. ACSA actuals are staged in air_traffic_acsa.csv.",
        "Nigel: decide replacement"),
    "timeseries/ocgt_load_factor.csv": (
        "Reatile workbook (AIA, March 2025)", "", WORKBOOK + " :: Assumptions, EAF load factor tables",
        MAIN, "manual (workbook extract)", XLSX_CMD, "extract_ocgt_load_factor", "", "",
        "Workbook load factors (45% in 2022) against Eskom actuals of 18% in FY2024.",
        "Nigel: decide replacement"),
    "timeseries/efficiency_improvement_diesel.csv": (
        "Reatile workbook (AIA, March 2025)", "", WORKBOOK + " :: efficiency improvement ranges",
        MAIN, "manual (workbook extract)", XLSX_CMD, "extract_efficiency_improvement", "", "",
        "No external source recorded in the workbook.", "Manish: source"),
    "timeseries/efficiency_improvement_gasoline.csv": (
        "Reatile workbook (AIA, March 2025)", "", WORKBOOK + " :: efficiency improvement ranges",
        MAIN, "manual (workbook extract)", XLSX_CMD, "extract_efficiency_improvement", "", "",
        "No external source recorded in the workbook.", "Manish: source"),
    "timeseries/refinery_production.csv": (
        "Reatile workbook (AIA, March 2025)", "", WORKBOOK + " :: Assumptions!L102:R131 and L135:R164",
        MAIN, "manual (workbook extract)", XLSX_CMD, "extract_refinery_production", "pack p8 context", "",
        "Holds utilisation, not production. Repeated rows removed on manish-branch (flag log section 3).",
        "Nigel: confirm"),
    # ---- workbook extracts not read by the engine --------------------------
    "timeseries/gdp.csv": (
        "Reatile workbook (AIA, March 2025)", "", WORKBOOK, MAIN, "manual (workbook extract)",
        XLSX_CMD, "extract_macro", "", "", "Superseded by macro_statssa.csv once adopted.", "Nigel"),
    "timeseries/gdp_growth.csv": (
        "Reatile workbook (AIA, March 2025)", "", WORKBOOK, MAIN, "manual (workbook extract)",
        XLSX_CMD, "extract_gdp_growth", "", "", "Superseded by gdp_growth_treasury.csv once adopted.", "Nigel"),
    "timeseries/population.csv": (
        "Reatile workbook (AIA, March 2025)", "", WORKBOOK, MAIN, "manual (workbook extract)",
        XLSX_CMD, "extract_macro", "", "", "Superseded by macro_statssa.csv once adopted.", "Nigel"),
    "timeseries/ocgt_load_shedding.csv": (
        "Reatile workbook (AIA, March 2025)", "", WORKBOOK, MAIN, "manual (workbook extract)",
        XLSX_CMD, "extract_ocgt_load_shedding", "", "", "Declared but not read by the engine.", "Nigel"),
    "timeseries/historical_demand.csv": (
        "Reatile workbook (AIA, March 2025)", "", WORKBOOK + " :: Gasoline/Diesel/Jet - DemandSupply, RSA Demand",
        MAIN, "manual (workbook extract)", XLSX_CMD, "extract_historical_demand",
        "comparison only (compare_history)", "",
        "15 stray jet rows removed on manish-branch (flag log section 4). Not declared in a block.",
        "Nigel: confirm"),
    # ---- energy department --------------------------------------------------
    "timeseries/fuel_sales_department.csv": (
        DEPT, DEPT_URL + "SA FUEL SALES VOLUME/", "<year>-...-FSV....xls(x), national annual workbooks 2005-2023",
        BOTH_LOCAL, "download", DEPT_CMD, "energy_dept.parse_sales", "pack p4, p5 national tie", "",
        "2013 corrected on manish-branch (published sheet). Series ends 2023.",
        "Nigel: confirm 2013 correction"),
    "timeseries/fuel_sales_department_quarterly.csv": (
        DEPT, DEPT_URL + "SA FUEL SALES VOLUME/", "same workbooks as fuel_sales_department.csv",
        BOTH_LOCAL, "download", DEPT_CMD, "energy_dept.parse_sales", "", "",
        "2013-Q4 corrected on manish-branch.", "Nigel: confirm 2013 correction"),
    "timeseries/fuel_sales_department_by_province.csv": (
        DEPT, DEPT_URL + "SA FUEL SALES VOLUME/", "<year>-...-Magisterial-Districts-data.xlsx, quarterly sheets",
        BOTH_LOCAL + " (2013 annual workbook on manish-branch)", "download", DEPT_CMD,
        "energy_dept.parse_provincial_sales via fetch_energy_dept._provincial", "pack p3, p4, p6, p12",
        "2023 (Q1 only)",
        "Ends 2022. 2018 understated about 1.8% (district Q1 sheet incomplete). 2014-Q3 differs from national file.",
        "Manish: later years (package 3)"),
    "timeseries/fuel_sales_department_by_province_quarterly.csv": (
        DEPT, DEPT_URL + "SA FUEL SALES VOLUME/", "same workbooks; source_file column names each one",
        BOTH_LOCAL, "download", DEPT_CMD, "energy_dept.parse_provincial_sales", "pack p4", "2023-Q1",
        "26 province/product years have blank quarters in the source (none petrol or diesel).",
        "resolved (flag log section 1)"),
    "timeseries/energy_balance_department.csv": (
        DEPT, DEPT_URL + "Energy_Balances.html", "<year>-Commodity-Flow-and-Energy-Balance.xlsx, 2007-2021",
        BOTH_LOCAL, "download", DEPT_CMD, "energy_dept.parse_balance", "pack p5 (2021 production)", "",
        "Ends 2021. Sector definitions shift in 2016. Fuel oil not extracted.",
        "Manish: later balance (package 4)"),
    "timeseries/fuel_prices_department.csv": (
        DEPT, DEPT_URL, "fuel-price-history-<year>.pdf, 2011-2025; price-breakdown-<year>-<month>.pdf to February 2026; "
        "cef-daily-<date>.pdf from February 2026 (Central Energy Fund)", BOTH_LOCAL, "download", DEPT_CMD,
        "energy_dept.parse_price_history", "", "2024 (to April)",
        "Runs to October 2026. Department to February 2026, then CEF daily sheets, which give inland "
        "prices only: coastal diesel has no value from December 2025, coastal petrol and paraffin none "
        "from March 2026.", "Nigel: confirm"),
    "timeseries/fuel_prices_department_annual.csv": (
        DEPT, DEPT_URL, "derived from fuel_prices_department.csv", "derived", "derived", DEPT_CMD,
        "fetch_energy_dept (12-month average)", "", "", "Complete years to 2025 for six series; coastal diesel to 2024 only.", "Nigel: confirm"),
    "timeseries/fuel_trade_department_review.csv": (
        DEPT, "https://www.dmpr.gov.za/ (SA Energy Trade Report 2024)",
        "external/data/raw/fuel_supply_review_20261006/trade2024.pdf, printed pp.12-13", MAIN, "download",
        "python -m lfm.scripts.collect_supply_review", "collect_supply_review.extract_trade", "pack p5", "",
        "Rounded figures. Diesel imports 10.8 bn L against FIASA 14.793. 2025 report returned 404.",
        "Manish (package 4)"),
    # ---- FIASA ----------------------------------------------------------------
    "timeseries/fuel_sales_fiasa.csv": (
        "Fuels Industry Association of South Africa", "https://fuelsindustry.org.za/publications/annual-reports/",
        "annual-report-<year>.pdf, 2021-2025 editions", BOTH_LOCAL + "; 2025 edition on main", "download",
        "python -m lfm.scripts.fetch_fuel_sales --vintage 2026", "fiasa.read_table / fiasa.combine",
        "pack p5 (2024 sales)", "",
        "Used for 2024 only. Its 2013 figures equal the department's superseded sheet.", "review"),
    "timeseries/fuel_trade_fiasa.csv": (
        "Fuels Industry Association of South Africa (from customs data)",
        "https://fuelsindustry.org.za/publications/annual-reports/",
        "annual-report-<year>.pdf; 2025 edition pp.47-49", BOTH_LOCAL + "; 2025 edition on main", "download",
        "python -m lfm.scripts.fetch_fuel_sales --vintage 2026", "fiasa.read_table / fiasa.combine",
        "pack p5 (source flag)", "",
        "Cross-check, and the record before 2014; SARS is primary from 2014. 'Kerosene' is jet plus "
        "paraffin. Its 2024 diesel import figure is 4.000 bn L above customs.", "Nigel: confirm 2024 figure"),
    "timeseries/refinery_capacity_reported.csv": (
        "Fuels Industry Association of South Africa",
        "https://fuelsindustry.org.za/publications/annual-reports/",
        "external/data/raw/fuel_supply_review_20261006/annual-report-2025.pdf, p.49", MAIN, "download",
        "python -m lfm.scripts.collect_supply_review", "collect_supply_review.extract_capacity", "pack p8", "",
        "Nameplate capacity, not output.", "Manish (package 4/5)"),
    "timeseries/fuel_trade_sars.csv": (
        "South African Revenue Service, trade statistics", SARS_URL,
        "sars-<imports|exports>-chapter27-fuels-<year>.xlsx, 2010-2026", MAIN_BRANCH, "download (web form)",
        SARS_CMD, "sars.read_report / sars.annual", "supersedes FIASA trade on pack p5", "2026 (to August)",
        "Primary record of imports and exports from 2014. Kilograms to 2012, litres from 2014, both in 2013.",
        "Nigel: confirm"),
    "timeseries/fuel_trade_sars_by_office.csv": (
        "South African Revenue Service, trade statistics", SARS_URL,
        "same workbooks", MAIN_BRANCH, "download (web form)", SARS_CMD, "sars.read_report / sars.annual",
        "imports by entry office (pack p5 gap)", "2026 (to August)",
        "Customs office that cleared the goods: a proxy for entry port, not a terminal record.",
        "Nigel: confirm"),
    "timeseries/fuel_trade_sars_by_partner.csv": (
        "South African Revenue Service, trade statistics", SARS_URL,
        "same workbooks", MAIN_BRANCH, "download (web form)", SARS_CMD, "sars.read_report / sars.annual",
        "", "2026 (to August)", "Origin for imports, destination for exports.", "Nigel: confirm"),
    "timeseries/oil_balance_jodi.csv": (
        "JODI oil database (South Africa's submissions)", "https://www.jodidata.org/oil/database/data-downloads.aspx",
        "jodi-secondary-zaf-2017-2022.csv; jodi-secondary-zaf-2023-2025.csv",
        "on manish-branch (external/data/raw/jodi/)", "scripted download and extract",
        "python -m lfm.scripts.stage_jodi --vintage 2026", "jodi.annual", "comparison rows only",
        "2025: no month reported",
        "Lowest JODI assessment code throughout. Diesel refinery output agrees with the energy balance within 4% "
        "for 2017-2021; petrol is 12-24% higher. Imports, demand and stocks are not usable.",
        "Not used (8 October)"),
    "timeseries/port_liquid_bulk_tnpa.csv": (
        "Transnet National Ports Authority", "https://www.transnet.net/SubsiteRender.aspx?id=24332214",
        "tnpa-cargo-summary-<period>.pdf, July 2024 to August 2026; calendar years 2024 and 2025",
        "on manish-branch (external/data/raw/tnpa/)", "scripted download and extract",
        "python -m lfm.scripts.stage_tnpa --vintage 2026 --fetch", "tnpa.parse_liquid_bulk", "none: all liquids, so not shown in the petrol and diesel tables",
        "January 2025 missing (publisher's link is wrong)",
        "Tons of all liquids, not fuel by product. Two months carry a note on the publisher's heading.",
        "Nigel: review"),
    "reference/zone_differentials_department.csv": (
        DEPT, "https://www.dmpr.gov.za/Portals/0/Energy_Website/files/esources/petroleum/petroleum_fuelprices.html",
        "department-diesel-wholesale-by-zone-2024-04.pdf; department-transport-cost-by-zone-2014-04-02.xls",
        "on manish-branch (external/data/raw/routes_access_20261008/)", "download and scripted extract",
        "python -m lfm.scripts.stage_zone_differentials --vintage 2026", "stage_zone_differentials.parse_diesel_2024",
        "workshop workbook, DR04 transport cost sheet", "",
        "Regulated transport allowance by pricing zone, not a commercial rate. Latest full list held is April 2024.",
        "Nigel: review"),
    "reference/zone_districts_department.csv": (
        DEPT, "https://www.dmpr.gov.za/Portals/0/Energy_Website/files/esources/petroleum/petroleum_fuelprices.html", "department-transport-cost-by-zone-2014-04-02.xls",
        "on manish-branch (external/data/raw/routes_access_20261008/)", "download and scripted extract",
        "python -m lfm.scripts.stage_zone_differentials --vintage 2026", "stage_zone_differentials.parse_zones_2014",
        "workshop workbook, DR04 transport cost sheet", "", "District list is from 2014.", "Nigel: review"),
    "reference/demand_evidence_points.csv": (
        "IEA; ICCT; Transnet; National Transmission Company South Africa", "https://www.iea.org/articles/fuel-economy-in-south-africa",
        "four documents named row by row", "on manish-branch (external/data/raw/demand_evidence_20261008/)", "manual transcription",
        "none", "typed by hand", "workshop workbook, DR07 sheets", "",
        "Vehicle fuel consumption 2005-2019, rail volumes 2018-2025, plant shutdown and commissioning dates. Each row carries its page.",
        "Nigel: review"),
    "reference/vehicle_population_by_fuel_province_dot2023.csv": (
        "Department of Transport (data from the Road Traffic Management Corporation)", "https://www.transport.gov.za/",
        "dot-transport-statistics-bulletin-2023.pdf, Table 2.8", "on manish-branch (external/data/raw/literature/)", "manual transcription",
        "none", "typed by hand", "workshop workbook, DR07 fleet by province sheet", "",
        "Petrol and diesel vehicles by province at December 2023. Not split by vehicle class. No later edition found.", "Nigel: review"),
    "reference/refinery_evidence_points.csv": (
        "Department of Mineral Resources and Energy; Glencore; Sasol; Central Energy Fund; PetroSA; Shell; Parliament; United Nations", DEPT_URL,
        "documents named row by row", "on manish-branch (external/data/raw/refinery_supply_20261008/ and folders named there)", "manual transcription",
        "none", "typed by hand", "workshop workbook, DR08 sheets", "",
        "Refinery capacity, status and closure dates, Natref yield, stated product splits, Secunda fuels output, outlook, and the United Nations output series (comparison only). The department's capacity table cites the industry association as its source.",
        "Nigel: review"),
    "reference/refinery_output_operators.csv": (
        "Sasol (production and sales metrics); Glencore (annual reports)", "https://www.sasol.com/",
        "sasol-metrics-fy2022/2025/2026.pdf, p.4; GLEN-2023/2024/2025-Annual-Report.pdf",
        "Sasol files on manish-branch (external/data/raw/sasol/); Glencore reports by link only",
        "manual transcription", "none", "typed by hand", "", "",
        "All refined products, no product split; fiscal and calendar years; Astron as energy content.",
        "Nigel: confirm"),
    # ---- economy ----------------------------------------------------------------
    "timeseries/macro_statssa.csv": (
        "Statistics South Africa (P0441 GDP; P0302 mid-year population)",
        "https://www.statssa.gov.za/?page_id=1854&PPN=P0441",
        "GDP P0441 - GDP Time series Q2 2026.xlsx (Annual sheet); Country projection ... (2002-2026).xlsx",
        "on manish-branch (external/data/raw/statssa/)", "manual download (site blocks scripts)",
        ECON_CMD, "statssa.parse_constant_price_series; statssa.parse_population", "pack p7 (sector value added)",
        "", "Manual placement each release. Years after 2026 are projections, not observations.",
        "Nigel: commit originals?"),
    "timeseries/macro_statssa_quarterly.csv": (
        "Statistics South Africa (P0441 GDP)", "https://www.statssa.gov.za/?page_id=1854&PPN=P0441",
        "GDP P0441 - GDP Time series Q2 2026.xlsx (Quarterly sheet)",
        "on manish-branch (external/data/raw/statssa/)", "manual download (site blocks scripts)", ECON_CMD,
        "statssa.parse_quarterly_constant_price_series", "", "2026 (to Q2)",
        "Not seasonally adjusted; four quarters add to the annual figure.", "Nigel: confirm"),
    "timeseries/activity_statssa_monthly.csv": (
        "Statistics South Africa (P2041 mining, P3041.2 manufacturing, P7162 land transport, P0141 CPI)",
        "https://www.statssa.gov.za/?page_id=1847", "release zips, July and August 2026",
        "on manish-branch (external/data/raw/statssa/)", "manual or browser download (site blocks scripts)",
        "python -m lfm.scripts.fetch_statssa_monthly --vintage 2026", "statssa.parse_monthly_series",
        "extends pack p7 (industry, freight)", "2026 (to July; CPI to August)",
        "Activity measures, not fuel volumes. Not seasonally adjusted. Tonnes, not tonne-kilometres.",
        "Nigel: confirm"),
    "timeseries/fuel_lever_design_2026_10_07.csv": (
        "AIA (Nigel Zhuwaki), authored proposal, not a publisher", "",
        "pptx/story/fuel_lever_design_2026_10_07.json (anchors and mechanisms)",
        "on main (authored in the repository)", "authored by hand", "", "", "pack p12-14", "",
        "120 proposed low/medium/high lever values for diesel, jet and petrol at 2030 and 2035. "
        "A sensitivity proposal, not an observation and not an approved forecast.",
        "Nigel: ranges under review (fuel_lever_review_2026-10-07.md)"),
    "timeseries/gdp_by_province_statssa.csv": (
        "Statistics South Africa (P0441.2 Provincial GDP)", "https://www.statssa.gov.za/?page_id=1847",
        "P0441.2  Provincial Gross Domestic Product(2024).zip, Tables 2-10, block c",
        "on manish-branch (external/data/raw/statssa/)", "manual or browser download (site blocks scripts)",
        ECON_CMD, "statssa.parse_provincial_gdp", "provincial driver for pack p3-4", "",
        "Annual, 2013-2024. Economic activity by province, not fuel litres.", "Nigel: confirm"),
    "timeseries/macro_worldbank.csv": (
        "World Bank (republishing Stats SA and UN)", "https://api.worldbank.org/v2/country/ZAF/indicator/",
        "worldbank-<indicator>.json", BOTH_LOCAL, "API", ECON_CMD, "economy.parse_world_bank", "", "",
        "Cross-check only; population after 2025 is a UN projection.", "none"),
    "timeseries/gdp_growth_treasury.csv": (
        "National Treasury, Budget Review 2026, chapter 2",
        "https://www.treasury.gov.za/documents/national%20budget/2026/review/Chapter%202.pdf",
        "budget-review-2026-chapter-2.pdf", BOTH_LOCAL, "download", ECON_CMD, "economy.parse_treasury_growth",
        "", "", "Forecast to 2028 only.", "none"),
    # ---- vehicles -------------------------------------------------------------------
    "timeseries/vehicle_population_natis.csv": (
        "NaTIS (Road Traffic Management Corporation)", "https://www.natis.gov.za/",
        "monthly live vehicle population PDFs", BOTH_LOCAL, "download",
        "python -m lfm.scripts.fetch_natis --vintage 2026", "natis.parse", "pack p7 (stock)", "",
        "All fuels together; no petrol/diesel split.", "open: fleet fuel mix"),
    "timeseries/new_vehicle_registrations_natis.csv": (
        "NaTIS (Road Traffic Management Corporation)", "https://www.natis.gov.za/",
        "monthly new registrations PDFs", BOTH_LOCAL, "download",
        "python -m lfm.scripts.fetch_natis --vintage 2026", "natis.parse", "", "2026 (to June)", "", "none"),
    "timeseries/new_vehicle_registrations_natis_annual.csv": (
        "NaTIS (Road Traffic Management Corporation)", "https://www.natis.gov.za/",
        "derived from the monthly file", "derived", "derived",
        "python -m lfm.scripts.fetch_natis --vintage 2026", "fetch_natis (calendar-year sum)", "", "", "", "none"),
    "timeseries/nev_sales_naamsa.csv": (
        "naamsa, quarterly review of business conditions", "https://naamsa.net/quarterly-reviews/",
        "quarterly review PDFs", BOTH_LOCAL, "download", "python -m lfm.scripts.fetch_naamsa --vintage 2026",
        "naamsa.parse_nev", "pack p7 (EV and hybrid sales)", "",
        "New sales, not fleet. Audit logged parser warnings on the 5 October refresh.", "Manish (package 5)"),
    "timeseries/new_vehicle_market_naamsa.csv": (
        "naamsa, quarterly review of business conditions", "https://naamsa.net/quarterly-reviews/",
        "quarterly review PDFs", BOTH_LOCAL, "download", "python -m lfm.scripts.fetch_naamsa --vintage 2026",
        "naamsa.parse_market", "", "", "2026-2027 are naamsa's own outlook, not observations.", "none"),
    "reference/vehicle_population_by_fuel_dot2023.csv": (
        "Department of Transport, Transport Statistics Bulletin 2023, Table 2.8 (source: RTMC)",
        "https://www.transport.gov.za/wp-content/uploads/2023/02/Transport-Statistics-Bulletin-2023.pdf",
        "dot-transport-statistics-bulletin-2023.pdf, p.40",
        "on manish-branch (external/data/raw/literature/)", "manual transcription", "none",
        "typed by hand", "", "", "One date only (December 2023). No later edition found.", "Nigel: commit original?"),
    "reference/vehicle_parameters_stone2018.csv": (
        "Stone, Merven, Maseela and Moonsamy (2018), J. Energy in Southern Africa 29(2), and supplement",
        "https://www.scielo.org.za/pdf/jesa/v29n2/06.pdf",
        "stone-2018-vehicle-parc-model-jesa-29-2.pdf; stone-2018-supplementary.pdf",
        "on manish-branch (external/data/raw/literature/)", "manual transcription", "none",
        "typed by hand", "", "", "Values are for 2014. Transcription not independently re-checked.",
        "Nigel: review"),
    "reference/fleet_fuel_split_2023.csv": (
        "Derived by AIA from the two reference tables above", "", "derived", "derived", "derived",
        "python -m lfm.scripts.derive_fleet_fuel_split", "lfm.model.core.fitting.proportional_fit", "", "",
        "An estimate: 2010 pattern fitted to December 2023 official totals.", "Nigel: review"),
    # ---- power, aviation, freight, infrastructure ---------------------------------
    "timeseries/ocgt_generation_eskom.csv": (
        "Eskom integrated reports", "https://www.eskom.co.za/investors/integrated-results/",
        "integrated report PDFs, years to March 2022-2026", BOTH_LOCAL, "download",
        "python -m lfm.scripts.fetch_eskom --vintage 2026", "eskom.parse_report", "pack p7 (power)", "",
        "GWh for financial years; diesel litres not reported in the extract.", "Manish (package 5)"),
    "reference/ocgt_diesel_burn_reported.csv": (
        "Parliament (replies by the Ministers of Public Enterprises and of Electricity and Energy)",
        "https://pmg.org.za/committee-question/30686/", "reply NW1980 (2025); press reports for 2022 and 2023",
        "by link only", "manual transcription", "none", "typed by hand", "", "",
        "Three years; none for the year to March 2024. Implies 0.31 litres per kWh; not adopted in the model.",
        "Nigel: decide on the factor"),
    "timeseries/air_traffic_acsa.csv": (
        "Airports Company South Africa", "https://www.airports.co.za/StatisticsLib/",
        "acsa-group-passengers.pdf; acsa-group-aircraft_movements.pdf", BOTH_LOCAL, "download",
        "python -m lfm.scripts.fetch_acsa --vintage 2026", "acsa.parse", "", "2026 (to August)",
        "Jet is tracked separately from the petrol/diesel focus. No cargo series.", "open: air cargo"),
    "timeseries/air_traffic_acsa_annual.csv": (
        "Airports Company South Africa", "https://www.airports.co.za/StatisticsLib/", "derived from the monthly file",
        "derived", "derived", "python -m lfm.scripts.fetch_acsa --vintage 2026", "acsa.calendar_years", "", "",
        "", "none"),
    "timeseries/freight_payload_statssa_review.csv": (
        "Statistics South Africa, Land transport P7162",
        "https://www.statssa.gov.za/?page_id=1854&PPN=P7162",
        "external/data/raw/demand_drivers_20261006/P7162December2024.pdf and P7162December2025.pdf", MAIN,
        "download (two fixed PDFs)", "python -m lfm.scripts.collect_freight_review",
        "collect_freight_review.totals", "pack p7 (freight activity)", "",
        "Two years only. 2024 road payload revised from 790.6 to 979.8 Mt between editions. Tonnes, not tonne-km.",
        "Manish (package 5)"),
    "infrastructure/storage_transnet_pipelines_depots.csv": (
        "Transnet Pipelines, leasing RFPs 2026", "https://www.transnet.net/TPL-Leasing-Opportunities",
        "external/sources/transnet_tpl_leasing_2026/tpl-rfp-<site>.pdf", MAIN, "manual transcription", "none",
        "typed by hand", "pack p3, p9, p14", "", "Two of five RFPs state no product storage.", "none"),
    "reference/fuel_levy_revenue_raf.csv": (
        "Road Accident Fund", "https://static.pmg.org.za/RAF_Annual_Report_2025.pdf",
        "raf-annual-report-2024-25.pdf, note 16 (p.183)", "on manish-branch (external/data/raw/raf/)",
        "manual transcription", "none", "typed by hand", "hand-back deck section 1", "",
        "Gross levies and diesel rebate in rand; litres derived in the balance note. Fiscal years; "
        "petrol and diesel together.", "Nigel: weigh against the 2024 sales figures"),
    # ---- added by Nigel on main, 7 October (sa_review_evidence.sources.yaml) --
    "timeseries/eskom_fuel_eaf_review_2026_10_07.csv": (
        "Eskom", "https://www.eskom.co.za/investors/integrated-results/", "eskom-integrated-report-2025.pdf",
        "on main (external/data/refresh_20261005/raw/eskom/)", "scripted extract",
        "python -m lfm.scripts.stage_sa_review_evidence", "stage_sa_review_evidence", "South Africa review pack", "",
        "Eskom energy availability and peaking fuel by financial year. Fuel volume includes kerosene and is Eskom "
        "only; the 2026 volume was not found. Status in the sources file: independent verification pending.",
        "Nigel: verify and decide adoption"),
    "timeseries/investment_review_2026_10_07.csv": (
        "World Bank", "https://api.worldbank.org/v2/country/ZAF/indicator/BX.KLT.DINV.WD.GD.ZS",
        "worldbank_fdi.json; worldbank_gfcf.json", "on main (external/data/raw/sa_review_20261007T181010425382Z/)",
        "scripted extract", "python -m lfm.scripts.stage_sa_review_evidence", "stage_sa_review_evidence",
        "South Africa review pack", "",
        "Foreign direct investment and gross fixed capital formation as a share of GDP. Status in the sources "
        "file: preserved; not independently verified.", "Nigel: verify and decide adoption"),
    "infrastructure/power_fleet_diesel.csv": (
        "Eskom; press reports", "https://www.eskom.co.za/eskom-divisions/gx/peaking-power-stations/",
        "eskom-gx0001-generation-plant-mix-rev29.pdf", "on manish-branch (external/data/raw/eskom/)",
        "manual transcription", "none", "typed by hand", "workshop workbook, Power fleet sheet", "",
        "Diesel peaking stations and coal stations being retired, with capacities and dates. Three rows are "
        "marked to confirm.", "Nigel, Henry: agree the fleet and the repowering scenario"),
    "infrastructure/terminal_site_assumptions.csv": (
        "NERSA; Vopak; Transnet Pipelines", "https://www.nersa.org.za/regulator-decisions",
        "external/data/raw/vopak_storage_20261006/nersa-vopak-*.pdf, durban.html, lesedi.html",
        "on manish-branch (external/data/raw/vopak_storage_20261006/)", "manual transcription", "none",
        "typed by hand", "hand-back deck section 4", "",
        "Site assumptions for Vopak Lesedi and Durban. Each row is marked evidence or estimate; "
        "estimates are the analyst's.", "Nigel: agree provisional operating ranges"),
}

FIELDS = [
    "dataset", "status", "publisher", "source_url", "original_file", "original_location", "method",
    "refresh_command", "parser_or_function", "extract_path", "rows", "first_period", "last_period",
    "latest_partial_period", "units", "geography", "engine_consumer", "pack_or_other_use", "issue",
    "owner_next_action",
]


def build(vintage: str) -> list[dict]:
    base = REPO / "assumptions" / vintage
    profile = pd.read_csv(PROFILE) if PROFILE.exists() else pd.DataFrame(columns=["csv"])
    rows: list[dict] = []
    for path in sorted(base.glob("*/*.csv")):
        rel = path.relative_to(base).as_posix()
        if rel.startswith("seasonality/"):
            continue
        data = pd.read_csv(path)
        periods = data["period"].astype(str) if "period" in data else pd.Series(dtype=str)
        used = profile[(profile["csv"] == rel) & (profile["model_access"] == "Requested by engine")]
        entry = TRACE.get(rel)
        (publisher, url, original, location, method, command, parser, pack, partial, issue,
         owner) = entry or ("not traced",) + ("",) * 10
        if len(used):
            status = "engine-used"
        elif pack:
            status = "reporting-only"
        else:
            status = "staged, unused"
        geography = "South Africa, by province" if "province" in data else "South Africa, national"
        if "country" in data and data["country"].astype(str).str.contains(":").any():
            geography = "South Africa, by refinery"
        rows.append({
            "dataset": path.stem, "status": status, "publisher": publisher, "source_url": url,
            "original_file": original, "original_location": location, "method": method,
            "refresh_command": command, "parser_or_function": parser,
            "extract_path": f"assumptions/{vintage}/{rel}", "rows": len(data),
            "first_period": periods.min() if len(periods) else "",
            "last_period": periods.max() if len(periods) else "",
            "latest_partial_period": partial,
            "units": "; ".join(sorted(map(str, data["unit"].dropna().unique()))) if "unit" in data else
                     "not stated in file",
            "geography": geography,
            "engine_consumer": "; ".join(used["calculation_locations"].dropna().unique()),
            "pack_or_other_use": pack, "issue": issue, "owner_next_action": owner,
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--vintage", default="2026")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    rows = build(args.vintage)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    counts = pd.Series([r["status"] for r in rows]).value_counts().to_dict()
    untraced = [r["dataset"] for r in rows if r["publisher"] == "not traced"]
    print(f"wrote {len(rows)} datasets -> {args.out}  {counts}")
    if untraced:
        print("not traced:", ", ".join(untraced))


if __name__ == "__main__":
    main()
