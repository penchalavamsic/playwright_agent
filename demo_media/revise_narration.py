"""Generate the revised, anonymous male narration; keep the original assets."""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import wave

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'tmp/voice_runtime'))
import edge_tts

FFMPEG = Path(os.environ.get('FFMPEG') or ROOT.parent / 'tmp/media_runtime/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
OUT = ROOT / 'assets/male-narration'
OUT.mkdir(exist_ok=True)
VOICE = 'en-US-ChristopherNeural'
LINES = {
    'intro': ['Playwright Studio.', 'Turn your test flows into real evidence.'],
    'setup': ['Start with your application URL.', 'Open a project, or choose Try demo.'],
    'profile': ['Select a role.', 'Save its credentials with Edit, then choose that profile.'],
    'flow': ['Write each action in order. Log in, click, fill, select, and check.', 'Verify text and API results.'],
    'session': ['Open Advanced settings. Choose a fresh or saved session.', 'Set a success marker, or inspect a manual session.'],
    'exports': ['Choose your languages and frameworks.', 'Include a test plan, and set the output folder.'],
    'run': ['Click Run test.', 'The browser follows your steps, creates the task, and verifies the response. This is real footage.'],
    'results': ['Review every step.', 'Failures stop dependent actions, so the results reflect what actually happened.'],
    'report': ['Open the full report.', 'Filter results and expand a case. Advisory plans are clearly marked as not run.'],
    'evidence': ['Inspect screenshots and video.', 'Review API responses, or download the trace. Evidence stays with each report.'],
    'code': ['Review the test plan and generated files.', 'Reopen for another run, or execute the exported suites.'],
    'loop': ['Hmm. A login loop?', 'Check redirects and responses. Stop once, and skip dependent steps.'],
    'close': ['Playwright Studio.', 'Ready for your next test.'],
}

async def generate(scene, semaphore):
    async with semaphore:
        sid = scene['id']
        parts = []
        for index, phrase in enumerate(LINES[sid]):
            key = hashlib.sha256(phrase.encode()).hexdigest()[:8]
            target = OUT / f'{sid}-{index}-{key}.mp3'
            if not target.exists() or target.stat().st_size < 1000:
                await edge_tts.Communicate(phrase, VOICE, rate='-3%', pitch='-5Hz').save(str(target))
            wav = target.with_suffix('.wav')
            subprocess.run([str(FFMPEG), '-y', '-v', 'error', '-i', str(target),
                            '-af', 'silenceremove=start_periods=1:start_duration=0.02:start_threshold=-48dB:start_silence=0.04,areverse,silenceremove=start_periods=1:start_duration=0.02:start_threshold=-48dB:start_silence=0.10,areverse',
                            '-ar', '48000', '-ac', '1', str(wav)], check=True)
            with wave.open(str(wav)) as reader:
                parts.append(reader.readframes(reader.getnframes()))
        pause = bytes(round(48000 * .20) * 2)
        with wave.open(str(OUT / f'{sid}.wav'), 'wb') as writer:
            writer.setnchannels(1)
            writer.setsampwidth(2)
            writer.setframerate(48000)
            writer.writeframes(pause.join(parts))
        duration = (sum(len(p) for p in parts) + len(pause)) / 96000
        print(f'{sid}: {duration:.2f}s / {scene["seconds"]}s', flush=True)
        return {'scene': sid, 'raw_seconds': duration, 'slot_seconds': scene['seconds']}

async def main():
    scenes = json.loads((ROOT / 'storyboard.json').read_text(encoding='utf-8'))
    for scene in scenes:
        scene['voice'] = ' '.join(LINES[scene['id']])
        scene['seconds'] = {'intro': 4, 'setup': 6, 'flow': 9, 'loop': 8}.get(scene['id'], scene['seconds'])
    scenes[-1]['caption'] = 'A complete workflow, from setup to reusable tests.'
    (ROOT / 'storyboard_revised.json').write_text(json.dumps(scenes, indent=2), encoding='utf-8')
    semaphore = asyncio.Semaphore(2)
    durations = await asyncio.gather(*(generate(s, semaphore) for s in scenes))
    (OUT / 'voice-settings.json').write_text(json.dumps({
        'voice': VOICE, 'rate': '-3%', 'pitch': '-5Hz', 'phrase_gap_seconds': .20,
        'type': 'synthetic neural narration', 'durations': durations,
    }, indent=2), encoding='utf-8')

if __name__ == '__main__':
    asyncio.run(main())
