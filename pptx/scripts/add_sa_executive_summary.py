"""Split the reviewed opening into baseline/changes and investment outlook."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
source = root / 'pptx/story/sa_market_story_feedback_2026_10_07.json'
story = json.loads(source.read_text(encoding='utf-8'))
outlook = story['slides'][0]
outlook['section'] = 1
outlook['title'] = 'Vopak can capture inland growth through the Durban–Lesedi corridor, with expansion conditional on turnover and returns'
outlook['headers'] = ['Investment outlook', 'Why it matters', 'What determines the choice']
outlook['rows'][3][1] = 'Demand and domestic supply each\nhave L/M/H paths. Medium/Medium\nis the reference to calibrate.'
baseline = {
    'title': 'Slow demand growth and greater import reliance set the baseline; power, refineries and routes could change it',
    'section': 1,
    'headers': ['Baseline / reference', 'What the evidence establishes', 'What changes the outlook'],
    'column_widths': [165, 329, 344.8],
    'font_size': 13,
    'icons': ['ship', 'route', 'turns', 'matrix'],
    'rows': [
        ['Fuel demand\nand power',
         '2013–2023 CAGR: petrol −2.08%;\ndiesel +0.82%. Eskom OCGT fuel use\nfell 40% in FY2025.',
         'Growth, rail, EVs and efficiency alter\ntransport demand; fleet recovery and\nnew generation alter diesel dispatch.'],
        ['Domestic supply\nand imports',
         '2020–2025 imports rose by 5.43bn\nlitres of diesel and 2.73bn of petrol.\nThe sourcing mix has shifted.',
         'SAPREF and PetroSA restart paths,\nSecunda gas/MRG and Natref output\ncan change domestic supply.'],
        ['Corridor position\nand tank turnover',
         'Durban and Lesedi provide coastal\nand inland assets serving Gauteng.\nWorking capacity and turns are open.',
         'Route costs, access and customer\ncapture determine flow; achievable\nturnover determines handling headroom.'],
        ['Medium / Medium\nreference world',
         'M/M anchors the nine-world matrix.\nHistorical evidence is assembled;\nnumerical calibration remains open.',
         'Vary demand and supply around M/M,\nthen test capture, turnover and returns\nto identify investment triggers.']
    ],
    'note': 'Executive summary — baseline and changes. Comparable historical periods differ: Department sales 2013–2023; SARS imports 2020–2025; Eskom FY2025 vs FY2024 (own diesel + kerosene). M/M is a reference framework, not a calibrated forecast.'
}
story['slides'].insert(0, baseline)
for slide in story['slides']:
    slide['note'] = slide.get('note', '').replace('appendix pp18, 21–22', 'appendix pp19, 22–23').replace('appendix p24', 'appendix p25')
story.update({
    'main_story_pages': '2–15', 'executive_summary_pages': '2–3',
    'situation_pages': '6–10', 'complication_pages': '11–14',
    'appendix_pages': '16–29', 'share_inference_page': 29,
    'opening_pages': '2: baseline and changes; 3: investment outlook; 4: SCR synthesis; 5: nine-world matrix',
    'cover_status': 'Executive summary: baseline, changes and investment outlook; calibration gaps explicit'
})
(root / 'pptx/story/sa_market_story_executive_2026_10_07.json').write_text(json.dumps(story, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
