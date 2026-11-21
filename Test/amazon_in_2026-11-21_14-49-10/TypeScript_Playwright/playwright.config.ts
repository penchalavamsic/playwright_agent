import { defineConfig, devices } from '@playwright/test';
import * as dotenv from 'dotenv';
import * as path from 'path';

dotenv.config({ path: path.resolve(__dirname, '../.env') });

export default defineConfig({
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