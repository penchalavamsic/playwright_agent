package com.corp.qa.listeners;

import com.corp.qa.pages.LoginPage;
import org.testng.ITestContext;
import org.testng.ITestListener;
import org.testng.ITestResult;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

/**
 * Self-contained Offline Enterprise Report Listener producing Complete-Suite-Test-Report/index.html.
 * Zero external CDN links.
 */
public class EnterpriseReportListener implements ITestListener {

    private final List<ITestResult> results = new ArrayList<>();

    @Override
    public void onTestSuccess(ITestResult result) {
        results.add(result);
    }

    @Override
    public void onTestFailure(ITestResult result) {
        results.add(result);
    }

    @Override
    public void onTestSkipped(ITestResult result) {
        results.add(result);
    }

    @Override
    public void onFinish(ITestContext context) {
        try {
            Path reportDir = Paths.get("..", "Complete-Suite-Test-Report");
            Files.createDirectories(reportDir.resolve("Evidence").resolve("Plans"));
            Files.createDirectories(reportDir.resolve("Evidence").resolve("Screenshots"));
            Files.createDirectories(reportDir.resolve("Evidence").resolve("Recording"));
            Files.createDirectories(reportDir.resolve("Evidence").resolve("Trace"));

            int total = results.size();
            int passed = 0;
            int failed = 0;
            int skipped = 0;
            double totalDuration = 0.0;

            StringBuilder cards = new StringBuilder();
            String profile = LoginPage.getEnv("TEST_ACCESS_PROFILE", "STANDARD_USER");

            for (int i = 0; i < results.size(); i++) {
                ITestResult r = results.get(i);
                String status = (r.getStatus() == ITestResult.SUCCESS) ? "passed"
                        : (r.getStatus() == ITestResult.FAILURE ? "failed" : "skipped");
                if ("passed".equals(status)) passed++;
                else if ("failed".equals(status)) failed++;
                else skipped++;

                double dur = Math.max(0.01, (r.getEndMillis() - r.getStartMillis()) / 1000.0);
                totalDuration += dur;
                String testId = String.format("JAVA-%03d", i + 1);
                String title = r.getMethod().getDescription() != null && !r.getMethod().getDescription().isEmpty()
                        ? r.getMethod().getDescription()
                        : r.getMethod().getMethodName();
                String ssRel = "Evidence/Screenshots/" + testId + "/final-screenshot.png";
                String vidRel = "Evidence/Recording/" + testId + "/video.webm";

                cards.append("<div class=\"test-card ").append(status).append("\" id=\"test-").append(i).append("\">")
                     .append("<div class=\"test-header\" onclick=\"toggleExpand('test-").append(i).append("')\">")
                     .append("<div class=\"test-card-heading\"><span class=\"test-id-col\">").append(testId).append("</span>")
                     .append("<span class=\"test-title-col\">").append(title).append("</span></div>")
                     .append("<span class=\"test-status ").append(status).append("\">").append(status.toUpperCase()).append("</span>")
                     .append("<span class=\"test-duration\">").append(String.format("%.2fs", dur)).append("</span>")
                     .append("<span class=\"expand-icon\">▼</span></div>")
                     .append("<div class=\"test-body\"><div class=\"test-meta\"><span><strong>Profile:</strong> ").append(profile).append("</span></div>")
                     .append("<div class=\"final-ss\"><h4>Final Screenshot</h4><img src=\"").append(ssRel).append("\" style=\"max-width:640px\"></div>")
                     .append("<div class=\"video-container\"><h4>Screen Recording</h4><video controls preload=\"metadata\" style=\"width:100%;max-width:640px\"><source src=\"").append(vidRel).append("\" type=\"video/webm\"></video></div>")
                     .append("<div class=\"actual-result\"><h4>Actual Result</h4><p><strong>Status:</strong> ").append(status).append("</p></div></div></div>");
            }

            String html = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><title>Swag Labs Detailed Test Evidence Report — saucedemo.com — " + profile + "</title>"
                    + "<style>body{font-family:'Segoe UI',Tahoma,sans-serif;background:#f5f5f5;color:#333;margin:0;}"
                    + ".report-header{background:#1a1a2e;color:#fff;padding:24px;}"
                    + ".summary-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:16px;margin-top:16px;}"
                    + ".summary-card{background:rgba(255,255,255,0.1);border-radius:8px;padding:12px;text-align:center;}"
                    + ".summary-card .summary-value{font-size:1.6em;font-weight:bold;}"
                    + ".summary-card.passed .summary-value{color:#4caf50;}.summary-card.failed .summary-value{color:#f44336;}"
                    + ".container{max-width:1100px;margin:0 auto;padding:24px 16px;}"
                    + ".test-card{background:#fff;border-radius:8px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,0.1);}"
                    + ".test-card.passed{border-left:4px solid #4caf50;}.test-card.failed{border-left:4px solid #f44336;}"
                    + ".test-header{display:flex;align-items:center;padding:12px 16px;cursor:pointer;gap:12px;}"
                    + ".test-card-heading{display:grid;grid-template-columns:minmax(150px,auto) 1fr;gap:16px;flex:1;}"
                    + ".test-body{display:none;padding:0 16px 16px;}.test-card.expanded .test-body{display:block;}</style></head><body>"
                    + "<div class=\"report-header\"><h1>Swag Labs Detailed Test Evidence Report — saucedemo.com — " + profile + "</h1>"
                    + "<div class=\"summary-grid\">"
                    + "<div class=\"summary-card\"><div class=\"summary-value\">" + total + "</div><div class=\"summary-label\">Total</div></div>"
                    + "<div class=\"summary-card passed\"><div class=\"summary-value\">" + passed + "</div><div class=\"summary-label\">Passed</div></div>"
                    + "<div class=\"summary-card failed\"><div class=\"summary-value\">" + failed + "</div><div class=\"summary-label\">Failed</div></div>"
                    + "<div class=\"summary-card\"><div class=\"summary-value\">" + skipped + "</div><div class=\"summary-label\">Skipped</div></div>"
                    + "<div class=\"summary-card\"><div class=\"summary-value\">" + String.format("%.2fs", totalDuration) + "</div><div class=\"summary-label\">Duration</div></div>"
                    + "<div class=\"summary-card\"><div class=\"summary-value\">" + LocalDate.now() + "</div><div class=\"summary-label\">Date</div></div>"
                    + "<div class=\"summary-card profile\"><div class=\"summary-value\">" + profile + "</div><div class=\"summary-label\">Profile</div></div>"
                    + "</div></div><div class=\"container\">" + cards + "</div>"
                    + "<script>function toggleExpand(id){document.getElementById(id).classList.toggle('expanded');}</script></body></html>";

            Files.write(reportDir.resolve("index.html"), html.getBytes(StandardCharsets.UTF_8));
        } catch (IOException ignored) {
        }
    }
}