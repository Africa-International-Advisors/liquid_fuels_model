"""Build the agreed kickoff pages using the supplied Vopak master and layouts."""
from pathlib import Path
import io
import json
import re
import sys
import os
from copy import deepcopy

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_TICK_LABEL_POSITION
from appendix_data import current_comparison
from coverage_map import draw_coverage_map
from scenario_pages import draw_scenario_page
from imports_page import draw_imports
from results_pages import draw_results
from review_pages import draw_inventory, draw_excel
from reconciliation_waterfalls import draw_waterfalls
from network_sequence import draw_network_stage
from infrastructure_reference import draw_infrastructure_reference
from full_assumption_inventory import add_inventory
from asset_maps import draw_asset_page
from logistics_map import draw_logistics_map
from pipeline_network import draw_pipeline_network
from about_page import draw_about
from client_page import draw_client
from client_financials import draw_financials
from client_economics import draw_client_economics
from client_strategy import draw_client_strategy
from executive_summary import draw_summary
from full_architecture import draw_full_architecture
from workstream_overview import draw_workstreams
from cadence_page import draw_cadence
from balance_opportunity_page import draw_balance_opportunity
from infrastructure_assumptions import draw_infrastructure_assumptions
from gas_map import draw_gas_map
from demand_stacks import draw_demand_stacks
from model_assessment import draw_model_assessment
from architecture_page import draw_architecture
from delivery_gantt import draw_gantt
from infrastructure_pages import draw_infrastructure
from lfm.reporting.reconciliation import build_reconciliation
from brand_pptx import BrandStyle, add_themed_slide, remove_all_slides_cleanly
from brand_pptx import _strip_table_style, cell_bottom_rule

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from brand_configs import vopak as cfg

brand = BrandStyle.from_module(cfg)
reconciliation = build_reconciliation(ROOT.parent / 'external/sources/Liquid Fuels Model - Supply Demand, 2025 - Reatile Copy.xlsx', ROOT / 'output/data')
prs = Presentation(ROOT / cfg.SOURCE_TEMPLATE)
cover_panel = deepcopy(prs.slides[0].shapes[0]._element)
cover_pictures = [(s.image.blob, s.left, s.top, s.width, s.height)
                  for s in prs.slides[0].shapes if s.shape_type == 13]
remove_all_slides_cleanly(prs)
# Remove unfilled instructional footer copy in the inherited working master.
for master in prs.slide_masters:
    for shape in master.shapes:
        if shape.has_text_frame and ('Click to edit' in shape.text or shape.name == 'Text Placeholder 6'):
            shape.text_frame.clear()

def text(slide, value, x, y, w, h, size=21, bold=False, color=None):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(.02)
    tf.margin_top = tf.margin_bottom = 0
    for i, line in enumerate(value.split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.name = cfg.THEME_FONT
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = color or brand.ink
        p.space_after = Pt(8)
    return shape

def section_chevrons(slide, active):
    labels = ['1  About', '2  Analytical specifications',
              '3  Model build', '4  Delivery approach']
    for i, label in enumerate(labels):
        shape = slide.shapes.add_shape(
            MSO_SHAPE.CHEVRON, Inches(.5 + i * 2.93), Inches(.08),
            Inches(2.86), Inches(.42))
        shape.name = f'Section navigation {i + 1}'
        shape.adjustments[0] = .12
        shape.fill.solid()
        shape.fill.fore_color.rgb = brand.accent_primary if i == active else brand.grey_fill
        shape.line.fill.background()
        tf = shape.text_frame
        tf.clear()
        tf.word_wrap = False
        tf.margin_left = tf.margin_right = Inches(.18)
        tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = label
        p.alignment = PP_ALIGN.CENTER
        p.font.name = cfg.THEME_FONT
        p.font.size = Pt(13)
        p.font.bold = i == active
        p.font.color.rgb = brand.white if i == active else brand.accent_primary

def table(slide, lines, y=1.65, height=4.5, x=.5, widths=None, size=None):
    rows = [[c.strip() for c in line.strip('|').split('|')] for line in lines
            if not re.match(r'^\|[\s:|-]+\|$', line)]
    widths = widths or ([.95,3.5,3.6,3.6] if len(rows[0]) == 4 else
                        [3.7,7.95] if len(rows[0]) == 2 else [2.7,4.2,4.75])
    shape = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(sum(widths)), Inches(height))
    tbl = shape.table
    _strip_table_style(tbl)
    for col, width in zip(tbl.columns, widths):
        col.width = Inches(width)
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = tbl.cell(r,c)
            cell.text = value
            cell.margin_left = cell.margin_right = Inches(.16)
            cell.margin_top = cell.margin_bottom = Inches(.06)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = brand.white
            cell_bottom_rule(cell, color=cfg.DIVIDER_HEADER if r == 0 else cfg.DIVIDER_BODY,
                             w_pt=.35 if r == 0 else .25)
            for p in cell.text_frame.paragraphs:
                p.font.name = cfg.THEME_FONT
                p.font.size = Pt(size or (18 if len(rows) >= 6 else 20))
                p.font.bold = r == 0
                p.font.color.rgb = brand.ink
    return shape

