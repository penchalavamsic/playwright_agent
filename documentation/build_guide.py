"""Build a paginated application manual with vector figures and linked contents."""
from pathlib import Path
import json
import math
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
    Spacer, PageBreak, Table, TableStyle, KeepTogether, Flowable, Preformatted)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.graphics.shapes import Drawing, Rect, Line, Polygon, String
from reportlab.graphics import renderSVG
from pypdf import PdfReader, PdfWriter
from guide_content import SECTIONS

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output'
QA = ROOT / 'qa'
OUT.mkdir(exist_ok=True)
QA.mkdir(exist_ok=True)
FONT = Path('C:/Windows/Fonts')
for name, filename in [('Body','segoeui.ttf'),('Bold','segoeuib.ttf'),('Italic','segoeuii.ttf'),('Code','consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT / filename)))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Bold', italic='Italic', boldItalic='Bold')
BLACK=colors.HexColor('#000000')
INK=colors.HexColor('#253345')
MUTED=colors.HexColor('#526071')
TEAL=colors.HexColor('#087F8C')
PALE=colors.HexColor('#F0F6F7')
BORDER=colors.HexColor('#D9D9D9')
WIDTH, HEIGHT = A4
CONTENT = WIDTH-96

STYLES = {
    'body': ParagraphStyle('BodyText', fontName='Body', fontSize=10.1, leading=14.5, textColor=INK, spaceAfter=8),
    'h1': ParagraphStyle('Heading1', fontName='Bold', fontSize=21, leading=26, textColor=BLACK, spaceAfter=8, keepWithNext=True),
    'h2': ParagraphStyle('Heading2', fontName='Bold', fontSize=11.5, leading=15, textColor=BLACK, spaceBefore=9, spaceAfter=5, keepWithNext=True),
    'audience': ParagraphStyle('Audience', fontName='Body', fontSize=9, leading=12, textColor=MUTED, spaceAfter=16, keepWithNext=True),
    'step': ParagraphStyle('Step', fontName='Body', fontSize=10, leading=14, textColor=INK, leftIndent=21, firstLineIndent=-21, spaceAfter=7),
    'bullet': ParagraphStyle('Bullet', fontName='Body', fontSize=10, leading=14, textColor=INK, leftIndent=14, firstLineIndent=-14, spaceAfter=7),
    'cell': ParagraphStyle('Cell', fontName='Body', fontSize=9.2, leading=12.6, textColor=INK, spaceAfter=0),
    'headcell': ParagraphStyle('HeadCell', fontName='Bold', fontSize=9.2, leading=12.6, textColor=colors.white, spaceAfter=0),
    'caption': ParagraphStyle('Caption', fontName='Italic', fontSize=8.6, leading=11.5, textColor=MUTED, spaceBefore=5, spaceAfter=12),
    'code': ParagraphStyle('Code', fontName='Code', fontSize=8.6, leading=11.5, textColor=INK, leftIndent=8, spaceBefore=4, spaceAfter=10),
    'title': ParagraphStyle('Title', fontName='Bold', fontSize=35, leading=42, textColor=BLACK, spaceAfter=15),
    'subtitle': ParagraphStyle('Subtitle', fontName='Body', fontSize=19, leading=25, textColor=BLACK, spaceAfter=20),
}

def para(s, style='body'):
    return Paragraph(escape(s).replace('\n','<br/>'), STYLES[style])

def wrap_label(text, width, size=9.5, face='Body'):
    lines=[]
    for part in text.split('\n'):
        line=''
        for word in part.split():
            candidate=(line+' '+word).strip()
            if pdfmetrics.stringWidth(candidate,face,size)>width and line:
                lines.append(line); line=word
            else: line=candidate
        lines.append(line)
    return lines

def node(d,x,y,w,h,title,body='',fill=PALE,stroke=TEAL):
    d.add(Rect(x,y,w,h,rx=6,ry=6,fillColor=fill,strokeColor=stroke,strokeWidth=.8))
    title_lines=wrap_label(title,w-16,9.5,'Bold')
    body_lines=wrap_label(body,w-16,8.5) if body else []
    line_h=11.5
    total=len(title_lines)*line_h+(4+len(body_lines)*10.3 if body_lines else 0)
    yy=y+(h+total)/2-10
    for line in title_lines:
        d.add(String(x+w/2,yy,line,fontName='Bold',fontSize=9.5,textAnchor='middle',fillColor=INK)); yy-=line_h
    yy-=4
    for line in body_lines:
        d.add(String(x+w/2,yy,line,fontName='Body',fontSize=8.5,textAnchor='middle',fillColor=MUTED)); yy-=10.3

def arrow(d,x1,y1,x2,y2,color=TEAL,label=''):
    d.add(Line(x1,y1,x2,y2,strokeColor=color,strokeWidth=1.2))
    angle=math.atan2(y2-y1,x2-x1)
    points=[x2,y2,x2-6*math.cos(angle-.45),y2-6*math.sin(angle-.45),x2-6*math.cos(angle+.45),y2-6*math.sin(angle+.45)]
    d.add(Polygon(points,fillColor=color,strokeColor=color))
    if label:
        d.add(String((x1+x2)/2,(y1+y2)/2+5,label,fontName='Body',fontSize=8,fillColor=MUTED,textAnchor='middle'))

def diagram(kind):
    w=CONTENT
    if kind=='journey':
        d=Drawing(w,94)
        labels=[('Set up','URL and profile'),('Describe','Ordered flow'),('Run','Real browser'),('Review','Report evidence'),('Reuse','Exported suite')]
        nw=(w-48)/5
        for i,(title,body) in enumerate(labels):
            x=i*(nw+12); node(d,x,16,nw,66,title,body)
            if i<4: arrow(d,x+nw,49,x+nw+11,49)
    elif kind=='interface':
        d=Drawing(w,250)
        node(d,0,0,170,244,'SETUP','',fill=colors.white,stroke=BORDER)
        node(d,181,0,w-181,244,'','',fill=colors.white,stroke=BORDER)
        for y,title,body in [(204,'Open project   |   Try demo',''),(159,'Application URL','<TARGET_URL>'),(111,'Login profile   |   Edit','<ROLE>'),(51,'Test flow','<ORDERED_ACTIONS>'),(9,'Advanced settings   |   Run test','')]:
            node(d,8,y,154,32 if not body else 44,title,body,stroke=BORDER)
        node(d,190,196,w-199,39,'Test results','Open full report',stroke=BORDER)
        node(d,190,151,w-199,35,'Results  |  Details  |  Test plan  |  Files','',stroke=BORDER)
        node(d,190,13,w-199,127,'Selected result or generated content','Step outcomes, messages, plan text, or source files',fill=colors.white,stroke=BORDER)
    elif kind=='manual':
        d=Drawing(w,150)
        items=[('Saved profile','Same project and role'),('Manual sign in','Complete the challenge'),('Capture','Inspection only'),('Close browser','Release the profile'),('Automated run','Validate the real flow')]
        nw=(w-36)/3
        coords=[(0,85),(nw+18,85),(2*(nw+18),85),(2*(nw+18),8),(nw+18,8)]
        for (title,body),(x,y) in zip(items,coords):node(d,x,y,nw,57,title,body)
        arrow(d,nw,113,nw+17,113);arrow(d,2*nw+18,113,2*nw+35,113)
        arrow(d,w-nw/2,85,w-nw/2,65);arrow(d,2*(nw+18),36,2*nw+19,36)
    elif kind=='failure':
        d=Drawing(w,103)
        nw=(w-54)/4
        for i,(title,body,col) in enumerate([('Step 1','Passed','#EAF5F1'),('Step 2','Failed','#FCEDEC'),('Step 3','Skipped','#F2F3F5'),('Step 4','Skipped','#F2F3F5')]):
            x=i*(nw+18);node(d,x,32,nw,60,title,body,fill=colors.HexColor(col),stroke=BORDER)
            if i<3:arrow(d,x+nw,62,x+nw+17,62)
        d.add(String(w/2,10,'Later actions are not attempted after the first failure.',fontName='Body',fontSize=9,fillColor=MUTED,textAnchor='middle'))
    elif kind=='authchoice':
        d=Drawing(w,180)
        node(d,150,127,199,44,'Start with a short login flow')
        node(d,0,53,151,55,'Incognito works','Choose Fresh')
        node(d,174,53,151,55,'Remembered sign in','Choose Saved + marker')
        node(d,348,53,151,55,'Interactive challenge','Manual saved session')
        for x in [75,249,423]:arrow(d,249,127,x,110)
        for x in [75,249,423]:arrow(d,x,53,x,28)
        node(d,0,0,w,28,'Still failing  |  Inspect routes, responses, markers, and the target session',stroke=BORDER)
    elif kind=='architecture':
        d=Drawing(w,245)
        node(d,0,192,138,44,'Desktop interface')
        node(d,0,130,138,44,'Command line')
        node(d,175,157,152,66,'Pipeline','Parse, inspect, plan, generate')
        arrow(d,138,214,174,196);arrow(d,138,152,174,177)
        node(d,367,157,132,66,'Browser engine','Playwright and session guard')
        arrow(d,327,190,366,190)
        node(d,367,73,132,55,'Target application','Local or deployed')
        arrow(d,433,157,433,129)
        node(d,175,73,152,55,'Workspace','Settings, reports, evidence')
        arrow(d,251,157,251,129);arrow(d,367,157,327,128)
        node(d,0,7,138,55,'Exported projects','Four language options')
        node(d,175,7,152,55,'Framework execution','A separate later test run')
        node(d,367,7,132,55,'Execution reports','New evidence per run')
        arrow(d,175,89,138,48);arrow(d,138,35,174,35);arrow(d,327,35,366,35)
        arrow(d,327,62,367,73)
    elif kind=='pipeline':
        d=Drawing(w,100)
        stages=[('1  Parse intent','Ordered steps'),('2  Inspect browser','Execution evidence'),('3  Plan tests','Scenarios and plan'),('4  Synthesize','Language stages'),('5  Scaffold','Files and reports')]
        nw=(w-48)/5
        for i,(title,body) in enumerate(stages):
            x=i*(nw+12)
            node(d,x,12,nw,77,title,body)
            if i<4:arrow(d,x+nw,50,x+nw+11,50)
    elif kind=='locator':
        d=Drawing(w,112)
        items=[('Read live page','Compatible controls'),('Match target','Label or identifier'),('Require one','Unique best match'),('Act and record','Outcome + locator')]
        nw=(w-42)/4
        for i,(title,body) in enumerate(items):
            x=i*(nw+14);node(d,x,31,nw,68,title,body)
            if i<3:arrow(d,x+nw,65,x+nw+13,65)
        d.add(String(w/2,9,'Missing or ambiguous target  >  fail the step  >  skip dependent steps',fontName='Body',fontSize=9,fillColor=MUTED,textAnchor='middle'))
    elif kind=='evidence':
        d=Drawing(w,160)
        node(d,0,100,141,52,'Browser execution','Actions and assertions')
        node(d,179,100,141,52,'Inspection report','Measured steps and paths')
        node(d,358,100,141,52,'Report case','Observed status')
        arrow(d,141,126,178,126);arrow(d,320,126,357,126)
        node(d,0,10,141,56,'Captured files','Screenshots, video, trace')
        node(d,179,10,141,56,'Evidence directory','Existing files copied')
        node(d,358,10,141,56,'HTML and JSON','Relative evidence links')
        arrow(d,70,100,70,67);arrow(d,141,38,178,38);arrow(d,320,38,357,38);arrow(d,428,100,428,67)
    else: raise ValueError(kind)
    return d

class GuideDoc(BaseDocTemplate):
    def __init__(self,path):
        super().__init__(str(path),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=48,bottomMargin=45,
                         title='Playwright Studio Complete Application Guide',author='',subject='User procedures and technical architecture',pageCompression=1)
        self.addPageTemplates([PageTemplate(id='main',frames=Frame(48,45,CONTENT,HEIGHT-93,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0),onPage=self.decorate)])
        self.chapter_pages={}
    def decorate(self,c,doc):
        c.saveState()
        if doc.page>1:
            c.setFont('Body',8);c.setFillColor(BLACK)
            c.drawString(48,HEIGHT-28,'PLAYWRIGHT STUDIO  |  APPLICATION GUIDE')
            c.setFont('Body',8);c.setFillColor(MUTED)
            c.drawString(48,25,'User procedures and technical reference')
            c.drawRightString(WIDTH-48,25,str(doc.page))
        c.restoreState()
    def afterFlowable(self,f):
        if hasattr(f,'chapter_id'):
            key=f'chapter-{f.chapter_id}'
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(f.getPlainText(),key,0,False)
            self.notify('TOCEntry',(0,f.getPlainText(),self.page,key))
            self.chapter_pages[f.chapter_id]=self.page

def make_table(headers,rows,widths):
    widths=widths or [1/len(headers)]*len(headers)
    matrix=[[para(x,'headcell') for x in headers]]+[[para(x,'cell') for x in row] for row in rows]
    t=Table(matrix,colWidths=[CONTENT*x for x in widths],repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#203C50')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F3F6F8')]),
        ('GRID',(0,0),(-1,-1),.5,BORDER),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
    ]))
    t.spaceBefore=3;t.spaceAfter=10
    return t

