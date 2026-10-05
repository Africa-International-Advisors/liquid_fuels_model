"""Evidence-qualified model assessment with cell and code citations."""


def draw_model_assessment(slide, text, table):
    text(slide,'Use Excel as a provisional historical reference; validate Python before relying on its forecasts.',.55,1.82,11.5,.62,19,True)
    rows=[
        '| Test | Excel evidence | Python evidence | Assessment / next check |',
        '| Petrol | 9.05 bn litres recorded; 9.44m vehicles. Litres/vehicle is inferred from the total. [1] | 7.93 bn litres; cohort fleet 4.68m. Mileage, fuel use and scrappage include provisional inputs. [2] | No accuracy winner. Reconcile fleet coverage and validate kilometres and fuel consumption. |',
        '| Diesel | 11.88 bn litres total; power 0.50; remaining 11.38 includes non-road demand. [1] | 15.28 bn litres; power 3.58 plus industrial 2.50 and agriculture 0.70 placeholders. [2,3] | Python uplift is not validated. Check power history and sector overlap before accepting it. |',
        '| Jet | Recorded demand 1.87; regression calculates 1.60 bn litres. [1] | Same regression result: 1.60 bn litres, matching Excel to numerical precision. [3] | Translation agrees; accuracy is unproven. Check product coverage and fit to observed demand. |',
    ]
    table(slide,rows,x=.55,y=2.65,height=2.95,widths=[.9,3.05,3.7,4.0],size=13)
    text(slide,'Decision gate: compare both against independent, like-for-like actuals across several historical years; then test forecasts on held-out years. [4,5]',.55,5.79,11.5,.55,14,True)
    refs=[
        '[1] Inherited workbook: Gasoline - DemandSupply K29/T29/X29; Diesel - DemandSupply K30/T30/M30; Jet - DemandSupply J23; fJetFuel H24.',
        '[2] assumptions/2026/vehicles.yaml, generation.yaml, industrial.yaml, agriculture.yaml; src/lfm/model/demand/vehicles.py.',
        '[3] src/lfm/reporting/reconciliation.py; pptx/output/data/driver_reconciliation.json (2024, high_demand).',
        '[4] GATE_CHECKLIST.md: independent review and business approval outstanding. [5] DMRE SA Fuel Sales Volume portal: external benchmark to reconcile, not yet validated here.',
    ]
    for i,ref in enumerate(refs):
        shape=text(slide,ref,.55,6.42+i*.135,11.55,.18,7.5)
        if i==3:
            for run in shape.text_frame.paragraphs[0].runs:
                run.hyperlink.address='https://www.energy.gov.za/files/media/media_SAVolumes.html'
