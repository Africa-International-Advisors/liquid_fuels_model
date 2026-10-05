"""Format resolved assumptions and engine outputs; no duplicate model formulas."""
from lfm.assumptions import YamlDirectoryProvider
from lfm.run import Run
from lfm.model.demand.vehicles import _ev_penetration
from lfm.model.supply.flows import compute_supply, _utilisation_series
from lfm.scripts.compare_history import model_historical
from pptx.util import Inches


def draw_scenario_page(slide, index, table, text):
    provider=YamlDirectoryProvider()
    runs=[Run(vintage='2026',scenario=s) for s in ['high_demand','low_demand']]
    def value(domain,key,run): return provider.get(domain,key,run).value
    def series_value(domain,key,run):
        frame=value(domain,key,run)
        return float(frame[(frame.country=='ZAF') & (frame.period==2030)].value.iloc[0])
    def pair(domain,key,fmt):
        return [fmt(series_value(domain,key,r)) for r in runs]
    if index==21:
        text(slide,'South Africa | selected 2030 drivers + 2024 sector anchors; full inventory separate; M unset',.55,1.78,11.45,.35,15)
        rows=['| Demand driver | H demand | M demand | L demand | Fuel affected / mechanism |']
        values=[
            ('GDP per capita, 2015 ZAR',pair('macro','gdp_per_capita',lambda x:f'{x:,.0f}'),'Petrol, diesel, jet / GDP links'),
            ('EV share of new vehicles',[f"{_ev_penetration(value('vehicles','ev_scurve',r)['ZAF'],2030):.2%}" for r in runs],'Petrol, diesel / ICE additions'),
            ('Efficiency gain: petrol / diesel',[f"{series_value('vehicles','efficiency_improvement.gasoline',r):.1%} / {series_value('vehicles','efficiency_improvement.diesel',r):.1%}" for r in runs],'Petrol, diesel / new cohorts'),
            ('Departing passengers, million',pair('aviation','passenger_departures',lambda x:f'{x/1e6:.2f}'),'Jet / shared passenger path'),
            ('OCGT load factor',pair('generation','load_factor',lambda x:f'{x:.1%}'),'Diesel / power generation'),
        ]
        for domain,label in [('industrial','Industry'),('agriculture','Agriculture')]:
            anchor=value(domain,'base_year_volume',runs[0])['ZAF']
            elasticity=value(domain,'elasticity',runs[0])['ZAF']
            baseline=f"{float(anchor['value'])/1e9:.2f} bn L"
            values.append((f'{label}: 2024 anchor',[baseline,baseline],f'Diesel / GDP elasticity {elasticity:g}'))
        for name,vals,link in values:
            rows.append(f'| {name} | {vals[0]} | Unset | {vals[1]} | {link} |')
        table(slide,rows,y=2.15,height=2.85,widths=[3.1,1.65,1.35,1.65,3.9],size=13)
        text(slide,'Resulting demand, billion litres in 2030 (provisional)',.55,5.1,11.45,.3,16,True)
        totals=[model_historical(r,provider).query("period==2030 and country=='ZAF'").iloc[0] for r in runs]
        outputs=['| Output | H demand | M demand | L demand | Coverage |']
        for label,key,cov in [('Petrol','petrol_95','Petrol 95'),('Diesel','diesel_50ppm','50 ppm; marine 500 ppm excluded'),('Jet','jet_a1','Jet A1')]:
            outputs.append(f'| {label} | {totals[0][key]/1e9:.2f} | Unset | {totals[1][key]/1e9:.2f} | {cov} |')
        output_table=table(slide,outputs,y=5.5,height=1.0,widths=[3.1,1.65,1.35,1.65,3.9],size=12)
        for row in output_table.table.rows:
            for cell in row.cells:
                cell.margin_top=cell.margin_bottom=Inches(.015)
        text(slide,'Industry/agriculture anchors are provisional shared inputs, not 2030 forecasts. Annual km: 17k / 28k / 70k (car / LCV / HCV).',.55,6.65,11.45,.35,11)
    else:
        text(slide,'South Africa | sources reviewed 2 Oct 2026 | utilisation columns are 2030 model assumptions',.55,1.78,11.45,.35,14)
        capacities=value('supply','refinery_capacity',runs[0])['ZAF']
        statuses={
            'enref':'Terminal conversion announced; Oct status unverified [1]',
            'sapref':'Redevelopment programme [2]',
            'natref':'Disruption reported; Oct availability unverified [3]',
            'sasol':'Secunda operating in FY2026 [4]',
            'astron':'Mar maintenance; Oct availability unverified [5]',
            'petrosa':'GTL reinstatement planned [6]',
        }
        rows=['| Asset | Latest sourced status* | Model capacity, kbpd | 2030 H util. | 2030 M util. | 2030 L util. |']
        for name in ['enref','sapref','natref','sasol','astron','petrosa']:
            utils=[float(_utilisation_series(value('supply','refinery_utilisation',r),'ZAF',name).loc[2030]) for r in runs]
            rows.append(f'| {name.upper()} | {statuses[name]} | {capacities[name]:g} | {utils[0]:.1%} | Unset | {utils[1]:.1%} |')
        status_table=table(slide,rows,y=2.16,height=2.48,widths=[1.15,3.9,1.7,1.65,1.65,1.6],size=11.5)
        for row in status_table.table.rows:
            for cell in row.cells:
                cell.margin_top=cell.margin_bottom=Inches(.015)
        text(slide,'Domestic output, bn litres | 90% availability; asset-specific product yields',.55,5.04,11.45,.3,14,True)
        supplies=[compute_supply(provider,r).query("period==2030 and country=='ZAF'").set_index('refinery_product').supply_litres for r in runs]
        outputs=['| Product | H domestic | M domestic | L domestic | Available imports |']
        for label,key in [('Petrol','gasoline'),('Diesel','diesel'),('Jet','jet_a1')]:
            outputs.append(f'| {label} | {supplies[0][key]/1e9:.2f} | Unset | {supplies[1][key]/1e9:.2f} | Not modelled |')
        output_table=table(slide,outputs,y=5.4,height=.8,widths=[3.1,2.15,2.15,2.1,2.15],size=11)
        for row in output_table.table.rows:
            for cell in row.cells:
                cell.margin_top=cell.margin_bottom=Inches(.015)
        citations=[
            ('[1] Engen, Apr 2021','https://engen-admin.engen.co.za/storage/app/uploads/public/60f/043/f7b/60f043f7b4f71965269047.pdf'),
            ('[2] CEF, 9 Sep 2026','https://cefgroup.co.za/2026/09/10/cef-outlines-roadmap-to-rebuild-south-africas-refining-capacity-and-unlock-economic-opportunities-in-durban-south/'),
            ('[3] Sasol, 1 Sep 2026','https://sasol.com/media-centre/media-releases/natref-operational-update'),
            ('[4] Sasol, 1 Sep 2026','https://www.sasol.com/media-centre/media-releases/sasol-delivers-stronger-fy2026-performance-and-strengthens-financial-resilience'),
            ('[5] DMPR, 10 Mar 2026','https://www.gov.za/news/media-statements/mineral-and-petroleum-resources-fuel-supply-and-prices-10-mar-2026'),
            ('[6] CEF, 23 Sep 2026','https://cefgroup.co.za/2026/09/23/cef-group-presents-five-year-financial-performance-governance-outcomes-and-sanpc-development-progress-to-parliament/'),
        ]
        for i,(label,url) in enumerate(citations):
            shape=text(slide,label,.55+i*1.95,6.38,1.9,.25,8.5)
            for p in shape.text_frame.paragraphs:
                for run in p.runs:
                    run.hyperlink.address=url;run.font.underline=True
        text(slide,'*Published evidence, not confirmation of today’s availability. H/L production remains linked to demand; M and imports are unset.',.55,6.75,11.45,.3,10)
