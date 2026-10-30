// Rasterize SVG files with headless Chromium: node render.js out_dir file1.svg [file2.svg ...]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [outDir, ...files] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const f of files) {
    const svg = fs.readFileSync(f, 'utf8');
    const w = +svg.match(/width="(\d+)"/)[1], h = +svg.match(/height="(\d+)"/)[1];
    await page.setViewportSize({ width: w, height: h });
    await page.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    const out = path.join(outDir, path.basename(f).replace(/\.svg$/, '.png'));
    await page.locator('svg').first().screenshot({ path: out, omitBackground: true });
  }
  await browser.close();
})();
