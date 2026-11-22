PLAYWRIGHT STUDIO — DEMO VIDEO

REVISED EDIT
Playwright_Studio_Demo_Revised.mp4 is the updated 88-second Full HD walkthrough.
It removes the GitHub address and download reference, with no personal names or
capture dates on screen. Product and framework labels remain for clarity.
The male neural voice uses a lower pitch, restrained bass enhancement, deliberate
phrase breaks, and a brief thoughtful "hmm" in the login diagnosis chapter.
This is synthetic narration, not a recorded human speaker.
Playwright_Studio_Demo_Revised.srt contains the matching captions.
Demo_Storyboard_Revised.jpg and Verification_Revised.json document this edit.
Demo_Preview_Revised.png is the cover image. The edit includes burned-in subtitles,
chapter labels, actual browser footage, and screenshots of the desktop application.

Coverage:
• URL, existing projects, and the built-in demo
• Role-based login profiles
• Ordered click, fill, select, checkbox, UI and API assertions
• Fresh/saved sessions, login markers, background and manual modes
• Python, Java, TypeScript and JavaScript outputs and the output folder
• Real flow execution and individual step outcomes
• Report filters, executed versus unexecuted cases, screenshots, video, APIs and trace
• Test plans, generated files, numbered project runs and CLI execution
• Login-loop detection and skipped dependent steps

Capture dates, report date cards and the desktop clock are not shown in the video.
The original reports were preserved. Date cards were hidden only for the capture view.
The successful run uses the disposable local QA Task Portal; the login-loop example
uses the local authentication regression fixture. No office deployment is depicted.

AUTHORING AND VERIFICATION
The published MP4 and PDF guide can be used directly; no authoring tools are needed.
The raw assets, local project, work files, and superseded exports remain gitignored.
Rebuilding the video therefore requires supplying the local captures under assets/,
including evidence.json with paths to the actual recording, screenshot, and trace.
Do not substitute invented evidence for missing recordings.

Authoring dependencies: Python, Pillow, NumPy, edge-tts, Playwright, Edge, Windows
Segoe UI/Consolas fonts, and FFmpeg with libx264. Set FFMPEG to the executable path;
otherwise the scripts use the documented project-local imageio-ffmpeg location.
Set FFPROBE to ffprobe's path, or install ffprobe on PATH, for verification.

1. python demo_media/revise_narration.py
2. python demo_media/render_demo.py --revised
3. python demo_media/verify_video.py --revised

Neural narration generation sends the demo narration text to the speech service.
The Studio application itself does not use that service. Generated narration is
cached in the ignored assets directory. storyboard_revised.json contains the final
script and chapter timing; storyboard.json supplies the base structure. narrate.ps1
is the earlier optional Windows System.Speech narration helper.

capture_reports.py expects the local demo report beneath project/ and FAILED_REPORT
set to the failed-authentication report's index.html. It captures presentation views
without altering the original report data. Other application screenshots must be
provided locally before a full video rebuild.
