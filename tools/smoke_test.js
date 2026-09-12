/* Runtime smoke test for the theme's JavaScript.
 *
 * Loads the static preview page (tools/build_preview.py) in jsdom, stubs the
 * Shopify AJAX cart API with a realistic payload, then checks that
 * assets/theme.js and the section {% javascript %} blocks:
 *
 *   - boot without throwing
 *   - paint the cart drawer from /cart.js (count, line items, subtotal,
 *     savings, free-shipping progress)
 *   - open drawers, run sliders, wire quick-add and quantity steppers
 *
 * Anything logged here as a failure would also break in a real browser.
 *
 *   npm install jsdom                       # once
 *   python3 tools/build_preview.py          # build the page
 *   python3 -m http.server 4000 --directory /home/user/preview &
 *   JSDOM_PATH=./node_modules/jsdom node tools/smoke_test.js http://127.0.0.1:4000/
 */
const path = require('path');
const JSDOM_PATH = process.env.JSDOM_PATH || '/tmp/node_modules/jsdom';
const { JSDOM, VirtualConsole } = require(path.resolve(JSDOM_PATH));

const URL = process.argv[2] || 'http://127.0.0.1:4000/';

/* ---- a cart shaped exactly like /cart.js -------------------------------- */
const CART = {
  token: 'c1a2b3', note: '', attributes: {},
  item_count: 3, items_subtotal_price: 443000,
  original_total_price: 505000, total_price: 443000, total_discount: 62000,
  total_weight: 1800, requires_shipping: true, currency: 'INR',
  cart_level_discount_applications: [],
  items: [
    {
      id: 41111, key: '41111:aaa111', quantity: 1,
      title: 'Bagru table runner - Terracotta / Long',
      product_title: 'Bagru table runner', variant_title: 'Terracotta / Long',
      vendor: 'Bagru workshop', url: '#',
      image: 'https://cdn.shopify.com/s/files/1/runner.png',
      price: 248000, original_price: 310000, final_price: 248000,
      line_price: 310000, original_line_price: 310000, final_line_price: 248000,
      options_with_values: [{ name: 'Colour', value: 'Terracotta' }, { name: 'Size', value: 'Long' }],
      properties: { 'Gift note': 'Happy Diwali', _hidden: 'x' },
      discounts: [{ title: 'Festival 20%', amount: 62000 }],
      selling_plan_allocation: null,
    },
    {
      id: 42222, key: '42222:bbb222', quantity: 2,
      title: 'Indigo napkin set of four', product_title: 'Indigo napkin set of four',
      variant_title: null, vendor: 'Sanganer', url: '#', image: '',
      price: 97500, original_price: 97500, final_price: 97500,
      line_price: 195000, original_line_price: 195000, final_line_price: 195000,
      options_with_values: [], properties: {}, discounts: [], selling_plan_allocation: null,
    },
  ],
};

const results = [];
function check(name, pass, detail) {
  results.push({ name, pass: !!pass, detail: detail === undefined ? '' : String(detail) });
}