def native_icon(slide, kind, x, y):
    """Small editable PowerPoint symbols; no raster icons or font glyph dependencies."""
    def shape(st, dx, dy, w, h, fill=False):
        s = slide.shapes.add_shape(st, Inches(x+dx), Inches(y+dy), Inches(w), Inches(h))
        s.name = f'{kind} icon'
        s.fill.solid() if fill else s.fill.background()
        if fill:
            s.fill.fore_color.rgb = brand.ink
        s.line.color.rgb = brand.ink
        s.line.width = Pt(1.2)
        return s
    if kind == 'context':
        shape(MSO_SHAPE.RECTANGLE, .02, 0, .3, .38)
        for dy in (.10,.18,.26):
            shape(MSO_SHAPE.RECTANGLE,.08,dy,.18,.012,True)
    elif kind == 'challenge':
        shape(MSO_SHAPE.ISOSCELES_TRIANGLE,0,0,.4,.36)
        text(slide,'!',x+.13,y+.10,.14,.23,13,True)
    elif kind == 'direction':
        shape(MSO_SHAPE.RIGHT_ARROW,0,.06,.4,.27)
    elif kind == 'market':
        for dx,h in ((0,.16),(.13,.26),(.26,.38)):
            shape(MSO_SHAPE.RECTANGLE,dx,.38-h,.075,h,True)
    elif kind == 'terminal':
        shape(MSO_SHAPE.CAN,0,.07,.17,.3)
        shape(MSO_SHAPE.CAN,.22,0,.17,.37)
    elif kind == 'question':
        shape(MSO_SHAPE.OVAL,0,0,.4,.4)
        s=text(slide,'?',x+.06,y+.025,.28,.34,20,True)
        s.text_frame.paragraphs[0].alignment=PP_ALIGN.CENTER

def row_table(slide, rows, y=1.85, height=4.5, widths=(3,8.65), icons=False, size=21):
    s = slide.shapes.add_table(len(rows),2, Inches(.5), Inches(y), Inches(11.65), Inches(height))
    t = s.table
    _strip_table_style(t)
    for c,w in zip(t.columns,widths): c.width=Inches(w)
    for r,row in enumerate(rows):
        for c,value in enumerate(row):
            cell=t.cell(r,c)
            cell.text=value
            cell.margin_left=Inches(.75 if icons and c==0 else .16)
            cell.margin_right=Inches(.16)
            cell.margin_top=cell.margin_bottom=Inches(.12)
            cell.vertical_anchor=MSO_ANCHOR.MIDDLE
            cell.fill.solid(); cell.fill.fore_color.rgb=brand.white
            cell_bottom_rule(cell,color=cfg.DIVIDER_BODY,w_pt=.25)
            for p in cell.text_frame.paragraphs:
                p.font.name=cfg.THEME_FONT; p.font.size=Pt(size)
                p.font.bold=c==0; p.font.color.rgb=brand.ink
        if icons:
            native_icon(slide,['context','challenge','direction'][r],.7,y+(r+.5)*height/len(rows)-.19)
    return s

raw = (ROOT / 'story/analyst-kickoff-scr.md').read_text(encoding='utf-8')
sections = re.findall(r'^## (\d+)\. ([\s\S]*?)(?=^## |\Z)', raw, flags=re.M)
inventory_only = os.environ.get('LFM_INVENTORY_ONLY') == '1'
if inventory_only:
    sections = []
