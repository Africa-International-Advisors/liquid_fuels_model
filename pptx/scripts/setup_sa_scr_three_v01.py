from pathlib import Path
r=Path(__file__).resolve().parents[2];p=r/'pptx/scripts'
for source,target in [('trim_sa_story_v37.py','trim_sa_scr_three_v01.py'),('apply_sa_story_navigation_v37.py','apply_sa_scr_three_navigation_v01.py'),('finalize_sa_story_v36.mjs','finalize_sa_scr_three_v01.mjs')]:
 t=(p/source).read_text(encoding='utf8')
 t=t.replace('story_v37','scr_three_v01').replace('story_v36','scr_three_v01')
 t=t.replace('SA_Market_Story_2026-10-11_v37','SA_SCR_Three_Page_2026-10-11_v01').replace('SA_Market_Story_2026-10-11_v36','SA_SCR_Three_Page_2026-10-11_v01')
 if source.startswith('trim'):t=t.replace('[24:]','[3:]')
 if source.startswith('apply'):
  t=t.replace("clean=QA/'styled_body.pptx'","clean=QA/'body.pptx'").replace('len(native)==23','len(native)==3').replace('Exported 24 slides; 23','Exported 3 slides; 3')
 if source.startswith('finalize'):t=t.replace("candidatePath:qa+'/with_chart_workbooks.pptx'","candidatePath:qa+'/SA_SCR_Three_Page_2026-10-11_v01.pptx'")
 (p/target).write_text(t,encoding='utf8')
