const fs = require('fs');
const path = require('path');

/**
 * Self-contained Offline Enterprise Playwright Reporter producing Complete-Suite-Test-Report/index.html.
 * Zero external CDN dependencies.
 */
class EnterpriseSuiteReporter {
  constructor() {
    this.results = [];
    this.startTime = Date.now();
  }

  onTestEnd(test, result) {
    const testId = `PW-${String(this.results.length + 1).padStart(3, '0')}`;
    const reportDir = path.resolve(__dirname, '../Complete-Suite-Test-Report');
    const ssDir = path.join(reportDir, 'Evidence', 'Screenshots', testId);
    const recDir = path.join(reportDir, 'Evidence', 'Recording', testId);
    const traceDir = path.join(reportDir, 'Evidence', 'Trace', testId);
    fs.mkdirSync(ssDir, { recursive: true });
    fs.mkdirSync(recDir, { recursive: true });
    fs.mkdirSync(traceDir, { recursive: true });

    let finalScreenshotRel = '';
    let videoRel = '';
    let traceRel = '';
    let stepIdx = 0;
    const stepScreenshots = [];

    for (const att of result.attachments || []) {
      const ctype = (att.contentType || '').toLowerCase();
      const name = (att.name || '').toLowerCase();
      if (ctype.startsWith('image/') || name.includes('screenshot')) {
        stepIdx += 1;
        const fname = stepIdx === 1 ? 'final-screenshot.png' : `${String(stepIdx).padStart(2, '0')}-step.png`;
        const dest = path.join(ssDir, fname);
        if (att.path && fs.existsSync(att.path)) {
          fs.copyFileSync(att.path, dest);
        } else if (att.body) {
          fs.writeFileSync(dest, att.body);
        }
        const rel = `Evidence/Screenshots/${testId}/${fname}`;
        if (!finalScreenshotRel) finalScreenshotRel = rel;
        stepScreenshots.push({ rel, caption: att.name || fname });
      } else if (name === 'video' || ctype.includes('video') || (att.path && att.path.endsWith('.webm'))) {
        if (att.path && fs.existsSync(att.path)) {
          fs.copyFileSync(att.path, path.join(recDir, 'video.webm'));
          videoRel = `Evidence/Recording/${testId}/video.webm`;
        }
      } else if (name === 'trace' || (att.path && att.path.endsWith('.zip'))) {
        if (att.path && fs.existsSync(att.path)) {
          fs.copyFileSync(att.path, path.join(traceDir, 'trace.zip'));
          traceRel = `Evidence/Trace/${testId}/trace.zip`;
        }
      }
    }

    this.results.push({
      test_id: testId,
      title: test.title,
      status: result.status === 'timedOut' ? 'failed' : result.status,
      duration_s: Number(((result.duration || 0) / 1000).toFixed(2)),
      profile: process.env.TEST_ACCESS_PROFILE || 'SUPER_USER',
      final_screenshot: finalScreenshotRel,
      step_screenshots: stepScreenshots,
      video_rel_path: videoRel,
      trace_rel_path: traceRel,
      error_message: result.error ? (result.error.message || '') : '',
    });
  }

