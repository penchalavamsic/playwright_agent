package com.corp.qa.listeners;

import com.corp.qa.tests.BaseTest;
import com.google.gson.GsonBuilder;
import org.testng.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class EnterpriseReportListener implements ITestListener {
    private final List<ITestResult> results = new ArrayList<>();
    public void onTestSuccess(ITestResult r) { results.add(r); }
    public void onTestFailure(ITestResult r) { results.add(r); }
    public void onTestSkipped(ITestResult r) { results.add(r); }
    private static String esc(Object s) { return String.valueOf(s == null ? "" : s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&#39;"); }

    public void onFinish(ITestContext context) {
        try {
            Path root = BaseTest.REPORT_ROOT;
            Files.createDirectories(root);
            List<Map<String, Object>> cases = new ArrayList<>();
            int passed = 0, failed = 0, skipped = 0;
            StringBuilder cards = new StringBuilder();
            for (ITestResult r : results) {
                String status = r.isSuccess() ? "passed" : r.getStatus() == ITestResult.FAILURE ? "failed" : "skipped";
                if (status.equals("passed")) passed++; else if (status.equals("failed")) failed++; else skipped++;
                Map<String, Object> record = new LinkedHashMap<>();
                String title = r.getTestClass().getName() + "." + r.getMethod().getMethodName();
                record.put("test_id", title); record.put("title", title); record.put("status", status);
                record.put("duration_s", (r.getEndMillis() - r.getStartMillis()) / 1000.0);
                record.put("error_message", r.getThrowable() == null ? "" : r.getThrowable().toString());
                for (String key : List.of("final_route", "final_screenshot", "video_rel_path", "trace_rel_path", "media_note"))
                    record.put(key, r.getAttribute(key) == null ? "" : r.getAttribute(key));
                cases.add(record);
                cards.append("<details open class=\"").append(status).append("\"><summary>").append(esc(title)).append(" — ").append(status.toUpperCase()).append("</summary>");
                cards.append("<p>Duration: ").append(record.get("duration_s")).append("s</p><pre>").append(esc(record.get("error_message"))).append("</pre>");
                String screenshot = String.valueOf(record.get("final_screenshot"));
                String video = String.valueOf(record.get("video_rel_path"));
                String trace = String.valueOf(record.get("trace_rel_path"));
                if (!screenshot.isEmpty()) cards.append("<img width=\"640\" src=\"").append(esc(screenshot)).append("\" alt=\"Final state\">");
                if (!video.isEmpty()) cards.append("<video controls width=\"640\" src=\"").append(esc(video)).append("\"></video>");
                if (!trace.isEmpty()) cards.append("<p><a href=\"").append(esc(trace)).append("\">Download Playwright trace</a></p>");
                cards.append("</details>");
            }
            Map<String, Object> summary = new LinkedHashMap<>();
            summary.put("total", cases.size()); summary.put("passed", passed); summary.put("failed", failed); summary.put("skipped", skipped); summary.put("test_cases", cases);
            Files.writeString(root.resolve("report-summary.json"), new GsonBuilder().setPrettyPrinting().create().toJson(summary), StandardCharsets.UTF_8);
            String html = "<!doctype html><html><head><meta charset=\"utf-8\"><title>Java flow execution report</title><style>body{font:16px system-ui;background:#edf2f8;margin:30px;color:#17283f}details{padding:24px;background:white;margin:20px 0;border-radius:10px;border-left:5px solid #889}.passed{border-color:#16824a}.failed{border-color:#c63232}img,video{max-width:100%;display:block;margin:16px 0}pre{white-space:pre-wrap}summary{font-weight:bold;cursor:pointer}</style></head><body><h1>Java flow execution report</h1><p>Total: " + cases.size() + " | Passed: " + passed + " | Failed: " + failed + " | Skipped: " + skipped + "</p>" + cards + "</body></html>";
            Files.writeString(root.resolve("index.html"), html, StandardCharsets.UTF_8);
            System.out.println("Execution report: " + root.resolve("index.html").toAbsolutePath());
        } catch (Exception ex) { throw new RuntimeException("Could not write execution report", ex); }
    }
}
