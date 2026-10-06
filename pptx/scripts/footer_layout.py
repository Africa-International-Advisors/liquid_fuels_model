"""Consistent filled divider markers and a footer band clear of content notes."""
from pptx.util import Inches, Pt
from brand_configs import vopak as cfg

NOTE_PREFIXES=('Sales totals, not density.','Illustrative road cost only.','Routes schematic;','*Ladysmith excludes','Latest staged:','All products; year to June','Typeface: Lato.','S = Situation','History is observed;')

def finish_footer_and_markers(prs,brand):
    for s in prs.slides:
        for q in s.shapes:
            if q.name=='SCR divider marker: circle':
                q.fill.solid();q.fill.fore_color.rgb=brand.accent_primary;q.line.color.rgb=brand.accent_primary
            elif q.name=='SCR divider marker: arrow':q.line.color.rgb=brand.white
            elif q.name=='Strictly Confidential footer':
                q.top=Inches(7.36);q.height=Inches(.13)
                for p in q.text_frame.paragraphs:p.font.size=Pt(7.5)
        sources=[q for q in s.shapes if q.has_text_frame and (q.text.startswith('Source:') or q.name=='Unified source footer')]
        if not sources:continue
        source=sources[0];notes=[]
        for q in list(s.shapes):
            if q.has_text_frame and q!=source and q.top>=Inches(6.7) and q.top<Inches(7.05) and q.text.startswith(NOTE_PREFIXES):
                notes.append(q.text);q._element.getparent().remove(q._element)
        if notes:source.text='Note: '+' '.join(notes)+'\n'+source.text
        source.name='Unified source footer';source.top=Inches(7.10);source.left=Inches(.5);source.width=Inches(10.2);source.height=Inches(.26)
        tf=source.text_frame;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
        for p in tf.paragraphs:
            p.font.name=cfg.THEME_FONT;p.font.size=Pt(7.5);p.space_before=p.space_after=Pt(0);p.line_spacing=Pt(9)
            for r in p.runs:r.font.size=Pt(7.5)
        # Three-row provincial legend: keep the third row above the footer rule.
        legend=['Gauteng','KwaZulu-Natal','Western Cape','Mpumalanga','Eastern Cape','Free State','North West','Limpopo','Northern Cape']
        if any(q.has_text_frame and q.text=='Northern Cape' and q.top>Inches(6) for q in s.shapes):
            for q in s.shapes:
                if q.has_text_frame and q.text in legend and q.top>Inches(6):
                    row=legend.index(q.text)//3;q.top=Inches(6.30+.23*row);q.height=Inches(.20)
                    q.text_frame.margin_top=q.text_frame.margin_bottom=0
                elif q.shape_type==9 and q.height==0 and Inches(6.40)<=q.top<Inches(7.0) and q.width<Inches(.4):
                    old=q.top/Inches(1);row=min(2,max(0,round((old-6.43)/.26)));q.top=Inches(6.37+.23*row)
        links=[q for q in s.shapes if q.has_text_frame and q.text.startswith('[') and q.top>=Inches(6.7)]
        if links:
            source.top=Inches(7.22);source.height=Inches(.13)
            for q in links:
                q.top=Inches(7.08);q.height=Inches(.12)
                q.text_frame.margin_top=q.text_frame.margin_bottom=0
                for p in q.text_frame.paragraphs:
                    p.font.size=Pt(7.5)
                    for r in p.runs:r.font.size=Pt(7.5)
        s.notes_slide.notes_text_frame.text+='\nFooter notes and source occupy the fixed footer band below the rule; legends remain above it. Divider circle is filled blue with a white arrow.'
