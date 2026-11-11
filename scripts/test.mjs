import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import { createServer } from 'node:http';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { extname, resolve, sep } from 'node:path';
import assert from 'node:assert/strict';

const root = resolve('docs');
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.json': 'application/json' };
const server = createServer(async (request, response) => {
  const url = new URL(request.url, 'http://localhost');
  if (!url.pathname.startsWith('/pro-ter-pa-v2/')) {
    response.writeHead(404).end();
    return;
  }
  const relative = decodeURIComponent(url.pathname.slice('/pro-ter-pa-v2/'.length));
  let path = resolve(root, relative);
  if (path !== root && !path.startsWith(root + sep)) {
    response.writeHead(403).end();
    return;
  }
  if (!extname(path)) path += '/index.html';
  try {
    response.setHeader('Content-Type', types[extname(path)] || 'application/octet-stream');
    response.end(await readFile(path));
  } catch {
    response.writeHead(404).end();
  }
});
await new Promise(ready => server.listen(0, '127.0.0.1', ready));
const base = `http://127.0.0.1:${server.address().port}/pro-ter-pa-v2/`;
const browser = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
const evidence = { pages: [], errors: [], screenshots: [] };
await mkdir('test-results', { recursive: true });
try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
  const page = await context.newPage();
  page.on('pageerror', error => evidence.errors.push(error.message));
  page.on('response', response => {
    if (response.status() >= 400) evidence.errors.push(`${response.status()} ${response.url()}`);
  });
  const routes = ['', 'chantier-de-terrassement/', 'nos-amenagements/', 'assainissement/', 'galerie-photos/', 'contact/', 'mentions-legales/'];
  for (const route of routes) {
    const response = await page.goto(base + route);
    assert.equal(response.status(), 200);
    await page.locator('h1').waitFor();
    await page.evaluate(async () => {
      document.querySelectorAll('img').forEach(image => { image.loading = 'eager'; });
      await Promise.all([...document.images].map(image => image.decode().catch(() => {})));
    });
    const broken = await page.locator('img[src]').evaluateAll(images => images.filter(image => !image.complete || !image.naturalWidth).map(image => image.src));
    assert.deepEqual(broken, [], `broken images on ${route}`);
    const audit = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
    assert.deepEqual(audit.violations.map(item => `${item.id}: ${item.nodes.map(node => node.target).join(', ')}`), [], `accessibility on ${route}`);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, `desktop overflow on ${route}`);
    evidence.pages.push({ route, status: response.status(), axeViolations: audit.violations.length, images: await page.locator('img').count() });
    if (route === '') {
      await page.screenshot({ path: 'test-results/desktop-home.png', fullPage: true });
      evidence.screenshots.push('desktop-home.png');
      await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(() => document.activeElement.className), 'skip');
      await page.keyboard.press('Enter');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'contenu');
    }
    if (route === 'galerie-photos/') {
      const photos = page.locator('[data-photo]');
      assert.ok(await photos.count() >= 28);
      await photos.first().click();
      await page.locator('dialog[open]').waitFor();
      assert.equal(await page.locator('[data-counter]').textContent(), `1 / ${await photos.count()}`);
      await page.keyboard.press('ArrowRight');
      assert.equal(await page.locator('[data-counter]').textContent(), `2 / ${await photos.count()}`);
      await page.keyboard.press('ArrowLeft');
      await page.keyboard.press('Escape');
      assert.equal(await page.locator('dialog[open]').count(), 0);
      assert.equal(await photos.first().evaluate(element => element === document.activeElement), true);
    }
    if (route === 'contact/') {
      assert.ok(await page.locator('a[href="mailto:proterpa@orange.fr"]').count() >= 1);
      assert.ok(await page.locator('a[href="tel:+33762058945"]').count() >= 1);
      assert.equal(await page.locator('form').count(), 0);
    }
  }
  await page.setViewportSize({ width: 390, height: 844 });
  for (const route of routes) {
    await page.goto(base + route);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, `mobile overflow on ${route}`);
    const button = page.locator('.menu-toggle');
    await button.click();
    assert.equal(await button.getAttribute('aria-expanded'), 'true');
    await page.keyboard.press('Escape');
    assert.equal(await button.getAttribute('aria-expanded'), 'false');
    if (route === '') {
      await page.evaluate(async () => {
        document.querySelectorAll('img[src]').forEach(image => { image.loading = 'eager'; });
        await Promise.all([...document.images].filter(image => image.hasAttribute('src')).map(image => image.decode()));
      });
      await page.screenshot({ path: 'test-results/mobile-home.png', fullPage: true });
      evidence.screenshots.push('mobile-home.png');
      const audit = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
      assert.deepEqual(audit.violations.map(item => item.id), []);
    }
  }
  await context.close();
  const noJs = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  const staticPage = await noJs.newPage();
  await staticPage.goto(base);
  assert.ok(await staticPage.locator('main a[href*="contact"]').count());
  assert.ok(await staticPage.locator('footer a[href*="galerie-photos"]').count());
  await noJs.close();
  assert.deepEqual(evidence.errors, []);
  await writeFile('test-results/evidence.json', JSON.stringify(evidence, null, 2));
  console.log(JSON.stringify(evidence, null, 2));
} finally {
  await browser.close();
  await new Promise(done => server.close(done));
}