  onEnd() {
    const reportDir = path.resolve(__dirname, '../Complete-Suite-Test-Report');
    for (const sub of ['Plans', 'Screenshots', 'Recording', 'Trace']) {
      fs.mkdirSync(path.join(reportDir, 'Evidence', sub), { recursive: true });
    }
    const profile = process.env.TEST_ACCESS_PROFILE || 'SUPER_USER' || 'PUBLIC';
    const total = this.results.length;
    const passed = this.results.filter((r) => r.status === 'passed').length;
    const failed = this.results.filter((r) => r.status === 'failed').length;
    const skipped = this.results.filter((r) => r.status === 'skipped').length;
    const duration = Number(this.results.reduce((acc, r) => acc + r.duration_s, 0).toFixed(2));
    const dateStr = new Date().toISOString().slice(0, 10);

    const cards = this.results
      .map(
        (tc, i) => `
      <div class="test-card ${tc.status}" id="test-${i}">
        <div class="test-header" onclick="toggleExpand('test-${i}')">
          <div class="test-card-heading">
            <span class="test-id-col">${tc.test_id}</span>
            <span class="test-title-col">${tc.title}</span>
          </div>
          <span class="test-status ${tc.status}">${tc.status.toUpperCase()}</span>
          <span class="test-duration">${tc.duration_s.toFixed(2)}s</span>
          <span class="expand-icon">▼</span>
        </div>
        <div class="test-body">
          <div class="test-meta"><span><strong>Profile:</strong> ${profile}</span></div>
          ${tc.final_screenshot ? `<div class="final-ss"><h4>Final Screenshot</h4><img src="${tc.final_screenshot}" style="max-width:640px"></div>` : ''}
          ${tc.video_rel_path ? `<div class="video-container"><h4>Screen Recording</h4><video controls preload="metadata" style="width:100%;max-width:640px"><source src="${tc.video_rel_path}" type="video/webm"></video></div>` : ''}
          ${tc.trace_rel_path ? `<div class="trace-section"><h4>Trace</h4><p><a href="${tc.trace_rel_path}" download>trace.zip</a></p></div>` : ''}
          <div class="actual-result"><h4>Actual Result</h4><p><strong>Status:</strong> ${tc.status}</p></div>
        </div>
      </div>`
      )
      .join('\n');

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Shutterstock Studio Portal Detailed Test Evidence Report — 127.0.0.1:56844 — ${profile}</title>
<style>
body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #f5f5f5; color: #333; margin: 0; }
.report-header { background: #1a1a2e; color: #fff; padding: 24px; }
.summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 16px; margin-top: 16px; }
.summary-card { background: rgba(255,255,255,0.1); border-radius: 8px; padding: 12px; text-align: center; }
.summary-card .summary-value { font-size: 1.6em; font-weight: bold; }
.summary-card.passed .summary-value { color: #4caf50; }
.summary-card.failed .summary-value { color: #f44336; }
.container { max-width: 1100px; margin: 0 auto; padding: 24px 16px; }
.test-card { background: #fff; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.test-card.passed { border-left: 4px solid #4caf50; }
.test-card.failed { border-left: 4px solid #f44336; }
.test-header { display: flex; align-items: center; padding: 12px 16px; cursor: pointer; gap: 12px; }
.test-card-heading { display: grid; grid-template-columns: minmax(150px, auto) 1fr; gap: 16px; flex: 1; }
.test-body { display: none; padding: 0 16px 16px; }
.test-card.expanded .test-body { display: block; }
</style>
</head>
<body>
<div class="report-header">
  <h1>Shutterstock Studio Portal Detailed Test Evidence Report — 127.0.0.1:56844 — ${profile}</h1>
  <div class="summary-grid">
    <div class="summary-card"><div class="summary-value">${total}</div><div class="summary-label">Total</div></div>
    <div class="summary-card passed"><div class="summary-value">${passed}</div><div class="summary-label">Passed</div></div>
    <div class="summary-card failed"><div class="summary-value">${failed}</div><div class="summary-label">Failed</div></div>
    <div class="summary-card"><div class="summary-value">${skipped}</div><div class="summary-label">Skipped</div></div>
    <div class="summary-card"><div class="summary-value">${duration}s</div><div class="summary-label">Duration</div></div>
    <div class="summary-card"><div class="summary-value">${dateStr}</div><div class="summary-label">Date</div></div>
    <div class="summary-card profile"><div class="summary-value">${profile}</div><div class="summary-label">Profile</div></div>
  </div>
</div>
<div class="container">${cards}</div>
<script>function toggleExpand(id){document.getElementById(id).classList.toggle('expanded');}</script>
</body>
</html>`;

    fs.writeFileSync(path.join(reportDir, 'index.html'), html, 'utf-8');
  }
}

module.exports = EnterpriseSuiteReporter;