import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import { createServer } from 'node:http';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { extname, resolve, sep } from 'node:path';
import assert from 'node:assert/strict';

const root = resolve('docs');
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.json': 'application/json', '.woff2': 'font/woff2' };
const chromePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || (process.platform === 'darwin'
  ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  : '/usr/bin/google-chrome');
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
const browser = await chromium.launch({ executablePath: chromePath, args: ['--no-sandbox'] });
const evidence = { pages: [], errors: [], screenshots: [], interactions: [], widths: [] };
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
    await page.evaluate(() => document.fonts.ready);
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
      await page.locator('dialog[open]').waitFor({ state: 'detached' });
      assert.equal(await page.locator('dialog[open]').count(), 0);
      assert.equal(await photos.first().evaluate(element => element === document.activeElement), true);
    }
    if (route === 'contact/') {
      assert.ok(await page.locator('a[href="mailto:proterpa@orange.fr"]').count() >= 1);
      assert.ok(await page.locator('a[href="tel:+33762058945"]').count() >= 1);
      assert.equal(await page.locator('form').count(), 0);
    }
  }
  await page.goto(base + 'galerie-photos/');
  const photos = page.locator('.gallery figure:not([hidden]) [data-photo]');
  const total = await photos.count();
  assert.equal(total, 49);
  assert.equal(await page.locator('.gallery figure.uncropped').count(), 9);
  assert.equal(await page.locator('.gallery figure.uncropped img').first().evaluate(element => getComputedStyle(element).objectFit), 'contain');
  const googleLink = page.locator('.gallery figure.uncropped [data-photo]').last();
  const googleId = await googleLink.getAttribute('data-photo');
  const googleCaption = await googleLink.getAttribute('data-caption');
  assert.ok(await page.locator('a[href="https://www.google.com/maps/contrib/114227483729375855289/photos/"]').count());
  for (const [category, expected] of [['terrassement', 12], ['amenagements', 36], ['assainissement', 4]]) {
    await page.locator(`[data-filter="${category}"]`).click();
    assert.equal(new URL(page.url()).searchParams.get('categorie'), category);
    assert.equal(await photos.count(), expected);
    assert.match(await page.locator('[data-gallery-count]').textContent(), new RegExp(`^${expected} photos`));
    assert.equal(await page.locator(`[data-filter="${category}"]`).getAttribute('aria-pressed'), 'true');
  }
  const firstFiltered = photos.first();
  const firstId = await firstFiltered.getAttribute('data-photo');
  const lastId = await photos.last().getAttribute('data-photo');
  await firstFiltered.click();
  assert.equal(new URL(page.url()).searchParams.get('photo'), firstId);
  assert.equal(await page.locator('[data-counter]').textContent(), '1 / 4');
  await page.keyboard.press('ArrowLeft');
  assert.equal(new URL(page.url()).searchParams.get('photo'), lastId);
  assert.equal(await page.locator('[data-counter]').textContent(), '4 / 4');
  await page.keyboard.press('ArrowRight');
  assert.equal(new URL(page.url()).searchParams.get('photo'), firstId);
  const sharedURL = page.url();
  await page.evaluate(() => {
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: async value => { window.testCopiedURL = value; } } });
  });
  await page.locator('[data-copy]').click();
  await page.waitForFunction(() => document.querySelector('[data-copy-status]').textContent.endsWith('copié.'));
  assert.equal(await page.evaluate(() => window.testCopiedURL), sharedURL);
  await page.evaluate(() => {
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: async () => { throw new DOMException('Denied', 'NotAllowedError'); } } });
  });
  await page.locator('[data-copy]').click();
  await page.waitForFunction(() => document.querySelector('[data-copy-status]').textContent.startsWith('Copie impossible'));
  assert.equal(await page.locator('[data-share-link]').getAttribute('href'), sharedURL);
  const modalAudit = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
  assert.deepEqual(modalAudit.violations.map(item => item.id), []);
  await page.keyboard.press('Escape');
  await page.locator('dialog[open]').waitFor({ state: 'detached' });
  assert.equal(new URL(page.url()).searchParams.get('categorie'), 'assainissement');
  assert.equal(new URL(page.url()).searchParams.has('photo'), false);
  assert.equal(await firstFiltered.evaluate(element => element === document.activeElement), true);
  await page.goForward();
  await page.locator('dialog[open]').waitFor();
  await page.goBack();
  await page.locator('dialog[open]').waitFor({ state: 'detached' });
  await page.goBack();
  assert.equal(new URL(page.url()).searchParams.get('categorie'), 'amenagements');
  assert.equal(await photos.count(), 36);
  await page.goForward();
  await page.reload();
  assert.equal(await photos.count(), 4);
  await page.goto(sharedURL);
  await page.locator('dialog[open]').waitFor();
  await page.locator('[data-close]').click();
  await page.locator('dialog[open]').waitFor({ state: 'detached' });
  assert.equal(new URL(page.url()).searchParams.get('categorie'), 'assainissement');
  await page.goto(base + 'galerie-photos/?categorie=inconnue&photo=inconnue&contexte=test');
  assert.equal(await photos.count(), total);
  assert.equal(new URL(page.url()).searchParams.has('categorie'), false);
  assert.equal(new URL(page.url()).searchParams.has('photo'), false);
  assert.equal(new URL(page.url()).searchParams.get('contexte'), 'test');
  assert.match(await page.locator('[data-gallery-status]').textContent(), /Catégorie inconnue/);
  await page.goto(base + `galerie-photos/?categorie=terrassement&photo=${firstId}`);
  assert.equal(await photos.count(), 12);
  assert.equal(await page.locator('dialog[open]').count(), 0);
  assert.match(await page.locator('[data-gallery-status]').textContent(), /pas disponible/);
  await page.goto(base + `galerie-photos/?categorie=amenagements&photo=${googleId}`);
  await page.locator('dialog[open]').waitFor();
  assert.equal(await page.locator('[data-counter]').textContent(), '36 / 36');
  assert.equal(await page.locator('.lightbox-caption').textContent(), googleCaption);
  assert.equal(await page.locator('.lightbox-image').getAttribute('width'), '1600');
  assert.equal(await page.locator('.lightbox-image').getAttribute('height'), '1600');
  const firstAmenagement = await photos.first().getAttribute('data-photo');
  await page.keyboard.press('ArrowRight');
  assert.equal(new URL(page.url()).searchParams.get('photo'), firstAmenagement);
  await page.keyboard.press('ArrowLeft');
  assert.equal(new URL(page.url()).searchParams.get('photo'), googleId);
  await page.keyboard.press('Escape');
  await page.locator('dialog[open]').waitFor({ state: 'detached' });
  assert.equal(await googleLink.evaluate(element => element === document.activeElement), true);
  assert.equal(await googleLink.evaluate(element => {
    const bounds = element.getBoundingClientRect();
    return bounds.top >= document.querySelector('.site-header').getBoundingClientRect().bottom && bounds.bottom <= innerHeight;
  }), true, 'closing a deep-linked photo must bring its keyboard focus into view');
  evidence.interactions.push('category counts and selected states', 'filter reload/back/forward', 'filtered photo wraparound and focus return', 'stable direct photo URLs', 'truthful clipboard success and permission-denied feedback', 'invalid query recovery without removing unrelated parameters', 'modal WCAG AA');
  evidence.interactions.push('nine uncropped owner-published additions and source link', 'added-photo deep link, filtered wraparound and visible focus return');
  await page.setViewportSize({ width: 390, height: 844 });
  for (const route of routes) {
    await page.goto(base + route);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, `mobile overflow on ${route}`);
    const button = page.locator('.menu-toggle');
    await button.click();
    assert.equal(await button.getAttribute('aria-expanded'), 'true');
    if (await page.locator('.quick-contact').count()) {
      assert.equal(await page.locator('.quick-contact').isVisible(), false);
    }
    await page.keyboard.press('Escape');
    assert.equal(await button.getAttribute('aria-expanded'), 'false');
    if (await page.locator('.quick-contact').count()) {
      assert.equal(await page.locator('.quick-contact').isVisible(), true);
      assert.equal(await page.locator('.quick-contact a').first().getAttribute('href'), 'tel:+33762058945');
      await page.locator('.footer-bottom a').focus();
      const clear = await page.evaluate(() => document.activeElement.getBoundingClientRect().bottom <= document.querySelector('.quick-contact').getBoundingClientRect().top);
      assert.equal(clear, true, `contact bar must not cover footer focus: ${route}`);
    }
    if (route === '') {
      await page.evaluate(async () => {
        document.querySelectorAll('img[src]').forEach(image => { image.loading = 'eager'; });
        await Promise.all([...document.images].filter(image => image.hasAttribute('src')).map(image => image.decode()));
      });
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.screenshot({ path: 'test-results/mobile-home.png', fullPage: true });
      evidence.screenshots.push('mobile-home.png');
      const audit = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
      assert.deepEqual(audit.violations.map(item => item.id), []);
    }
  }
  await page.setViewportSize({ width: 568, height: 320 });
  await page.goto(base);
  await page.locator('.menu-toggle').click();
  await page.locator('#navigation a').last().focus();
  assert.equal(await page.locator('#navigation a').last().evaluate(element => element.getBoundingClientRect().bottom <= innerHeight), true);
  assert.equal(await page.locator('.quick-contact').isVisible(), false);
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('.quick-contact').isVisible(), true);
  await page.setViewportSize({ width: 320, height: 568 });
  await page.goto(base);
  assert.equal(await page.locator('.quick-contact').evaluate(element => element.getBoundingClientRect().height <= parseFloat(getComputedStyle(document.body).paddingBottom)), true);
    for (const width of [320, 390, 768, 850, 851, 1100, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      for (const route of routes) {
        await page.goto(base + route);
        await page.evaluate(() => document.fonts.ready);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, `${width}px overflow: ${route}`);
      }
      evidence.widths.push(width);
    }
    assert.equal(await page.locator('html').evaluate(element => getComputedStyle(element).scrollBehavior), 'auto');
    await page.goto(base);
    assert.equal(await page.locator('.service-visual img').count(), 3);
    assert.equal(await page.locator('.gallery img').first().evaluate(element => getComputedStyle(element).transitionDuration), '0s');
    for (const [name, width, route] of [
      ['tablet-home', 768, ''],
      ['desktop-gallery', 1440, 'galerie-photos/?categorie=amenagements'],
      ['tablet-gallery', 768, 'galerie-photos/?categorie=terrassement'],
      ['mobile-gallery', 390, 'galerie-photos/?categorie=assainissement'],
      ['mobile-lightbox', 390, `galerie-photos/?categorie=assainissement&photo=${firstId}`],
    ]) {
      await page.setViewportSize({ width, height: 900 });
      await page.goto(base + route);
      await page.evaluate(async () => {
        await document.fonts.ready;
        document.querySelectorAll('img[src]').forEach(image => { image.loading = 'eager'; });
        await Promise.all([...document.images].map(image => image.decode()));
      });
      if (name === 'mobile-lightbox') {
        assert.equal(await page.locator('.quick-contact').isVisible(), false);
      }
      await page.screenshot({ path: `test-results/${name}.png`, fullPage: false });
      evidence.screenshots.push(`${name}.png`);
    }
    evidence.interactions.push('quick contact/menu/modal visibility and unobscured footer focus', 'reduced-motion styles', 'self-hosted fonts', 'three photographic service rows');
  await context.close();
  const noJs = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  const staticPage = await noJs.newPage();
  await staticPage.goto(base);
  assert.ok(await staticPage.locator('main a[href*="contact"]').count());
  assert.ok(await staticPage.locator('footer a[href*="galerie-photos"]').count());
  await staticPage.goto(base + 'galerie-photos/?categorie=assainissement');
  assert.equal(await staticPage.locator('.gallery [data-photo]').count(), total);
  assert.equal(await staticPage.locator('.gallery figure.uncropped [data-photo]').count(), 9);
  assert.equal(await staticPage.locator('figure[hidden]').count(), 0);
  assert.equal(await staticPage.locator('[data-gallery-filters]').isVisible(), false);
  assert.ok((await staticPage.locator('.gallery [data-photo]').first().getAttribute('href')).endsWith('.webp'));
  await noJs.close();
  assert.deepEqual(evidence.errors, []);
  await writeFile('test-results/evidence.json', JSON.stringify(evidence, null, 2));
  console.log(JSON.stringify(evidence, null, 2));
} finally {
  await browser.close();
  await new Promise(done => server.close(done));
}
