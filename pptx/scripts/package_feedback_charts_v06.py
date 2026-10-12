"""Package native chart literals with Excel-compatible precision and workbooks."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as ET
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
qa = root / 'pptx/qa/evidence_v06'
source = qa / 'refreshed_candidate.pptx'
staged = qa / 'excel_precision.pptx'
ns = {'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'}
with ZipFile(source) as zin, ZipFile(staged, 'w', ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if '/charts/' in item.filename and item.filename.endswith('.xml'):
            tree = ET.fromstring(data)
            for value in tree.xpath('//c:numLit/c:pt/c:v | //c:numCache/c:pt/c:v', namespaces=ns):
                value.text = format(float(value.text), '.15g')
            data = ET.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
        zout.writestr(item, data)
helper = Path('C:/Users/ITafr/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations/container_tools/materialize_literal_chart_workbooks.py')
subprocess.run([sys.executable, str(helper), str(staged), str(qa / 'with_chart_workbooks.pptx'), '--workspace', str(root), '--receipt', str(qa / 'chart_workbooks_receipt.json')], check=True)
