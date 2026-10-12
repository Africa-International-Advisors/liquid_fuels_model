"""Resolve registered inputs and export the four South Africa analyses."""
import argparse, csv, hashlib, json
from pathlib import Path
import yaml
from lfm.model.sa_analytics import build

def main():
    root=Path(__file__).resolve().parents[3]
    parser=argparse.ArgumentParser();parser.add_argument('--planning-case',action='store_true');args=parser.parse_args()
    source=root/'assumptions/2026/sa_analytics_2025.yaml'
    case_source=root/'assumptions/2026/sa_story_case_2025.yaml'
    case=yaml.safe_load(case_source.read_text('utf8'))['production']['value'] if args.planning_case else None
    result=build(yaml.safe_load(source.read_text('utf8'))['snapshot']['value'],case)
    result['input_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    if case:result['planning_case_sha256']=hashlib.sha256(case_source.read_bytes()).hexdigest()
    out=root/('output/delivered/sa_analytics_2026_10_11_v02' if case else 'output/delivered/sa_analytics_2026_10_11')
    out.mkdir(parents=True,exist_ok=True)
    (out/'analytics.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    for name,tab in result['sheets'].items():
        with (out/(name.lower().replace(' ','_')+'.csv')).open('w',encoding='utf8',newline='') as f:
            w=csv.writer(f);w.writerow(tab['headers'])
            w.writerows([[x['value'] if isinstance(x,dict) else x for x in r] for r in tab['rows']])
    s=result['summary']
    notes=[
        'South Africa analytics: 2025 baseline and 2030 sensitivities',
        'Prepared 11 October 2026. Petrol and diesel only. All volumes bn litres unless stated.',
        '',
        *[f'{k}: {v:.4f}' for k,v in s.items()],
        '',
        '1 DEMAND',
        'Department 2023 sales are the primary national anchor. Petrol grows with assumed activity (+0.5%/year) and efficiency (-1.5%/year). Non-power diesel grows 1%/year; utility and assumed private-backup volumes are replaced annually. FIASA 2024 is a separate source-choice sensitivity.',
        'Sector estimates use 2018-2021 mean intensity at observed annual activity. Road diesel starts with the 2021 energy-balance road category; 2025 road tonnes proxy activity. A 75% road-diesel freight allocation is authored, not a measured split. Sector-attributed road purchases stay with those sectors. Other diesel remains a visible residual. The construction of disjoint categories is an analytical convention, not a newly verified census.',
        'Eskom p141 contains 679.1m litres of diesel and kerosene for FY2025, whereas the prior slides cited 677.9m. This run explicitly uses the p141 series consistently. FY measures proxy calendar years; all Eskom fuel is provisionally treated as diesel. Private-backup assumptions are 0.8/0.6/0.2bn in 2023/24/25. They are not reported measurements.',
        '',
        '2 DOMESTIC SUPPLY',
        'Secunda: FY2025 27.6m barrels of refined products, 90% assumed petrol/diesel, 65/35 within that subset. Natref: FY2025 Sasol 14.7m barrels / 63.64%, petrol yield 30.5%, diesel 34%. FY2026 is not grossed up using that share because reported output includes above-share processing. Astron: 164365 billion Btu / 35.5 MJ per litre, assuming 80% petrol/diesel and 50/50 within that subset. SAPREF, PetroSA and Enref contribute zero 2025 refining output.',
        'The independent supply-plus-net-import estimate exceeds the demand estimate. This is an unresolved statistical/scope difference, not assumed stocks, not incremental demand, and not Vopak opportunity. Product-level differences are on Balance. Sales coverage, refinery yields, fiscal timing and trade scope require reconciliation.',
        '',
        '3 OUTLOOK',
        'Three authored 2025-2030 paths vary activity, road efficiency, rail displacement, power recovery and refinery availability/restarts. Rail displacement applies only to freight after growth and efficiency, with 10% diesel rebound for rail. Power reductions apply separately. Refinery restarts ramp to scenario utilisation over two years; the base case has none through 2030.',
        'Demand-implied imports use zero stock change and constant 2025 exports. A separate trade-anchored series applies modelled changes to observed 2025 customs imports; it preserves, rather than solves, the opening discrepancy. The workbook shows both and must not conflate them.',
        '',
        '4 MOZAMBIQUE',
        'Existing liquid-fuel nodes: Galp/IPG Matola, Petromoc Lingamo, Galp/IPG Beira, Petromoc Nacala and Pemba. Galp Matola was inaugurated in December 2020 and Beira operates since February 2021, so these are not new 2025 additions. Lingamo has a published 390000m3 across liquid fuels. Potential overlap with other operator capacity is unconfirmed; individual facility sensitivities are not added.',
        'Temane PSA began production in December 2025, but disclosed output is light oil, gas and LPG, not finished petrol/diesel. No direct finished-fuel supply is credited. CFM berth tonnes/year are not storage or South African delivered volumes.',
        'Route economics compare the same inland destination using explicit illustrative distance, tanker, border, terminal and financing inputs. They are not quoted tariffs or a determination of customs/tax treatment. Gas and coal developments are excluded from petrol/diesel terminal capacity. Diversion reallocates South African imports between gateways, rather than reducing national demand.',
        '',
        'PRIORITIES / OWNERS / EXPIRY',
        'Manish: reconcile Department/FIASA sales definitions and SARS product/quantity scope; obtain calendar-year plant output and product yields. Trigger: before using a single national balance externally.',
        'Nigel with Vopak/hauliers: replace route cost assumptions with matched product/destination quotes, border costs, allocation and terminal access. Trigger: before ranking routes or treating diversion as contracted volume.',
        'Nigel: review private-backup demand, road-freight split, restart dates and scenario assumptions. Trigger: before external presentation; registered expiry 12 November 2026.',
        'No independent review or business approval is inferred. Existing model forecast defaults and previous delivered workbooks are preserved.'
    ]
    if case:
        notes.insert(3,'CURRENT PLANNING CASE: User-directed domestic production 5.8bn L. The original 10.23bn plant estimate remains a reference only. Original mix allocates the override by product; the small total residual masks offsetting petrol and diesel differences. Do not infer verified production or product reconciliation from aggregate closure.')
        notes=[x.replace('The independent supply-plus-net-import estimate exceeds the demand estimate.','The original independent supply-plus-net-import estimate exceeded demand. The directed national total approximately balances, but its provisional product allocation creates offsetting differences.') for x in notes]
    (out/'analytical_findings.txt').write_text('\n'.join(notes),encoding='utf8')
    print(json.dumps(s,indent=2))
if __name__=='__main__':main()
