"""Integrated current-and-target architecture with explicit implementation status."""
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE


def draw_full_architecture(slide,brand,cfg,text):
    def label(copy,x,y,w,h,size=12,bold=False):
        s=text(slide,copy,x,y,w,h,size,bold)
        for p in s.text_frame.paragraphs:p.space_after=Pt(3)
        return s
    def box(x,y,w,h,head,body):
        s=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));s.fill.solid();s.fill.fore_color.rgb=brand.white;s.line.color.rgb=cfg.DIVIDER_HEADER;s.line.width=Pt(.5)
        label(head,x+.1,y+.12,w-.2,.47,14,True)
        label(body,x+.1,y+.56,w-.2,h-.62,11)
    label('Whole-model design | [E] existing, provisional  [H] held baseline  [P] planned  [A] engagement analysis',.55,1.83,11.5,.35,13,True)
    label('Shared dimensions: market / country x fuel x time x scenario | SA populated; SACU + priority Africa extensions [P]',.55,2.22,11.5,.32,12)
    xs=[.55,2.54,5.58,7.72,10.26];ws=[1.75,2.8,1.9,2.3,1.9]
    box(xs[0],2.8,ws[0],3.3,'01 Evidence',
        'Excel + reports\nMacro / population\nFleet + mileage\nEnergy + trade\nAssets + routes\nCustomers / access\n\nVintaged YAML/CSV [E]\nSource register [E]')
    box(xs[1],2.8,ws[1],2.15,'02 Demand [E/H]',
        'Vehicles: fleet, km, efficiency, EVs [E]\nAviation: GDP/capita + passengers [E]\nPower: MW, dispatch, efficiency [E]\nIndustry / marine / agriculture: GDP-scaled baselines [H]')
    box(xs[1],5.05,ws[1],1.05,'Domestic production [E]',
        'Capacity x utilisation x availability x product yields')
    box(xs[2],2.8,ws[2],3.3,'03 Fuel balance',
        'Demand vs domestic output [E]\n\nImport requirement, exports + stock changes [P]\n\nAvailable imports [P]\n\nRemaining fuel gap [P]')
    box(xs[3],2.8,ws[3],3.3,'04 Infrastructure [P]',
        'Ports / airports / terminals\n\nPipeline / rail / road links\nPower lines + power stations\nShared capacity + access\n\nReceipt / dispatch limits\nWorking tanks + stock cover\n\nFeasible flows + storage gaps')
    box(xs[4],2.8,ws[4],3.3,'05 Decisions',
        'Run outputs + provenance [E]\n\nCompetition + customer commitments [A]\n\nSA-wide Vopak opportunities [A]\nWalvis Bay case [A]\nAfrican priorities [A]')
    for x,w in zip(xs[:-1],ws[:-1]):
        s=slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,Inches(x+w+.025),Inches(4.26),Inches(.19),Inches(.14));s.fill.solid();s.fill.fore_color.rgb=brand.accent_primary;s.line.fill.background()
    label('Scenarios across the chain: two paired runs [E] -> independent H/M/L demand x available supply; M/M baseline [P]',.55,6.26,11.5,.3,12,True)
    label('Controls across the chain: input resolution, code/input hashes, checks and exceptions [E]; reconciliation, review and approval remain open.',.55,6.62,11.5,.32,11)
