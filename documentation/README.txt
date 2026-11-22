PLAYWRIGHT STUDIO COMPLETE APPLICATION GUIDE

output/Playwright_Studio_Complete_Guide.pdf is the final 34-page manual.
It includes 32 linked sections, nine labeled vector diagrams, user procedures,
technical architecture, session handling, report interpretation, troubleshooting,
command-line options, exported-suite instructions, and maintenance guidance.
Examples use replaceable values rather than personal or account details.

AUTHORING
guide_content.py contains the structured document text.
build_guide.py creates the PDF with linked contents and bookmarks.
check_guide.py renders every page and checks bounds, metadata, navigation,
identifying text patterns, and the sample flows against the application's parser.
The qa/ directory holds temporary layout images and verification files and is ignored.

Use Python with reportlab, pypdf, pypdfium2, pdfplumber, and Pillow installed.
The builder uses the standard Windows Segoe UI and Consolas fonts.
Run from the repository root:

  python documentation/build_guide.py
  python documentation/check_guide.py

After any layout or content change, inspect the rendered qa/page-*.png images.
Automated checks alone cannot establish readable or correct diagrams.
The guide documents application behavior from the source; it does not claim that
all deployed identity providers or office environments have been verified.
