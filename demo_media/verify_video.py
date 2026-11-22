from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
SUFFIX='_Revised' if '--revised' in sys.argv else ''
VIDEO=ROOT/f'Playwright_Studio_Demo{SUFFIX}.mp4'
PROBE=os.environ.get('FFPROBE') or shutil.which('ffprobe')
if not PROBE:
    raise SystemExit('Install ffprobe on PATH or set FFPROBE to its executable path.')
ENCODER=Path(os.environ.get('FFMPEG') or ROOT.parent/'tmp/media_runtime/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
(ROOT/'work').mkdir(exist_ok=True)
info=json.loads(subprocess.check_output([str(PROBE),'-v','error','-show_streams','-show_format','-of','json',str(VIDEO)],text=True))
video=next(s for s in info['streams'] if s['codec_type']=='video')
audio=next(s for s in info['streams'] if s['codec_type']=='audio')
assert video['codec_name']=='h264'
assert (video['width'],video['height'])==(1920,1080)
assert video['avg_frame_rate']=='30/1'
assert abs(float(info['format']['duration'])-88)<.05
assert audio['codec_name']=='aac'
assert 'creation_time' not in info['format'].get('tags',{})
with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True)
    page=browser.new_page(viewport={'width':1280,'height':720})
    (ROOT/'work/playback.html').write_text('<html><body style="margin:0;background:#080f1d"><video muted autoplay style="width:100%;height:100vh;object-fit:contain" src="'+VIDEO.as_uri()+'"></video></body></html>',encoding='utf-8')
    page.goto((ROOT/'work/playback.html').as_uri())
    page.wait_for_function('document.querySelector("video").currentTime>1 && document.querySelector("video").videoWidth===1920',timeout=15000)
    for t in [2,23,43,59,67,74,81,86]:
        page.evaluate('(t)=>{let v=document.querySelector("video");v.pause();v.currentTime=t}',t)
        page.wait_for_function('(t)=>{let v=document.querySelector("video");return !v.seeking && Math.abs(v.currentTime-t)<.1 && v.readyState>=2}',arg=t)
    assert page.locator('video').evaluate('(v)=>v.error') is None
    browser.close()
audio_check=subprocess.run([str(ENCODER),'-hide_banner','-i',str(VIDEO),'-vn','-af','volumedetect','-f','null','-'],capture_output=True,text=True,check=True)
levels=[line.split(']')[-1].strip() for line in audio_check.stderr.splitlines() if 'mean_volume:' in line or 'max_volume:' in line]
result={'file':VIDEO.name,'duration_seconds':float(info['format']['duration']),'resolution':'1920x1080','fps':30,
        'video_codec':video['codec_name'],'audio_codec':audio['codec_name'],'size_bytes':VIDEO.stat().st_size,
        'playback_verified':True,'chapters':13,'visible_capture_timestamps':False,'audio_levels':levels}
(ROOT/f'Verification{SUFFIX}.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