inventory_count = 0
for index, section in sections:
    index = int(index)
    title, body = section.split('\n', 1)
    note_start = re.search(r'^(Speaker note:|Source note:|Sources?:)', body, re.M)
    notes = body[note_start.start():].strip() if note_start else ''
    body = body[:note_start.start()] if note_start else body
    body = re.sub(r'\nLayout:.*?\n\n', '\n', body, flags=re.S).strip()
    footer_match = re.search(r'^Footer: (.*)$', body, re.M)
    footer = footer_match.group(1) if footer_match else ''
    if footer_match:
        body = body[:footer_match.start()].strip()
    if index == 33:
        slide = add_themed_slide(prs, 'Header only', brand=brand, title=title, slide_number_idx=12)
        for shape in list(slide.shapes):
            if shape.is_placeholder:
                shape._element.getparent().remove(shape._element)
        draw_about(slide,prs,brand,text)
        for logo in slide.slide_layout.slide_master.shapes:
            if logo.shape_type == 13 and logo.top > Inches(7):
                slide.shapes.add_picture(io.BytesIO(logo.image.blob),logo.left,logo.top,logo.width,logo.height)
        text(slide,str(len(prs.slides)),12.13,7.16,.22,.2,9)
    elif index in (1,13,40):
        slide = add_themed_slide(prs, '1_Title', brand=brand)
        for shape in list(slide.shapes):
            if shape.is_placeholder:
                shape._element.getparent().remove(shape._element)
        # Website-inspired split cover on the supplied title layout.
        panel=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,prs.slide_width,prs.slide_height)
        panel.fill.solid(); panel.fill.fore_color.rgb=brand.accent_primary; panel.line.fill.background()
        from PIL import Image
        photo=ROOT / ('assets/cover-options/durban.jpg' if index==1 else 'assets/cover-options/lesedi.jpg')
        pw,ph=Image.open(photo).size
        split=prs.slide_width/2
        pic=slide.shapes.add_picture(str(photo),split,0,width=prs.slide_width-split,height=prs.slide_height)
        source_ratio=pw/ph; target_ratio=(prs.slide_width-split)/prs.slide_height
        if source_ratio>target_ratio:
            pic.crop_left=pic.crop_right=(1-target_ratio/source_ratio)/2
        else:
            pic.crop_top=pic.crop_bottom=(1-source_ratio/target_ratio)/2
        slide.shapes.add_picture(str(ROOT / 'assets/vopak-logo-white.png'),Inches(.55),Inches(.5),width=Inches(2.15))
        text(slide,'Liquid fuels\ndemand and supply\nmodel' if index==1 else 'Appendix' if index==13 else 'Agree priorities\nand next steps',.65,2.7,5.15,1.7,31 if index in (1,40) else 36,False,brand.white)
        rule=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(.65),Inches(4.65),Inches(5.7),Inches(4.65))
        rule.line.color.rgb=brand.white; rule.line.width=Pt(.6)
        text(slide,'Analyst kickoff' if index==1 else 'Evidence and model detail' if index==13 else 'Discussion',.65,5.05,5.0,.7,21,False,brand.white)
        if index==1:
            text(slide,'Coverage: SACU + priority African regions',.65,5.73,5.0,.4,13,color=brand.white)
        text(slide,'2 October 2026',.65,6.23,5.0,.3,13,color=brand.white)
        text(slide,'Internal working discussion',.65,6.62,5.0,.3,12,color=brand.white)
        terminal='durban' if index==1 else 'lesedi'
        credit=text(slide,f'Photo source: Royal Vopak | Terminal {terminal.title()} | vopak.com',.65,7.0,5.2,.18,8,color=brand.white)
        credit.name='Photo source credit'
        credit.click_action.hyperlink.address=f'https://www.vopak.com/terminals/vopak-terminal-{terminal}'
        for paragraph in credit.text_frame.paragraphs:
            paragraph.alignment=PP_ALIGN.LEFT
        slide.notes_slide.notes_text_frame.text=f'Cover image: Vopak Terminal {terminal.title()}, from https://www.vopak.com/terminals/vopak-terminal-{terminal}; selected by user. Primary blue #0A2373 verified against website CSS on 2 October 2026. Original supplied template preserved.'

    else:
        slide = add_themed_slide(prs, 'Header only', brand=brand, title=title, slide_number_idx=12)
        title_shape = slide.shapes.title
        title_shape.left, title_shape.top = Inches(.5), Inches(.64)
        title_shape.width, title_shape.height = Inches(11.55), Inches(.9)
        for p in title_shape.text_frame.paragraphs:
            p.font.name = cfg.THEME_FONT
            p.font.size = Pt(27 if len(title) > 85 else 29 if len(title) > 47 else 32)
            p.font.bold = True
            p.font.color.rgb = brand.ink
        if index in (7,28) or (index >= 14 and index not in (21,22,29,30,34,35,36,37,38,39,45,52,53,54,55,56,57)):
            text(slide, 'APPENDIX  |  Current evidence and build readiness', .5, .12, 11.5, .35, 13, True)
        else:
            section_chevrons(slide, -1 if index==35 else 0 if index in (34,53,54,55,56,57) else 3 if index==30 else 2 if index in (28,29,36,37) else 1 if index in (21,22,38,39,45) else 0 if index <= 3 else 1 if index <= 5 else 2 if index <= 8 else 3)
        table_lines = [line for line in body.splitlines() if line.startswith('|')]
        if index in (23,26,49,31,50,24,25):
            draw_network_stage(slide,{23:0,26:1,49:2,31:3,50:4,24:5,25:6}[index],ROOT,brand,cfg,text,table)
        elif index in (53,54,55):
            draw_financials(slide,index,ROOT,brand,text,table)
        elif index == 57:
            draw_client_strategy(slide,brand,text)
        elif index == 56:
            draw_client_economics(slide,ROOT,brand,text)
        elif index == 51:
            draw_infrastructure_reference(slide,text,brand,cfg)
        elif index == 52:
            draw_cadence(slide,text,table)
        elif index == 5:
            draw_balance_opportunity(slide,text,table)
        elif index == 9:
            draw_gantt(slide,text,brand,cfg)
        elif index == 45:
            draw_inventory(slide,text,table)
        elif index == 46:
            draw_excel(slide,text,table,brand)
        elif index == 47:
            draw_waterfalls(slide,text,brand,cfg,reconciliation)
        elif index in (41,42,43,44,48):
            draw_results(slide,index,ROOT,text)
        elif index == 39:
            draw_imports(slide,ROOT,text,table)
        elif index == 38:
            draw_infrastructure_assumptions(slide,text,table)
        elif index == 37:
            draw_workstreams(slide,brand,text,table)
        elif index == 36:
            draw_full_architecture(slide,brand,cfg,text)
        elif index == 35:
            draw_summary(slide,text,row_table)
        elif index == 34:
            draw_client(slide,text,table)
        elif index == 31:
            draw_logistics_map(slide,ROOT,brand,cfg,text,roads_only=True)
        elif index == 32:
            draw_pipeline_network(slide,brand,cfg,text)
        elif index in (29,30):
            draw_infrastructure(slide,index,brand,cfg,text,table)
        elif index == 28:
            draw_architecture(slide,brand,cfg,text)
        elif index == 27:
            draw_model_assessment(slide,text,table)
        elif index == 26:
            draw_gas_map(slide,ROOT,brand,cfg,text)
        elif index == 25:
            draw_logistics_map(slide,ROOT,brand,cfg,text)
        elif index in (23,24):
            draw_asset_page(slide,index,ROOT,brand,cfg,text,table)
        elif index in (21,22):
            draw_scenario_page(slide,index,table,text)
        elif index == 20:
            draw_coverage_map(slide, ROOT, brand, cfg, text)
        elif index in (17,18,19):
            fuel = {17:'petrol',18:'diesel',19:'jet'}[index]
            r = reconciliation[fuel]
            effects = sorted(r['effects'].items(), key=lambda item: abs(item[1]))
            data = CategoryChartData()
            data.categories = [k for k,v in effects]
            data.add_series('Contribution to gap', [0.0 if abs(v)<.01 else v/1e9 for k,v in effects])
            text(slide, '2024 reconciliation | contribution in billion litres', .55, 1.83, 11.4, .35, 17)
            chart = slide.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(.5), Inches(2.5), Inches(7.25), Inches(3.7), data).chart
            chart.has_legend = False
            chart.has_title = False
            chart.category_axis.tick_label_position = XL_TICK_LABEL_POSITION.LOW
            chart.category_axis.tick_labels.font.size = Pt(12)
            chart.category_axis.tick_labels.font.name = cfg.THEME_FONT
            limit = {17:7,18:4,19:.3}[index]
            chart.value_axis.minimum_scale = -limit
            chart.value_axis.maximum_scale = limit
            chart.value_axis.tick_labels.font.size = Pt(11)
            chart.value_axis.tick_labels.number_format = '0.0'
            chart.value_axis.has_major_gridlines = True
            chart.value_axis.major_gridlines.format.line.color.rgb = cfg.DIVIDER_BODY
            chart.value_axis.major_gridlines.format.line.width = Pt(.25)
            series = chart.series[0]
            series.format.fill.solid()
            series.format.fill.fore_color.rgb = brand.accent_primary
            series.format.line.fill.background()
            series.invert_if_negative = False
            plot = chart.plots[0]
            plot.has_data_labels = True
            plot.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
            plot.data_labels.number_format = '+0.00;-0.00;0.00'
            plot.data_labels.font.size = Pt(12)
            plot.data_labels.font.color.rgb = brand.ink
            for point, (_, value) in zip(series.points, effects):
                label = point.data_label
                label.position = XL_LABEL_POSITION.INSIDE_END if value < -.01 else XL_LABEL_POSITION.OUTSIDE_END
                label.has_text_frame = True
                label.text_frame.text = f'{value/1e9:+.2f}' if abs(value) >= .01 else '0.00'
                label.font.size = Pt(12)
                label.font.color.rgb = brand.white if value < -.01 else brand.ink
                for paragraph in label.text_frame.paragraphs:
                    paragraph.font.name = cfg.THEME_FONT
                    paragraph.font.size = Pt(12)
                    paragraph.font.color.rgb = brand.white if value < -.01 else brand.ink
                    for run in paragraph.runs:
                        run.font.name = cfg.THEME_FONT
                        run.font.size = Pt(12)
                        run.font.color.rgb = brand.white if value < -.01 else brand.ink
            text(slide, f"Net difference: {(r['python']-r['observed'])/1e9:+.3f} bn litres", 8.0, 2.35, 4.1, .45, 19, True)
            if index == 17:
                rows = ['| Measure | Excel | Python |',
                        f"| Fleet, million | {r['excel_fleet']/1e6:.2f} | {r['python_fleet']/1e6:.2f} |",
                        f"| Litres / vehicle | {r['excel_litres_per_vehicle']:,.0f} | {r['python_litres_per_vehicle']:,.0f} |"]
                table(slide,rows,x=8,y=3.0,height=1.65,widths=[1.65,1.2,1.25],size=13)
                copy = 'Check opening stock, scrappage and fleet coverage; then mileage, fuel economy and segment mix. Excel stock includes other self-propelled vehicles.'
            elif index == 18:
                rows = ['| Power basis | Excel | Python |',
                        f"| Demand, bn L | {r['excel_power']/1e9:.2f} | {r['python_power']/1e9:.2f} |",
                        f"| Load factor* | {r['equivalent_excel_load_factor']:.1%} | {r['python_load_factor']:.1%} |"]
                table(slide,rows,x=8,y=3.0,height=1.65,widths=[1.65,1.2,1.25],size=13)
                copy = '*Excel equivalent calculated at Python capacity and efficiency. Review historical dispatch / scenario mapping and possible sector overlap.'
            else:
                rows = ['| Demand, bn L | Value |',
                        f"| Excel recorded | {r['observed']/1e9:.3f} |",
                        f"| Excel calculated | {r['excel_calculated']/1e9:.3f} |",
                        f"| Python calculated | {r['python']/1e9:.3f} |"]
                table(slide,rows,x=8,y=3.0,height=1.85,widths=[2.9,1.2],size=14)
                copy = 'Same GDP per capita, 17 million passengers and regression coefficients. Review fit and fuel definitions, rather than changing the Python translation.'
            text(slide,copy,8.0,5.05,4.1,1.25,14)
        elif index == 14:
            draw_demand_stacks(slide,ROOT,brand,cfg,text,reconciliation)
        elif table_lines:
            if index==4:
                table(slide,table_lines,y=1.85,height=4.55,widths=[1.9,4.85],size=17)
                divider = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(7.42), Inches(1.95), Inches(7.42), Inches(6.45))
                divider.name = 'Requirements and scenario matrix divider'
                divider.line.color.rgb = cfg.DIVIDER_HEADER
                divider.line.width = Pt(.5)
                text(slide,'Demand-supply matrix',7.6,1.95,4.55,.4,20,True)
                text(slide,'Rows: demand  /  Columns: supply',7.6,2.45,4.55,.4,13)
                matrix=table(slide,[
                    '| Demand / Supply | H | M | L |',
                    '| H | H/H | H/M | H/L |',
                    '| M | M/H | M/M | M/L |',
                    '| L | L/H | L/M | L/L |',
                ],x=7.6,y=3.05,height=2.35,widths=[1.45,1,1,1],size=16)
                cell=matrix.table.cell(2,2)
                cell.fill.fore_color.rgb=brand.grey_fill
                for p in cell.text_frame.paragraphs: p.font.bold=True
                for row, col, code, label in [(1,3,'H/L','Tight supply'), (2,2,'M/M','Baseline'), (3,1,'L/H','Ample supply')]:
                    cell = matrix.table.cell(row,col)
                    cell.margin_left = cell.margin_right = Inches(.02)
                    cell.fill.fore_color.rgb = brand.grey_fill
                    cell.text = code + '\n' + label
                    for i, p in enumerate(cell.text_frame.paragraphs):
                        p.font.name = cfg.THEME_FONT
                        p.font.size = Pt(15 if i == 0 else 10)
                        p.font.bold = True
                        p.font.color.rgb = brand.ink
                        p.alignment = PP_ALIGN.CENTER
                        p.space_after = Pt(0)
                text(slide,'H = High   M = Medium   L = Low',7.6,6.0,4.5,.28,13)
                text(slide,'Supply: domestic production + available imports',7.6,6.32,4.5,.25,11.5)
            else:
                table(slide, table_lines, y=1.85, height=4.6 if index==9 or index>=15 else 4.45,
                      widths=[2.1,4.55,5.0] if index>=15 else [3,8.65] if index==8 else None,
                      size=17 if index in (5,8) else 15 if index>=15 else 16 if index==9 else None)
            remaining = '\n'.join(line for line in body.splitlines() if not line.startswith('|')).strip()
            if remaining:
                text(slide, remaining, .55, 5.85, 11.45, .95, 18, color=brand.ink)
        elif index in (2,6,7,12):
            blocks = body.split('\n\n')
            rows = [(b.partition('\n')[0], b.partition('\n')[2]) for b in blocks]
            row_table(slide, rows, height=4.55 if index!=12 else 4.8,
                      icons=index in (2,6), size=19 if index in (2,6,7) else 20 if index==12 else 21)
        elif index == 11:
            responsibility = [
                '| Role | Working responsibilities |',
                '| Manish - Analyst | Sources evidence, develops calculations and records checks; available 100%. |',
                '| Nigel - Modelling lead | Reviews methodology, priorities and interpretation. |',
                '| Henry - Reviewer | Challenges the model before formal use. |',
            ]
            completion = [
                '| Completion criterion | Required evidence |',
                '| Traceability | A traceable source and assumption owner. |',
                '| Calculation and check | An explainable calculation and a relevant check. |',
                '| Review record | Documented limitations and review findings. |',
            ]
            for lines,y in [(responsibility,1.85),(completion,4.18)]:
                s=table(slide,lines,y=y,height=2.12)
                for row in s.table.rows:
                    for cell in row.cells:
                        cell.margin_top=cell.margin_bottom=Inches(.06)
                        for p in cell.text_frame.paragraphs: p.font.size=Pt(18)
        elif index == 3:
            blocks = body.split('\n\n')
            native_icon(slide,'question',.6,1.94)
            text(slide, blocks[0].replace('\n',' '), 1.18, 1.85, 10.9, 1.7, 21, False, brand.ink)
            for n, block in enumerate(blocks[1:]):
                heading, copy = block.split('\n', 1)
                native_icon(slide,'market' if n==0 else 'terminal',.58+n*6,4.14)
                text(slide, f'{n+1:02d}  {heading}', 1.12+n*6, 4.12, 4.8, .5, 21, True, brand.ink)
                text(slide, copy, .55+n*6, 4.85, 5.3, 1.7, 18)
        else:
            blocks = body.split('\n\n')
            step = {2:1.5,6:1.5,7:1.5,11:2.55,12:1.65}.get(index,1.5)
            for n, block in enumerate(blocks):
                heading, _, copy = block.partition('\n')
                y = [1.85,4.35,5.65][n] if index == 12 else 1.85+n*step
                if index in (2,6):
                    text(slide, heading, .55, y, 2.4, .8, 24, True, brand.ink)
                    text(slide, copy.replace('\n',' '), 3.05, y, 8.9, 1.3, 23)
                else:
                    text(slide, heading, .55, y, 11.4, .45, 22, True, brand.ink)
                    text(slide, copy, .55, y+.52, 11.4, 1.8 if index==12 and n==0 else step-.55, 20 if index in (11,12) else 22)
        if footer and index not in (5,9):
            text(slide, footer, .55, 6.62, 11.4, .4, 12 if index==4 else 14, True, brand.ink)
        sources = {
            52: 'Source: Confirmed team roles; proposed engagement cadence; Monday HG check-in planned by user. Recurring slots and client dates to agree.',
            49: 'Source: TNPA port inventory and existing sources; Natural Earth. Schematic locations; fuel handling to validate.',
            50: 'Source: TFR corridor overview; Department of Transport rail/port corridors; Natural Earth. Route presence is not fuel service.',
            51: 'Source: WS5 infrastructure input contract and proposed build; WS2 model interfaces; GATE_CHECKLIST.md. Engine not yet implemented.',
            45: "Source: assumptions/2026 YAML and CSV declarations; src/lfm/model/demand; assumption register. Input metadata unassessed; 2026 draft.",
            46: "Source: Inherited Liquid Fuels Model workbook; actual sheet names and formulas including fImports external links. Schematic calculation flow.",
            47: "Source: lfm.reporting.reconciliation; Gasoline K29/T29/X29; Diesel K30/T30/M30; fJetFuel H24; Jet DemandSupply J23. Provisional.",
            **{n: "Source: Saved Python 2026 high_demand / low_demand runs, 2 Oct 2026; balance_annual.csv; exact run paths in current-results-runs.json. 43 open exceptions." for n in (41,42,43,44,48)},
            39: 'Source: Inherited workbook fImports D94/D58/D22 (2022), M102/V102, M66/V66, M30/V30 (2030); Python supply.flows.compute_balance. Provisional.',
            2: 'Source: AIA strategy support proposal, August 2026, pp. 7-12',
            3: 'Source: Agreed engagement question; AIA strategy support proposal, August 2026',
            4: 'Source: Agreed geographic priorities and H/M/L scenario framework; AIA proposal, pp. 8-12',
            5: 'Source: Model architecture; AIA proposal, pp. 8-12; proposed analytical approach',
            6: 'Source: Agreed modelling operating-system requirements; inherited workbook and report',
            7: 'Source: Agreed requirements; AIA proposal; current model architecture',
            8: 'Source: Agreed build priorities, geographic scope and formal-use checklist',
            9: 'Source: Proposed integrated workplan: model, client analysis and storyboard',
            10: 'Source: Proposed analyst exercise and current project structure',
            11: 'Source: Confirmed team roles and availability; formal-use checklist',
            12: 'Source: Proposed week-1 baseline and readiness gate',
            14: 'Source: lfm.scripts.compare_history; assumptions vintage 2026; inherited workbook RSA demand; generated 1 October 2026',
            15: 'Source: assumptions/2026 YAML files and 11 time-series CSVs; repository inventory, 1 October 2026',
            16: 'Source: Excel Market share / Deficit Calculations; prior report pp. 33-45; master-assumptions-repo README and infrastructure domains (2 Oct 2026). Integration planned.',
            17: 'Source: Workbook Gasoline - DemandSupply K29, T29, X29; Python cohort diagnostics; lfm.reporting.reconciliation',
            18: 'Source: Workbook Diesel - DemandSupply K30, T30, M30; Python generation, vehicles and held-sector outputs',
            19: 'Source: Workbook fJetFuel F24:H24 and E2:E4; Jet - DemandSupply J23; Python aviation output',
            20: 'Source: Repository inputs; intermediary report PDF pp. 37-38, 42-45; Natural Earth outlines; approximate port locations',
            21: 'Source: assumptions/2026; resolved high_demand / low_demand inputs; existing demand engine, 2030 snapshot',
            22: 'Sources: [1–6] linked operating evidence above; model capacity and 2030 output: supply.yaml; refinery_production.csv; supply.flows. Provisional.',
            23: 'Source: Excel Assumptions M93:R97; Transnet Shippers Manual (2024), pp. 4, 19-20; Astron; Natural Earth; schematic routes',
            38: 'Source: Agreed infrastructure scope and WS5 input specification; aviation/generation modules. Requirements, not verified asset capacity or current capability.',
            37: 'Source: workstreams/README.md; confirmed team roles; WS5 brief and integrated six-week plan. Workstreams describe responsibilities, not separate teams.',
            36: 'Source: src/lfm/model/ and cli.py; assumptions/2026; WS5 specification; agreed engagement scope. Status distinguishes implemented and proposed components.',
            35: 'Source: AIA proposal, pp. 7-8; agreed analytical framework; WS5 brief and six-week plan. Proposed build; current outputs remain provisional.',
            34: 'Sources: [1-3] Royal Vopak corporate and South Africa publications; [4] AIA proposal, August 2026, pp. 7-8. Implications are our analytical framing.',
            31: 'Source: SANRAL national network and corridor publications; Natural Earth; approximate waypoints, not a route-capacity dataset.',
            32: 'Source: Transnet Shippers Manual, September 2024, pp. 9, 19-20; Astron refinery overview. Schematic; branch inventory still to reconcile.',
            29: 'Source: Agreed WS5 scope; workstreams/WS5_infrastructure_logistics/README.md; proposed architecture, not implemented capability.',
            30: 'Source: WS5 brief and integrated six-week workplan; proposed milestones, not completed acceptance gates.',
            28: 'Source: src/lfm/cli.py; run.py; assumptions/yaml_provider.py and snapshot.py; model/demand/; model/supply/flows.py; reporting/',
            27: 'Source: Cell-level workbook inspection; Python code and assumption audit; 2024 reconciliation. Assessment is provisional, not model approval.',
            26: 'Source: Transnet Shippers Manual (2024); Astron; ROMPCO; Sasol GNP audit (2024) and Piped Gas Solutions; Transnet Lilly notice. Schematic.',
            25: 'Source: TNPA; Transnet Freight Rail; Department of Transport; SANRAL national corridors. Schematic routes; see following network pages.',
            24: 'Source: Excel Market share C5:C6, C79:C80; Deficit Calculations AL1:AQ11; Transnet Pipelines public overview, accessed 1 Oct 2026',
        }
        if index not in (53,54,55,56,57):
            text(slide, sources[index], .5, 7.17, 10.1, .2, 8, color=brand.ink)
    slide.notes_slide.notes_text_frame.text = notes

