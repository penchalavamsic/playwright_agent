const { defineConfig, devices } = require('@playwright/test');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30000,
  expect: {
    timeout: 5000,
  },
  reporter: [
    ['./enterprise-reporter.js'],
    ['json', { outputFile: '../Complete-Suite-Test-Report/report-summary.json' }],
  ],
  use: {
    baseURL: process.env.BASE_URL || '',
    headless: true,
    ignoreHTTPSErrors: true,
    channel: 'chrome',
    screenshot: 'on',
    trace: 'on',
    video: 'on',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});