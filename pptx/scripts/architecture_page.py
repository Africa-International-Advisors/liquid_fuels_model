"""Native editable architecture diagram matching the current Python execution path."""
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE


def draw_architecture(slide, brand, cfg, text):
    def box(x,y,w,h,title,copy,size=14):
        s=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
        s.fill.solid();s.fill.fore_color.rgb=brand.white;s.line.color.rgb=cfg.DIVIDER_HEADER;s.line.width=Pt(.5)
        text(slide,title,x+.12,y+.12,w-.24,.4,15,True)
        text(slide,copy,x+.12,y+.64,w-.24,h-.7,size)
    def arrow(x,y,w=.25):
        s=slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,Inches(x),Inches(y),Inches(w),Inches(.16));s.fill.solid();s.fill.fore_color.rgb=brand.accent_primary;s.line.fill.background()
    text(slide,'One run = code version + assumption vintage + scenario',.55,1.83,11.5,.38,19,True)
    text(slide,'CLI coordinates the run, checks declared inputs and records provenance  |  src/lfm/cli.py + run.py',.55,2.27,11.5,.35,13)
    box(.55,2.88,2.1,2.72,'01  Inputs','Received Excel / sources\n\nVintaged YAML + CSV\nassumptions/2026/\n\nRegister + exceptions',12)
    arrow(2.68,4.05)
    box(2.96,2.88,2.12,2.72,'02  Resolve inputs','YamlDirectoryProvider\nloads files\n\nSnapshotProvider\nresolves inputs into\nmemory for the run',12)
    arrow(5.11,4.05)
    box(5.4,2.88,3.83,1.47,'03  Demand modules','Vehicles | Aviation | Power\nIndustrial* | Marine* | Agriculture*',13)
    box(5.4,4.51,3.83,1.09,'Domestic production','Refinery capacity x utilisation x availability x product yields',12)
    arrow(9.27,4.05)
    box(9.57,2.88,2.5,2.72,'04  Balance + save','Annual demand less\ndomestic production\n\nMonthly / annual CSVs\nBalance CSV\nprovenance.json',12)
    text(slide,'Pure calculation engine: src/lfm/model/\nShared geography, products and time dimensions',5.4,5.75,3.85,.58,11)
    text(slide,'Reporting consumes outputs\nExcel reports and PowerPoint',9.57,5.75,2.5,.58,11)
    text(slide,'*Held sectors use provisional baselines scaled by GDP. Current data: South Africa; scenarios: high_demand / low_demand.',.55,6.48,11.5,.26,11)
    text(slide,'Target extensions: independent H/M/L scenarios, available imports and WS5 infrastructure; see the Model Build section.',.55,6.83,11.5,.2,11,True)
