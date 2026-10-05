"""Four-part executive summary of the agreed engagement argument."""


def draw_summary(slide,text,row_table):
    text(slide,"Where do changing liquid-fuel flows across South Africa, Walvis Bay and priority African markets create opportunities for Vopak?",.55,1.83,11.5,.64,20,True)
    rows=[
        ('01  Project question','Where can changing South African liquid-fuel balances support Vopak storage and handling services; does Walvis Bay offer a credible opportunity; which African markets merit follow-up?'),
        ('02  Analytical specifications','Map petrol, diesel and jet flows across South African ports, inland markets and infrastructure; assess customer demand, competing terminal operators, usable capacity and commercial access.'),
        ('03  Model build','Build detailed South African fuel and infrastructure calculations; add focused Namibia/Walvis Bay analysis and SACU/African screening. Apply results to Vopak assets and growth options.'),
        ('04  Delivery approach','Over six weeks, develop the board narrative: South African market changes, Vopak asset and growth opportunities, Walvis Bay and African priorities.'),
    ]
    row_table(slide,rows,y=2.65,height=3.65,size=15)
    text(slide,'The test: where can Vopak serve sustained customer demand through its existing assets or credible growth options?',.55,6.58,11.5,.35,14,True)
