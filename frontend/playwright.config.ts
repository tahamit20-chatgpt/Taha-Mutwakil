import {existsSync} from 'node:fs';
import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'./e2e',workers:1,use:{baseURL:process.env.BIDFIT_TEST_BASE_URL||'http://127.0.0.1:8000',headless:true,launchOptions:{executablePath:process.env.CHROMIUM_PATH||(existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined),args:['--no-sandbox']}},reporter:'list'});
