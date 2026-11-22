from pathlib import Path
import json
import re
import sys
import importlib.util
import pypdfium2 as pdfium
import pdfplumber
from PIL import Image, ImageDraw
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
parser_spec=importlib.util.spec_from_file_location('guide_flow_parser',ROOT.parent/'core/flow_parser.py')
parser_module=importlib.util.module_from_spec(parser_spec)
parser_spec.loader.exec_module(parser_module)
parse_flow=parser_module.parse_flow
from guide_content import SECTIONS

checked_flows=0
for section in SECTIONS:
    for block in section['blocks']:
        if block[0]=='code' and block[1].startswith(('Login as ', 'click ')):
            example=block[1].replace('<ROLE>','ROLE').replace('<CODE>','201')
            example=re.sub(r'<[^>]+>','sample',example)
            parsed=parse_flow(example,'http://localhost','')
            assert not any(x['action_type']=='UNSUPPORTED' for x in parsed),example
            checked_flows+=1
PDF=ROOT/'output/Playwright_Studio_Complete_Guide.pdf'
QA=ROOT/'qa'
doc=pdfium.PdfDocument(str(PDF))
for index in range(len(doc)):
    page=doc[index]
    image=page.render(scale=1.8).to_pil().convert('RGB')
    image.save(QA/f'page-{index+1:02d}.png')
    page.close()
for start in range(0,len(doc),6):
    sheet=Image.new('RGB',(900,3*650),'#dde2e6')
    for j in range(start,min(start+6,len(doc))):
        im=Image.open(QA/f'page-{j+1:02d}.png')
        im.thumbnail((438,620))
        x=(j-start)%2*450+6;y=(j-start)//2*650+22
        sheet.paste(im,(x,y))
        ImageDraw.Draw(sheet).text((x,y-17),f'PAGE {j+1}',fill='black')
    sheet.save(QA/f'overview-{start//6+1}.jpg',quality=94)
reader=PdfReader(PDF)
texts=[p.extract_text() for p in reader.pages]
for forbidden in ['github.com','qa@example','local-demo-only','C:\\Users','C:/Users','Office QA task']:
    assert forbidden.casefold() not in '\n'.join(texts).casefold(),forbidden
assert '/CreationDate' not in reader.metadata and '/ModDate' not in reader.metadata
assert not reader.metadata.get('/Author')
assert len(reader.outline)==32
assert [reader.get_destination_page_number(item) for item in reader.outline]==list(range(2,34))
assert len(reader.pages[1].get('/Annots',[]))>=32
geometry=[]
with pdfplumber.open(PDF) as pdf:
    for index,page in enumerate(pdf.pages):
        chars=[c for c in page.chars if c.get('text','').strip()]
        out=[c['text'] for c in chars if c['x0']<43 or c['x1']>page.width-43 or c['top']<15 or c['bottom']>page.height-16]
        geometry.append({'page':index+1,'characters':len(chars),'out_of_bounds':out[:20]})
assert not any(x['out_of_bounds'] for x in geometry),geometry
(QA/'verification.json').write_text(json.dumps({'pages':len(doc),'bookmarks':len(reader.outline),'flow_examples_checked':checked_flows,'identifying_text_check':'passed','metadata_check':'passed','page_bounds_check':'passed','navigation_check':'passed','geometry':geometry},indent=2),encoding='utf-8')
print(json.dumps({'pages':len(doc),'bookmarks':len(reader.outline),'flow_examples_checked':checked_flows,'privacy':'passed','bounds':'passed','navigation':'passed'}))