if inventory_only:
    inventory_count = add_inventory(prs, ROOT, brand, cfg, text, table)
assert len(prs.slides) == (inventory_count if inventory_only else 53)
prs.core_properties.title = 'Liquid fuels model: full assumption inventory' if inventory_only else 'Liquid fuels model: analyst kickoff'
prs.core_properties.author = cfg.AUTHOR
prs.core_properties.subject = 'Complete registered inputs and current calculation conventions' if inventory_only else 'Reusable model development and proposed six-week analyst plan'
pdf_only = os.environ.get('LFM_PDF_ONLY') == '1'
out = ROOT / ('qa/pdf-review' if pdf_only else 'output/delivered/supporting')
out.mkdir(parents=True, exist_ok=True)
path = out / ('Vopak_Assumption_Inventory.pptx' if inventory_only else 'Vopak_Analyst_Kickoff.pptx')
prs.save(path)
if not pdf_only and not inventory_only:
    config_path = ROOT / 'deck.yaml'
    config = json.loads(config_path.read_text())
    config['build'].update(command=['@python','scripts/build_kickoff.py'], template_aware=True,
                           output=path.relative_to(ROOT).as_posix())
    config['pdf']['output'] = path.with_suffix('.pdf').relative_to(ROOT).as_posix()
    config_path.write_text(json.dumps(config,indent=2)+'\n')
print(path)