def build():
    story=[]
    story += [Spacer(1,65),para('Playwright Studio','title'),para('Complete application guide','subtitle'),
              Spacer(1,13),para('User procedures and technical architecture','h2'),
              para('A practical reference for operating the desktop application, writing reliable browser flows, interpreting reports, and maintaining generated automation.'),
              Spacer(1,34),diagram('journey'),Spacer(1,25),
              para('For everyday users','h2'),para('Follow the quick start, interface guide, flow examples, and report walkthroughs. No programming knowledge is required for the desktop procedures.'),
              para('For technical readers','h2'),para('Use the architecture, execution contracts, authentication behavior, command reference, source map, and validation guidance.'),
              Spacer(1,18),para('Examples use replaceable placeholders for application addresses, roles, account values, and test data. Diagrams show the implemented workflow and component responsibilities.','caption'),PageBreak()]
    story.append(para('Contents','h1'))
    story.append(para('Select a section to navigate. Use the PDF bookmarks for quick access.'))
    toc=TableOfContents()
    toc.levelStyles=[ParagraphStyle('TOC',fontName='Body',fontSize=9.8,leading=14,leftIndent=0,firstLineIndent=0,rightIndent=24,spaceBefore=0,textColor=INK)]
    toc.dotsMinLevel=0
    story += [toc,PageBreak()]
    for index,section in enumerate(SECTIONS,1):
        title=para(f'{index:02d}  {section["title"]}','h1');title.chapter_id=index
        story += [title,para(section['audience'],'audience')]
        for block in section['blocks']:
            kind=block[0]
            if kind=='p':story.append(para(block[1]))
            elif kind=='h':story.append(para(block[1],'h2'))
            elif kind in ('steps','bullets'):
                for n,item in enumerate(block[1],1):
                    story.append(para((f'{n}.  ' if kind=='steps' else '\u2022  ')+item,'step' if kind=='steps' else 'bullet'))
            elif kind=='code':
                lines=block[1].splitlines()
                longest=max(pdfmetrics.stringWidth(x,'Code',8.6) for x in lines)
                if longest>CONTENT-8:raise ValueError(('Code too wide',index,longest,block[1]))
                story.append(Preformatted(block[1],STYLES['code']))
            elif kind=='table':story.append(make_table(block[1],block[2],block[3]))
            elif kind=='figure':
                d=diagram(block[1]);story.append(KeepTogether([d,para(block[2],'caption')]))
                renderSVG.drawToFile(d,str(QA/(block[1]+'.svg')))
        if index<len(SECTIONS):story.append(PageBreak())
    staging=QA/'guide-layout.pdf'
    doc=GuideDoc(staging)
    doc.multiBuild(story)
    output=OUT/'Playwright_Studio_Complete_Guide.pdf'
    reader=PdfReader(staging)
    writer=PdfWriter(clone_from=reader)
    writer.metadata=None
    writer.add_metadata({'/Title':'Playwright Studio Complete Application Guide','/Subject':'User procedures and technical architecture','/Author':''})
    with output.open('wb') as handle:writer.write(handle)
    text='\n'.join(page.extract_text() for page in reader.pages)
    (QA/'extracted-text.txt').write_text(text,encoding='utf-8')
    validation={'pages':len(reader.pages),'sections':len(SECTIONS),'figures':9,'words':len(text.split()),'chapter_pages':doc.chapter_pages,'file':output.name}
    (QA/'layout-summary.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
    print(json.dumps(validation,indent=2))

if __name__=='__main__':build()
