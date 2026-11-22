"""Render an 88-second, labeled product walkthrough from actual Studio captures."""
from pathlib import Path
import json
import math
import os
import subprocess
import sys
import wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS, WORK = ROOT/'assets', ROOT/'work'
WORK.mkdir(exist_ok=True)
FFMPEG = Path(os.environ.get('FFMPEG') or ROOT.parent/'tmp/media_runtime/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
REVISED = '--revised' in sys.argv
SUFFIX = '_Revised' if REVISED else ''
SCENES = json.loads((ROOT/('storyboard_revised.json' if REVISED else 'storyboard.json')).read_text(encoding='utf-8'))
EVIDENCE = json.loads((ASSETS/'evidence.json').read_text())
W,H,FPS = 1920,1080,30
TOTAL = sum(scene['seconds'] for scene in SCENES)
TEAL,WHITE,MUTED = '#5EEAD4','#F1F5F9','#A6B6CE'
PANEL,BORDER = '#101D33','#283D5A'
FONT = Path('C:/Windows/Fonts')

def font(size, bold=False, mono=False):
    return ImageFont.truetype(str(FONT/('consola.ttf' if mono else 'segoeuib.ttf' if bold else 'segoeui.ttf')),size)

def text(im, xy, value, size=28, fill=WHITE, bold=False, mono=False):
    ImageDraw.Draw(im).text(xy, value, font=font(size,bold,mono), fill=fill, spacing=12)

def wrapped(value, width, size=28, bold=False):
    f=font(size,bold)
    lines=[]
    for paragraph in value.split('\n'):
        line=''
        for word in paragraph.split():
            trial=(line+' '+word).strip()
            if f.getlength(trial)>width and line:
                lines.append(line); line=word
            else: line=trial
        lines.append(line)
    return '\n'.join(lines)

def box(im, rect, fill=PANEL, outline=BORDER, radius=22):
    ImageDraw.Draw(im).rounded_rectangle(rect,radius=radius,fill=fill,outline=outline,width=2)

def pill(im,xy,label,color=TEAL):
    x,y=xy; width=int(font(20,True).getlength(label))+32
    box(im,(x,y,x+width,y+39),fill='#102F36',outline='#225653',radius=18)
    text(im,(x+16,y+5),label,20,color,True)

IMAGES={}
def get_image(name,crop=None):
    key=(str(name),crop)
    if key not in IMAGES:
        image=Image.open(name if Path(name).is_absolute() else ASSETS/name).convert('RGB')
        if crop: image=image.crop(crop)
        IMAGES[key]=image
    return IMAGES[key]

def screen(im,name,rect,crop=None,fill='#0B1425',label=None):
    x,y,x2,y2=rect
    box(im,(x-2,y-2,x2+2,y2+2),fill,outline=BORDER,radius=17)
    source=get_image(name,crop)
    scale=min((x2-x-20)/source.width,(y2-y-20)/source.height)
    size=(int(source.width*scale),int(source.height*scale))
    source=source.resize(size,Image.Resampling.LANCZOS)
    im.paste(source,(x+(x2-x-size[0])//2,y+(y2-y-size[1])//2))
    if label: pill(im,(x+16,y+16),label)

def notes(im,items,x=78,y=270,width=380):
    for i,(heading,body) in enumerate(items):
        cy=y+i*168
        text(im,(x,cy),heading,30,TEAL,True)
        text(im,(x,cy+47),wrapped(body,width,25),25,MUTED)

yy,xx=np.mgrid[0:H,0:W]
glow=np.maximum(0,1-np.sqrt(((xx-1600)/1500)**2+((yy-100)/1000)**2))
BASE=Image.fromarray(np.stack([8+glow*7,15+glow*15,29+glow*23],axis=-1).astype('uint8'))

def background(scene):
    im=BASE.copy(); d=ImageDraw.Draw(im)
    d.rounded_rectangle((72,42,99,69),radius=8,outline=TEAL,width=3)
    text(im,(113,40),'PLAYWRIGHT STUDIO',24,WHITE,True)
    text(im,(1530,45),'PRODUCT WALKTHROUGH',18,MUTED)
    text(im,(72,104),scene['title'],56,WHITE,True)
    text(im,(75,184),scene['chapter'],20,TEAL,True)
    d.line((72,221,1848,221),fill=BORDER,width=2)
    return im

def standard_scene(scene,phase=0):
    im=background(scene); sid=scene['id']
    if sid=='intro':
        text(im,(76,300),'Test flows.\nReal proof.',84,WHITE,True)
        text(im,(80,535),'A focused desktop workflow\nfor repeatable browser QA.',30,MUTED)
        pill(im,(80,674),'REAL EXECUTION'); pill(im,(80,732),'REUSABLE AUTOMATION')
        text(im,(80,789),'Extract the ZIP; keep the _internal folder.',21,MUTED)
        text(im,(80,822),'Requires Windows and Edge or Chrome.',21,MUTED)
        screen(im,'01-studio.png',(700,268,1844,846),crop=(12,28,1518,802))
    elif sid=='setup':
        notes(im,[('Start with a URL','Use your localhost or deployed web application.'),('Already have a project?','Open it to continue numbered runs.'),('Try it safely','The built-in demo supplies a local app and example flow.')])
        screen(im,'02-demo-setup.png',(550,250,1110,854),crop=(18,110,342,675))
        box(im,(1180,286,1835,756))
        text(im,(1215,323),'THREE WAYS TO START',24,TEAL,True)
        for j,label in enumerate(['Application URL','Open project','Try demo']):
            pill(im,(1220,398+j*99),str(j+1).zfill(2))
            text(im,(1300,399+j*99),label,35,WHITE,True)
    elif sid=='profile':
        notes(im,[('Choose the role','Select the access profile for this test.'),('Save the account','Use Edit to add a username and password.'),('Public application?','Choose the public URL option when no login is needed.')])
        screen(im,'03-profile.png',(610,245,1185,857),crop=(25,279,324,596))
        box(im,(1260,335,1837,702))
        text(im,(1290,371),'PROFILE SETUP',24,TEAL,True)
        text(im,(1290,425),'Role\nUsername / email\nPassword\nSave profile',31,WHITE)
    elif sid=='flow':
        screen(im,'06-ready.png',(76,265,575,789),crop=(30,349,321,548))
        text(im,(95,807),'A clear, ordered flow',25,TEAL,True)
        box(im,(632,250,1840,855))
        text(im,(668,274),'EXAMPLE USED IN THIS DEMO',23,TEAL,True)
        lines=['Login as QA;', 'click "Tasks"; click "New task";', 'fill "Title" with "Office QA task";', 'select "High" from "Priority";', 'check "Notify team"; click "Create task";', 'verify API "/api/tasks" status code 201;', 'verify "Task created"']
        for i,line in enumerate(lines):
            text(im,(680,340+i*65),f'{i+1:02d}',23,MUTED,mono=True)
            text(im,(735,335+i*65),line,30,WHITE,mono=True)
        text(im,(680,811),'Also supported: search, press a key, navigate',21,MUTED)
    elif sid=='session':
        screen(im,'04-session-options.png',(1210,250,1835,854),crop=(29,179,322,535))
        box(im,(76,270,1120,449))
        text(im,(110,300),'Fresh (incognito-like)',35,TEAL,True)
        text(im,(110,359),'A clean context for each run; cookies stay shared within the flow.',25,MUTED)
        box(im,(76,475,1120,654))
        text(im,(110,504),'Saved profile (normal)',35,TEAL,True)
        text(im,(110,562),'A dedicated session for this project, application and role.',25,MUTED)
        text(im,(110,704),'Success marker: /dashboard or a logged-in CSS selector',26,WHITE)
        text(im,(110,759),'Manual session: sign in yourself, then capture for inspection.',25,MUTED)
    elif sid=='exports':
        screen(im,'05-output-options.png',(75,255,690,856),crop=(30,354,325,659))
        for i,(short,title) in enumerate([('PY','Python / pytest'),('JAVA','Java / TestNG'),('TS','TypeScript'),('JS','JavaScript')]):
            x=765+(i%2)*555; y=285+(i//2)*195
            box(im,(x,y,x+515,y+165)); pill(im,(x+26,y+23),short)
            text(im,(x+28,y+84),title,32,WHITE,True)
        text(im,(795,735),'Include a test plan. Choose your output folder.',29,TEAL,True)
        text(im,(795,790),'Install each exported framework’s dependencies before rerunning.',23,MUTED)
    elif sid=='run':
        notes(im,[('Run test','The browser executes the exact requested sequence.'),('Create + verify','Input values, create the task, and check the API result.'),('Actual footage','The panel shows this demo’s real browser recording.')],width=430)
        screen(im,'07-running.png',(75,790,550,853),crop=(381,102,1498,152))
        box(im,(602,248,1842,863),fill='#EDF2F8')
    elif sid=='results':
        notes(im,[('Per-step outcomes','Read the result of every action and assertion.'),('Clear failure behavior','Dependent steps are skipped when an earlier step fails.'),('Open full report','Move from the summary to the supporting evidence.')])
        screen(im,'08-results.png',(535,250,1840,855),crop=(374,44,1500,661))
    elif sid=='report':
        if phase==0:
            screen(im,'11-report-overview.png',(75,265,1841,822),crop=(0,0,1440,455))
            pill(im,(100,829),'1 EXECUTED PASS'); pill(im,(385,829),'2 ADVISORY PLANS: NOT RUN')
        else:
            notes(im,[('Filter results','Show passed, failed, or unexecuted cases.'),('Expand a case','Inspect its ordered steps and actual outcomes.'),('Plan ≠ execution','An advisory plan is not a passed test.')])
            screen(im,'12-report-steps.png',(540,260,1839,852),crop=(0,0,770,287))
    elif sid=='evidence':
        screen(im,EVIDENCE['screenshot'],(75,254,930,631),crop=(180,120,1080,655))
        pill(im,(100,269),'STEP SCREENSHOTS')
        screen(im,str(sorted((WORK/'browser-frames').glob('frame-*.jpg'))[-10]),(970,254,1840,631))
        pill(im,(995,269),'RECORDED VIDEO')
        screen(im,'13-api-summary.png',(75,670,1290,858),crop=(0,180,1372,294))
        pill(im,(100,642),'CAPTURED API RESPONSES')
        box(im,(1330,670,1840,858))
        text(im,(1363,697),'PLAYWRIGHT TRACE',22,TEAL,True)
        text(im,(1363,740),'trace.zip',39,WHITE,True)
        text(im,(1363,802),'Download from the report',23,MUTED)
    elif sid=='code':
        if phase==0:
            screen(im,'09-plan.png',(70,256,1840,848),crop=(390,218,1484,750))
            pill(im,(108,276),'TEST PLAN')
        else:
            screen(im,'10-code.png',(70,256,1370,848),crop=(390,205,1480,752))
            box(im,(1420,279,1840,816))
            text(im,(1450,313),'CONTINUE & REUSE',21,TEAL,True)
            text(im,(1450,378),'Open project\nAppend numbered runs',26,WHITE)
            text(im,(1450,497),'EXPORTED SUITES',20,TEAL,True)
            text(im,(1450,547),'python -m pytest\n\nnpm test\n\nmvn test',27,WHITE,mono=True)
    elif sid=='loop':
        box(im,(75,260,1840,360),fill='#2B1B2A',outline='#73394D')
        text(im,(110,285),'LOGIN   →   DASHBOARD   →   LOGIN',37,'#FDA4AF',True)
        screen(im,'15-auth-diagnostics.png',(75,398,1290,856),crop=(0,0,1040,346))
        box(im,(1340,398,1840,856))
        text(im,(1374,438),'STOP + DIAGNOSE',27,'#FDA4AF',True)
        text(im,(1374,503),'401 response\nRedirect path\nNo automatic retry\nDependent steps skipped',27,WHITE)
        text(im,(1374,747),'Reproduced on a local\nauthentication fixture.',23,MUTED)
    elif sid=='close':
        for i,(number,label) in enumerate([('01','SET UP'),('02','RUN'),('03','REVIEW'),('04','REUSE')]):
            x=75+i*450
            box(im,(x,336,x+420,643)); text(im,(x+32,367),number,65,TEAL,True)
            text(im,(x+32,502),label,40,WHITE,True)
        text(im,(80,715),'Ready for your next test.',42,WHITE,True)
        text(im,(80,788),'Clear flows. Verified outcomes. Reusable automation.',28,MUTED)
    return im

def subtitle(im,scene):
    # All caption text is date-free; the timeline uses only an unlabeled progress strip.
    text(im,(77,879),scene['caption'],23,TEAL)
    box(im,(70,925,1850,1039),fill='#080F1D',outline='#1D2E45',radius=18)
    line=wrapped(scene['voice'],1685,29)
    assert len(line.splitlines())<=2, scene['id']
    text(im,(105,946 if '\n' in line else 966),line,29,WHITE)

def srt_time(seconds):
    ms=round(seconds*1000)
    return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'

def prepare_audio():
    tracks=[]; elapsed=0; captions=[]
    for idx,s in enumerate(SCENES,1):
        raw=(ASSETS/'male-narration' if REVISED else ASSETS)/(s['id']+'.wav')
        with wave.open(str(raw)) as wav: duration=wav.getnframes()/wav.getframerate()
        speed=max(1,duration/(s['seconds']-.40))
        assert speed<(1.12 if REVISED else 1.24),(s['id'],speed)
        target=WORK/(s['id']+'-timed.wav')
        tone='highpass=f=65,equalizer=f=160:t=q:w=0.8:g=1.5,loudnorm=I=-18:TP=-2:LRA=7,' if REVISED else ''
        subprocess.run([str(FFMPEG),'-y','-v','error','-i',str(raw),'-af',f'{tone}atempo={speed:.6f},adelay=200|200,apad',
            '-t',str(s['seconds']),'-ar','48000','-ac','2',str(target)],check=True)
        with wave.open(str(target)) as wav: tracks.append(wav.readframes(wav.getnframes()))
        captions.append(f'{idx}\n{srt_time(elapsed+.2)} --> {srt_time(elapsed+s["seconds"]-.15)}\n{wrapped(s["voice"],1685,29)}\n')
        elapsed+=s['seconds']
    with wave.open(str(WORK/'narration.wav'),'wb') as wav:
        wav.setnchannels(2); wav.setsampwidth(2); wav.setframerate(48000); wav.writeframes(b''.join(tracks))
    (ROOT/f'Playwright_Studio_Demo{SUFFIX}.srt').write_text('\n'.join(captions),encoding='utf-8')

def video_frames():
    folder=WORK/'browser-frames'; folder.mkdir(exist_ok=True)
    subprocess.run([str(FFMPEG),'-y','-v','error','-i',EVIDENCE['video'],'-vf','fps=30,scale=1088:612',
        '-q:v','2',str(folder/'frame-%04d.jpg')],check=True)
    return sorted(folder.glob('frame-*.jpg'))

def main():
    prepare_audio(); footage=video_frames()
    mode='preview' if 'preview' in sys.argv else 'render'
    poster=[]; elapsed=0; bases={}
    for s in SCENES:
        for phase in range(2 if s['id'] in ('report','code') else 1):
            bases[s['id'],phase]=standard_scene(s,phase)
        preview=bases[s['id'],0].copy(); subtitle(preview,s)
        if s['id']=='run': preview.paste(Image.open(footage[min(180,len(footage)-1)]),(675,250))
        preview.save(WORK/(s['id']+'-preview.jpg'),quality=94)
        poster.append(preview.resize((480,270)))
    contact=Image.new('RGB',(1920,270*4),'#080F1D')
    for i,p in enumerate(poster): contact.paste(p,((i%4)*480,(i//4)*270))
    contact.save(ROOT/f'Demo_Storyboard{SUFFIX}.jpg',quality=95)
    bases['intro',0].save(ROOT/f'Demo_Preview{SUFFIX}.png')
    if mode=='preview': return
    output=ROOT/f'Playwright_Studio_Demo{SUFFIX}.mp4'
    cmd=[str(FFMPEG),'-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
         '-i',str(WORK/'narration.wav'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','19',
         '-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-map_metadata','-1',
         '-metadata','title=Playwright Studio — Complete Demo','-metadata','comment=Actual local demo footage with synthetic English narration.',
         '-t',str(TOTAL),str(output)]
    with (WORK/'encoder.log').open('wb') as log:
        process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        previous=None
        try:
            for scene in SCENES:
                duration=scene['seconds']; sid=scene['id']
                for frame_number in range(duration*FPS):
                    t=frame_number/FPS
                    phase=int(t>=3) if sid=='code' else int(t>=3.8) if sid=='report' else 0
                    im=bases[sid,phase].copy()
                    if sid=='run':
                        frame=Image.open(footage[min(int(t*FPS),len(footage)-1)]).convert('RGB')
                        im.paste(frame,(675,250))
                    if sid=='evidence':
                        frame=Image.open(footage[min(int(t*FPS),len(footage)-1)]).convert('RGB').resize((640,360),Image.Resampling.LANCZOS)
                        im.paste(frame,(1085,262))
                        pill(im,(995,269),'RECORDED VIDEO')
                    if sid=='flow':
                        active=min(6,int(t/duration*7))
                        ImageDraw.Draw(im).rounded_rectangle((656,330+active*65,1821,390+active*65),radius=10,outline=TEAL,width=3)
                    if sid=='setup':
                        active=min(2,int(t/duration*3))
                        ImageDraw.Draw(im).rounded_rectangle((1205,385+active*99,1799,463+active*99),radius=12,outline=TEAL,width=3)
                    subtitle(im,scene)
                    d=ImageDraw.Draw(im)
                    d.rectangle((0,1073,int(W*(elapsed+t)/TOTAL),1079),fill=TEAL)
                    if previous is not None and t<.27:
                        im=Image.blend(previous,im,t/.27)
                    if elapsed+t>TOTAL-.45:
                        im=Image.blend(im,Image.new('RGB',(W,H),'#080F1D'),(elapsed+t-(TOTAL-.45))/.45)
                    process.stdin.write(im.tobytes())
                previous=im.copy(); elapsed+=duration
                print(f'Encoded {sid}: {elapsed}/{TOTAL} seconds',flush=True)
        finally:
            process.stdin.close()
        if process.wait()!=0: raise RuntimeError((WORK/'encoder.log').read_text())
    print(f'Finished: {output}',flush=True)

if __name__=='__main__': main()