(async () => {
  const errors = [];
  const vc = new VirtualConsole();
  vc.on('jsdomError', (e) => {
    const msg = String(e.stack || e.message);
    if (/fonts\.googleapis|Could not load link/.test(msg)) return; // no external fonts in the sandbox
    errors.push('jsdomError: ' + msg.split('\n').slice(0, 3).join(' | '));
  });
  vc.on('error', (...a) => errors.push('console.error: ' + a.join(' ')));

  const fetchLog = [];
  const dom = await JSDOM.fromURL(URL, {
    runScripts: 'dangerously',
    resources: 'usable',
    pretendToBeVisual: true,
    virtualConsole: vc,
    beforeParse(window) {
      window.matchMedia = window.matchMedia || function () {
        return { matches: false, addListener() {}, removeListener() {}, addEventListener() {}, removeEventListener() {} };
      };
      window.scrollBy = window.scrollBy || function () {};
      window.scrollTo = window.scrollTo || function () {};
      window.fetch = function (url, opts) {
        fetchLog.push(String(url) + (opts && opts.method ? ' ' + opts.method : ''));
        const body = /sections=/.test(String(url))
          ? { preview: '<div class="shopify-section">refreshed</div>' }
          : CART;
        return Promise.resolve({
          ok: true, status: 200,
          json: () => Promise.resolve(body),
          text: () => Promise.resolve(JSON.stringify(body)),
        });
      };
      window.addEventListener('error', (e) => errors.push('window.onerror: ' + ((e.error && e.error.stack) || e.message)));
      window.addEventListener('unhandledrejection', (e) => errors.push('unhandledrejection: ' + e.reason));
    },
  });

  const { window } = dom;
  const doc = window.document;
  const $ = (sel) => doc.querySelector(sel);
  const $$ = (sel) => Array.from(doc.querySelectorAll(sel));
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const click = (el) => el && el.dispatchEvent(new window.MouseEvent('click', { bubbles: true, cancelable: true }));

  await wait(1200);

  /* ---- boot ---------------------------------------------------------- */
  check('window.KK config object exists', typeof window.KK === 'object');
  check('no runtime errors on boot', errors.length === 0, errors.slice(0, 4).join('\n'));
  check('cart was fetched on load', fetchLog.some((u) => /cart\.js/.test(u)), fetchLog.join(', '));

  /* ---- cart render --------------------------------------------------- */
  const count = $('[data-cart-count]');
  check('cart count painted', count && count.textContent.trim() === '3', count && count.textContent);
  const items = $$('[data-cart-items] .cart-item');
  check('two line items rendered', items.length === 2, items.length);
  check('line item shows variant + property', /Terracotta/.test(items[0] && items[0].innerHTML) && /Gift note/.test(items[0] && items[0].innerHTML));
  check('hidden property (leading _) suppressed', !/_hidden/.test(items[0] ? items[0].innerHTML : ''));
  check('line item discount shown', /Festival 20%/.test(items[0] ? items[0].innerHTML : ''));
  check('compare price shown when line price differs', /price__compare/.test(items[0] ? items[0].innerHTML : ''));
  check('no-image fallback used', /cart-item__no-image/.test(items[1] ? items[1].innerHTML : ''));
  const subtotal = $('[data-cart-subtotal]');
  check('subtotal formatted as money', subtotal && /4,430/.test(subtotal.textContent), subtotal && subtotal.textContent);
  const savings = $('[data-cart-total-savings]');
  check('savings total computed', savings && /620/.test(savings.textContent), savings && savings.textContent);
  check('savings row unhidden', savings && savings.parentElement.hidden === false);
  const fill = $('[data-shipping-fill]');
  check('free-shipping bar filled to 89%', fill && fill.style.width === '89%', fill && fill.style.width);
  const shipText = $('[data-shipping-text]');
  check('free-shipping message shows remaining', shipText && /570/.test(shipText.textContent), shipText && shipText.textContent);
  const checkout = $('[data-cart-checkout]');
  check('checkout enabled with items', checkout && checkout.disabled === false);

  /* ---- quantity stepper ---------------------------------------------- */
  fetchLog.length = 0;
  click($('[data-cart-qty][data-qty="1"]'));
  await wait(400);
  check('quantity stepper posts to /cart/change.js', fetchLog.some((u) => /change\.js/.test(u)), fetchLog.join(', '));

  /* ---- drawers -------------------------------------------------------- */
  const cartDrawer = $('#CartDrawer');
  click($('[data-panel-open="CartDrawer"]'));
  await wait(200);
  check('cart drawer opens', cartDrawer && (cartDrawer.classList.contains('is-open') || cartDrawer.getAttribute('aria-hidden') === 'false'),
    cartDrawer && cartDrawer.className + ' / aria-hidden=' + cartDrawer.getAttribute('aria-hidden'));
  click($('[data-panel-close]'));
  await wait(200);
  check('drawer close button works', cartDrawer && !cartDrawer.classList.contains('is-open'));

  const menuDrawer = $('#MenuDrawer');
  click($('[data-panel-open="MenuDrawer"]'));
  await wait(200);
  check('mobile menu drawer opens', menuDrawer && (menuDrawer.classList.contains('is-open') || menuDrawer.getAttribute('aria-hidden') === 'false'),
    menuDrawer && menuDrawer.className);

  /* ---- slider ---------------------------------------------------------- */
  const dots = $('[data-slider-dots]');
  check('slider built its dots', dots && dots.children.length > 0, dots && dots.children.length);
  const slides = $$('[data-slider] [data-slide]');
  check('slider has slides', slides.length === 6, slides.length);

  /* ---- accordion ------------------------------------------------------- */
  const faq = $('[data-accordion]');
  check('faq accordion present', !!faq);

  /* ---- quick add -------------------------------------------------------- */
  fetchLog.length = 0;
  click($('[data-quick-add]'));
  await wait(400);
  check('quick add posts to /cart/add.js', fetchLog.some((u) => /add\.js/.test(u)), fetchLog.join(', '));

  /* ---- final error sweep ------------------------------------------------ */
  await wait(300);
  check('no runtime errors after interaction', errors.length === 0, errors.slice(0, 4).join('\n'));

  const failed = results.filter((r) => !r.pass);
  results.forEach((r) => console.log((r.pass ? '  ✓ ' : '  ✗ ') + r.name + (r.pass || !r.detail ? '' : '\n      ' + r.detail)));
  console.log('\n' + (results.length - failed.length) + '/' + results.length + ' checks passed');
  if (failed.length) console.log('FAILED: ' + failed.map((f) => f.name).join(' | '));

  window.close();
  process.exit(failed.length ? 1 : 0);
})().catch((e) => { console.error('harness failure:', e); process.exit(2); });
