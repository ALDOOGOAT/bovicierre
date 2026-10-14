import {defineConfig} from '@playwright/test';
// Herramientas manuales fuera de la puerta de pruebas, en Chrome real con GPU: videos de uso (tutorials.record.ts, 1280×720)
// y medición de rendimiento (perf.measure.ts). Uso: BOVI_UI_TEST_URL=http://127.0.0.1:15180 npx playwright test -c playwright.tools.config.ts <archivo>
export default defineConfig({testDir:'./tests_e2e',testMatch:/(tutorials\.record|perf\.measure)\.ts$/,workers:1,retries:0,timeout:600000,expect:{timeout:20000},reporter:'list',outputDir:'/tmp/bovicierre-tools',
    use:{baseURL:process.env.BOVI_UI_TEST_URL||'http://127.0.0.1:15180',headless:false,viewport:{width:1280,height:720},launchOptions:{executablePath:process.env.CHROME_BIN||'/usr/bin/google-chrome'},actionTimeout:20000,trace:'off'}});
