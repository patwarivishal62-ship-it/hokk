/*!
 * House of Kala Katha — Kala Katha theme
 * theme.js : single dependency-free bundle for every interactive feature.
 * Everything is defensive: a missing element never throws.
 */
(function () {
  'use strict';

  var KK = (window.KalaKatha = window.KalaKatha || {});
  var CFG = window.KK || {};

  /* ------------------------------------------------------------- helpers */
  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function on(el, ev, fn, opts) { if (el) el.addEventListener(ev, fn, opts || false); }
  function delegate(root, ev, selector, fn) {
    on(root, ev, function (e) {
      var t = e.target.closest ? e.target.closest(selector) : null;
      if (t && root.contains(t)) fn(e, t);
    });
  }
  function attr(el, name, fallback) {
    if (!el) return fallback;
    var v = el.getAttribute(name);
    return v === null || v === '' ? fallback : v;
  }
  function debounce(fn, wait) {
    var t;
    return function () {
      var args = arguments, self = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(self, args); }, wait || 200);
    };
  }
  function throttle(fn, wait) {
    var last = 0, timer = null;
    return function () {
      var now = Date.now(), args = arguments, self = this;
      var remaining = (wait || 100) - (now - last);
      if (remaining <= 0) { last = now; fn.apply(self, args); }
      else if (!timer) {
        timer = setTimeout(function () { last = Date.now(); timer = null; fn.apply(self, args); }, remaining);
      }
    };
  }
  function escapeHtml(str) {
    return String(str == null ? '' : str).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function trapFocus(container) {
    var selectors = 'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])';
    function handler(e) {
      if (e.key !== 'Tab') return;
      var f = $$(selectors, container).filter(function (el) { return el.offsetParent !== null; });
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
    container.addEventListener('keydown', handler);
    return function () { container.removeEventListener('keydown', handler); };
  }

  /* ---------------------------------------------------------- money util */
  function formatWithDelimiters(cents, precision, thousands, decimal) {
    precision = precision == null ? 2 : precision;
    thousands = thousands == null ? ',' : thousands;
    decimal = decimal == null ? '.' : decimal;
    if (isNaN(cents) || cents == null) cents = 0;
    var value = (cents / 100).toFixed(precision);
    var parts = value.split('.');
    var dollars = parts[0].replace(/(\d)(?=(\d\d\d)+(?!\d))/g, '$1' + thousands);
    return dollars + (parts[1] ? decimal + parts[1] : '');
  }

  function formatMoney(cents, format) {
    if (typeof cents === 'string') cents = parseInt(cents.replace(/\D/g, ''), 10) || 0;
    var f = format || CFG.moneyFormat || '${{amount}}';
    var m = f.match(/\{\{\s*(\w+)\s*\}\}/);
    var token = m ? m[1] : 'amount';
    var value;
    switch (token) {
      case 'amount_no_decimals': value = formatWithDelimiters(cents, 0); break;
      case 'amount_with_comma_separator': value = formatWithDelimiters(cents, 2, '.', ','); break;
      case 'amount_no_decimals_with_comma_separator': value = formatWithDelimiters(cents, 0, '.', ','); break;
      case 'amount_no_decimals_with_space_separator': value = formatWithDelimiters(cents, 0, ' ', ''); break;
      case 'amount_with_space_separator': value = formatWithDelimiters(cents, 2, ' ', ','); break;
      default: value = formatWithDelimiters(cents, 2);
    }
    return f.replace(/\{\{\s*\w+\s*\}\}/, value);
  }

  KK.formatMoney = formatMoney;
  window.Shopify = window.Shopify || {};
  if (!window.Shopify.formatMoney) window.Shopify.formatMoney = formatMoney;

  /* ------------------------------------------------------- reveal on load */
  var revealObserver = null;
  function initReveal(root) {
    var style = document.body.getAttribute('data-animations') || 'none';
    var items = $$('[data-animate]', root);
    if (!items.length) return;
    if (style === 'none' || !('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('is-visible'); });
      return;
    }
    if (!revealObserver) {
      revealObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            revealObserver.unobserve(entry.target);
          }
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    }
    items.forEach(function (el) {
      if (document.body.getAttribute('data-stagger') === 'true' && !el.style.getPropertyValue('--anim-delay')) {
        var group = el.parentNode ? $$('[data-animate]', el.parentNode) : [];
        var i = group.indexOf(el);
        if (i > -1) el.style.setProperty('--anim-delay', Math.min(i, 8) * 70 + 'ms');
      }
      revealObserver.observe(el);
    });
  }
  KK.initReveal = initReveal;

  /* ------------------------------------------------------------- drawers */
  var openStack = [];

  function lockBody(state) {
    if (state) document.body.classList.add('is-locked');
    else document.body.classList.remove('is-locked');
  }

  function openPanel(el) {
    if (!el || el.classList.contains('is-open')) return;
    var overlay = el.hasAttribute('data-uses-overlay') === false ? null : (el.querySelector('.overlay') || $('[data-shared-overlay]'));
    el.classList.add('is-open');
    el.setAttribute('aria-hidden', 'false');
    if (overlay) { overlay.classList.add('is-open'); overlay.setAttribute('aria-hidden', 'false'); }
    lockBody(true);
    var release = trapFocus(el);
    var entry = { el: el, overlay: overlay, release: release, prev: document.activeElement };
    openStack.push(entry);
    setTimeout(function () {
      var f = $('[data-autofocus]', el) || $('a[href],button,input', el);
      if (f) f.focus({ preventScroll: true });
    }, 120);
    document.dispatchEvent(new CustomEvent('kk:panel:open', { detail: { el: el } }));
  }

  function closePanel(el) {
    if (!el) return;
    var idx = -1;
    openStack.forEach(function (e, i) { if (e.el === el) idx = i; });
    if (idx === -1 && !el.classList.contains('is-open')) return;
    var entry = openStack[idx];
    el.classList.remove('is-open');
    el.setAttribute('aria-hidden', 'true');
    if (entry && entry.overlay) {
      entry.overlay.classList.remove('is-open');
      entry.overlay.setAttribute('aria-hidden', 'true');
    }
    if (entry) { entry.release(); openStack.splice(idx, 1); }
    if (!openStack.length) lockBody(false);
    if (entry && entry.prev && document.contains(entry.prev)) entry.prev.focus({ preventScroll: true });
    document.dispatchEvent(new CustomEvent('kk:panel:close', { detail: { el: el } }));
  }

  function closeTop() { if (openStack.length) closePanel(openStack[openStack.length - 1].el); }

  KK.openPanel = openPanel;
  KK.closePanel = closePanel;

  function initPanels(root) {
    delegate(root || document, 'click', '[data-panel-open]', function (e, el) {
      var target = document.getElementById(el.getAttribute('data-panel-open'));
      if (target) { e.preventDefault(); openPanel(target); }
    });
    delegate(root || document, 'click', '[data-panel-close]', function (e, el) {
      var host = el.closest('.drawer, .modal');
      if (host) { e.preventDefault(); closePanel(host); }
    });
    delegate(root || document, 'click', '[data-overlay-close]', function (e) {
      e.preventDefault(); closeTop();
    });
  }

  on(document, 'keydown', function (e) {
    if (e.key === 'Escape' || e.key === 'Esc') closeTop();
  });

  /* --------------------------------------------------------------- modal */
  var modalEl = null;
  KK.modal = {
    open: function (content, opts) {
      modalEl = modalEl || $('#KkModal');
      if (!modalEl) return;
      var slot = $('[data-modal-content]', modalEl);
      if (!slot) return;
      slot.innerHTML = '';
      if (typeof content === 'string') slot.innerHTML = content;
      else if (content) slot.appendChild(content);
      modalEl.classList.remove('modal--bare');
      if (opts && opts.bare) modalEl.classList.add('modal--bare');
      if (opts && opts.wide) modalEl.querySelector('.modal__panel').style.maxWidth = '96vw';
      openPanel(modalEl);
      document.dispatchEvent(new CustomEvent('kk:modal:open'));
    },
    close: function () { if (modalEl) closePanel(modalEl); }
  };

  /* -------------------------------------------------------------- header */
  function initHeader() {
    var header = $('[data-header]');
    if (!header) return;
    var behavior = document.body.getAttribute('data-header-behavior') || 'static';
    var wrapper = header.closest('.shopify-section-group-header-group') ||
                  header.closest('.shopify-section') || header;
    var lastY = window.scrollY;

    function measure() {
      var h = wrapper.offsetHeight || header.offsetHeight || 0;
      document.body.style.setProperty('--header-height', h + 'px');
    }

    if (behavior === 'sticky' || behavior === 'hide') {
      document.body.classList.add('header-is-sticky');
      if (behavior === 'hide') document.body.classList.add('header-is-hide');
      measure();
      on(window, 'resize', debounce(measure, 200));
      on(window, 'load', measure);
    }

    function update() {
      var y = window.scrollY;
      header.classList.toggle('is-stuck', y > 10);
      if (behavior === 'hide') {
        var down = y > lastY && y > (wrapper.offsetHeight || 80) + 24;
        wrapper.classList.toggle('is-hidden', down);
        if (y <= 4) wrapper.classList.remove('is-hidden');
      }
      lastY = y;
    }

    on(window, 'scroll', throttle(update, 60), { passive: true });
    update();

    /* desktop dropdowns: click support for touch devices */
    delegate(header, 'click', '.nav__item--children > .nav__link', function (e, el) {
      if (window.matchMedia('(hover: hover) and (min-width: 990px)').matches) return;
      var item = el.parentNode;
      var open = item.classList.contains('is-open');
      $$('.nav__item.is-open', header).forEach(function (i) { i.classList.remove('is-open'); });
      if (!open) { e.preventDefault(); item.classList.add('is-open'); }
    });

    delegate(document, 'click', function (e) {
      if (!header.contains(e.target)) {
        $$('.nav__item.is-open', header).forEach(function (i) { i.classList.remove('is-open'); });
      }
    });

    /* mobile menu accordions */
    delegate(header, 'click', '[data-menu-toggle]', function (e, el) {
      e.preventDefault();
      var panel = document.getElementById(el.getAttribute('aria-controls'));
      var open = el.getAttribute('aria-expanded') === 'true';
      el.setAttribute('aria-expanded', String(!open));
      if (panel) {
        panel.style.maxHeight = open ? '0px' : panel.scrollHeight + 'px';
        panel.classList.toggle('is-open', !open);
      }
    });

    /* announcement bar rotation */
    var slides = $$('.announcement__slide');
    if (slides.length > 1) {
      var i = 0;
      slides[0].classList.add('is-active');
      setInterval(function () {
        slides[i].classList.remove('is-active');
        i = (i + 1) % slides.length;
        slides[i].classList.add('is-active');
      }, 5200);
    }

    /* back to top */
    var btt = $('[data-back-to-top]');
    if (btt) {
      on(btt, 'click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
      on(window, 'scroll', throttle(function () {
        btt.classList.toggle('is-visible', window.scrollY > 700);
      }, 120), { passive: true });
    }
  }

  /* ------------------------------------------------------------ cart api */
  function okJson(response) {
    if (!response.ok) throw new Error('Cart request failed with HTTP ' + response.status);
    return response.json();
  }

  /* Every cart call is fired from a click handler, so a rejection has nowhere to
     go: report it on the page and resolve to null instead. */
  function cartFailed(err) {
    Cart.error((err && (err.description || err.message)) || (CFG.strings && CFG.strings.cartError) || 'Your cart could not be updated.');
    return null;
  }

  var Cart = {
    busy: false,
    get: function () {
      return fetch(CFG.routes ? CFG.routes.cart + '.js' : '/cart.js', { headers: { Accept: 'application/json' } })
        .then(function (r) {
          if (!r.ok) throw new Error('Cart request failed with HTTP ' + r.status);
          return r.json();
        })
        .catch(function (err) {
          Cart.error((err && err.message) || (CFG.strings && CFG.strings.cartError) || 'Your cart could not be loaded.');
          return null;
        });
    },
    add: function (items, cb) {
      var body = { items: Array.isArray(items) ? items : [items] };
      return fetch((CFG.routes ? CFG.routes.cart + '/add' : '/cart/add') + '.js', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(body)
      }).then(function (r) {
        if (!r.ok) return r.json().then(function (err) { throw err; });
        return r.json();
      }).then(function (res) { Cart.refresh(); if (cb) cb(res); return res; })
        .catch(function (err) {
          var msg = (err && err.description) || (CFG.strings && CFG.strings.cartError) || 'This item could not be added to your cart.';
          Cart.error(msg);
          throw err;
        });
    },
    change: function (changes) {
      return fetch((CFG.routes ? CFG.routes.cart + '/change' : '/cart/change') + '.js', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ changes: changes })
      }).then(okJson).then(function (cart) { Cart.refresh(cart); return cart; }).catch(cartFailed);
    },
    update: function (updates) {
      return fetch((CFG.routes ? CFG.routes.cart + '/update' : '/cart/update') + '.js', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ updates: updates })
      }).then(okJson).then(function (cart) { Cart.refresh(cart); return cart; }).catch(cartFailed);
    },
    clear: function () {
      return fetch((CFG.routes ? CFG.routes.cart + '/clear' : '/cart/clear') + '.js', {
        method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: '{}'
      }).then(okJson).then(function (cart) { Cart.refresh(cart); return cart; }).catch(cartFailed);
    },
    error: function (msg) {
      var box = $('[data-cart-errors]');
      if (box) { box.textContent = msg; box.hidden = false; }
      document.dispatchEvent(new CustomEvent('kk:cart:error', { detail: { message: msg } }));
    },
    refresh: function (cart) {
      var done = function (data) {
        if (!data) return;
        Cart.render(data);
        document.dispatchEvent(new CustomEvent('kk:cart:updated', { detail: { cart: data } }));
      };
      if (cart && typeof cart.item_count !== 'undefined') { done(cart); return Promise.resolve(cart); }
      return Cart.get().then(done);
    },

    /* -------- paint every cart surface from a single source of truth ---- */
    render: function (cart) {
      if (!cart) return;
      $$('[data-cart-count]').forEach(function (el) {
        el.textContent = cart.item_count;
        el.hidden = cart.item_count === 0;
        var bubble = el.closest('[data-cart-bubble]');
        if (bubble) bubble.hidden = cart.item_count === 0;
      });

      var items = Array.isArray(cart.items) ? cart.items : [];

      $$('[data-cart-items]').forEach(function (list) {
        if (!items.length) {
          var empty = $('[data-cart-empty]');
          list.innerHTML = empty ? empty.innerHTML : '';
        } else {
          list.innerHTML = items.map(itemRow).join('');
        }
      });

      $$('[data-cart-count-text]').forEach(function (el) { el.textContent = '(' + cart.item_count + ')'; });

      $$('[data-cart-subtotal]').forEach(function (el) { el.innerHTML = formatMoney(cart.total_price, CFG.moneyFormat); });
      $$('[data-cart-total-savings]').forEach(function (el) {
        var savings = items.reduce(function (sum, it) {
          return sum + (it.original_line_price - it.final_line_price);
        }, 0);
        el.hidden = savings <= 0;
        el.innerHTML = formatMoney(savings, CFG.moneyFormat);
      });

      /* free shipping progress */
      var threshold = parseFloat(CFG.freeShippingThreshold || 0);
      if (threshold > 0) {
        var remaining = Math.max(0, threshold * 100 - cart.total_price);
        var pct = Math.min(100, Math.round((cart.total_price / (threshold * 100)) * 100));
        $$('[data-shipping-bar]').forEach(function (bar) {
          var fill = $('[data-shipping-fill]', bar);
          var label = $('[data-shipping-text]', bar);
          if (fill) fill.style.width = pct + '%';
          if (label) {
            label.innerHTML = remaining <= 0
              ? (CFG.strings && CFG.strings.freeShippingMet)
              : (CFG.strings && CFG.strings.freeShippingRemaining ? CFG.strings.freeShippingRemaining.replace('[amount]', formatMoney(remaining)) : '');
          }
        });
      }

      /* checkout buttons availability */
      $$('[data-cart-checkout]').forEach(function (el) {
        el.disabled = cart.item_count === 0;
        el.classList.toggle('is-loading', false);
      });

      /* cart page: swap the live section */
      var pageSection = $('[data-cart-section]');
      if (pageSection && document.body.classList.contains('template-cart')) {
        var id = pageSection.getAttribute('data-cart-section');
        var url = CFG.routes ? CFG.routes.cart : '/cart';
        fetch(url + '?sections=' + encodeURIComponent(id), { headers: { Accept: 'text/html' } })
          .then(function (r) { return r.json(); })
          .then(function (res) {
            var html = res && res[id];
            if (!html) return;
            var tmp = document.createElement('div');
            tmp.innerHTML = html;
            var fresh = tmp.querySelector('#shopify-section-' + id) || tmp.firstElementChild;
            if (fresh) {
              pageSection.innerHTML = fresh.innerHTML;
              $$('script', pageSection).forEach(function (s) {
                var n = document.createElement('script');
                if (s.src) n.src = s.src; else n.textContent = s.textContent;
                s.parentNode.replaceChild(n, s);
              });
              KK.init(pageSection);
            }
          })
          .catch(function () { /* keep the drawer-only render */ });
      }
    }
  };

  function itemRow(item) {
    var img = item.image
      ? '<img src="' + item.image.replace(/(\.[a-z]{3,4})$/i, '_160x$1') + '" alt="' + escapeHtml(item.title) + '" width="80" height="100" loading="lazy">'
      : '<span class="cart-item__no-image"></span>';
    var opts = item.options_with_values && item.options_with_values.length
      ? '<div class="cart-item__variant">' + item.options_with_values.map(function (o) {
          return '<span>' + escapeHtml(o.name) + ': ' + escapeHtml(o.value) + '</span>';
        }).join('') + '</div>'
      : '';
    var props = item.properties && Object.keys(item.properties).length
      ? '<ul class="cart-item__properties">' + Object.keys(item.properties).map(function (k) {
          if (k.charAt(0) === '_' || !item.properties[k]) return '';
          return '<li>' + escapeHtml(k) + ': ' + escapeHtml(String(item.properties[k])) + '</li>';
        }).join('') + '</ul>'
      : '';
    var selling = item.selling_plan_allocation
      ? '<div class="cart-item__selling">' + escapeHtml(item.selling_plan_allocation.selling_plan_name) + '</div>' : '';
    var discounts = item.discounts && item.discounts.length
      ? '<div class="cart-item__discounts">' + item.discounts.map(function (d) {
          return '<span>' + escapeHtml(d.title) + ' (-' + formatMoney(d.amount) + ')</span>';
        }).join('') + '</div>' : '';
    var compare = item.original_line_price !== item.final_line_price
      ? '<s class="price__compare">' + formatMoney(item.original_line_price) + '</s>' : '';

    return '' +
      '<div class="cart-item" data-cart-item data-key="' + escapeHtml(item.key) + '">' +
        '<a class="cart-item__media" href="' + item.url + '" tabindex="-1" aria-hidden="true">' + img + '</a>' +
        '<div class="cart-item__details">' +
          '<div class="cart-item__head">' +
            '<a class="cart-item__title" href="' + item.url + '">' + escapeHtml(item.product_title || item.title) + '</a>' +
            '<button type="button" class="cart-item__remove" data-cart-remove="' + escapeHtml(item.key) + '" aria-label="' + escapeHtml((CFG.strings && CFG.strings.remove) || 'Remove') + '">' +
              '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M3.5 6.2h17M8.5 6.2V4h7v2.2M6.2 6.2 7.3 21h9.4l1.1-14.8"/></svg>' +
            '</button>' +
          '</div>' +
          (item.vendor ? '<div class="cart-item__vendor">' + escapeHtml(item.vendor) + '</div>' : '') +
          opts + selling + props + discounts +
          '<div class="cart-item__foot">' +
            '<div class="quantity quantity--small">' +
              '<button type="button" class="quantity__btn" data-cart-qty="' + escapeHtml(item.key) + '" data-qty="-1" aria-label="' + escapeHtml((CFG.strings && CFG.strings.decrease) || 'Decrease quantity') + '">&minus;</button>' +
              '<input class="quantity__input" type="number" inputmode="numeric" min="0" value="' + item.quantity + '" data-cart-input="' + escapeHtml(item.key) + '" aria-label="' + escapeHtml((CFG.strings && CFG.strings.quantity) || 'Quantity') + '">' +
              '<button type="button" class="quantity__btn" data-cart-qty="' + escapeHtml(item.key) + '" data-qty="1" aria-label="' + escapeHtml((CFG.strings && CFG.strings.increase) || 'Increase quantity') + '">+</button>' +
            '</div>' +
            '<div class="cart-item__price price">' + compare + '<span class="price__current">' + formatMoney(item.final_line_price) + '</span></div>' +
          '</div>' +
        '</div>' +
      '</div>';
  }

  function initCart(root) {
    var scope = root || document;

    /* add to cart */
    delegate(scope, 'submit', '[data-product-form]', function (e, form) {
      var btn = $('[type="submit"]', form);
      if (form.hasAttribute('data-no-ajax')) return; /* e.g. dynamic checkout */
      e.preventDefault();
      var fd = new FormData(form);
      var items = [];
      var ids = fd.getAll('id');
      var qtys = fd.getAll('quantity');
      ids.forEach(function (id, i) {
        var q = parseInt(qtys[i] || 1, 10);
        if (q > 0) items.push({ id: parseInt(id, 10), quantity: q });
      });
      if (!items.length) {
        var props = {};
        fd.forEach(function (v, k) { if (k.indexOf('properties[') === 0) props[k.replace('properties[', '').replace(']', '')] = v; });
        items = [{ id: parseInt(fd.get('id'), 10), quantity: parseInt(fd.get('quantity') || 1, 10), properties: props, selling_plan: fd.get('selling_plan') || undefined }];
      }
      if (btn) { btn.classList.add('is-loading'); btn.setAttribute('aria-busy', 'true'); }
      var errBox = $('[data-form-errors]', form);
      if (errBox) { errBox.hidden = true; errBox.textContent = ''; }

      Cart.add(items).then(function () {
        if (btn) { btn.classList.remove('is-loading'); btn.removeAttribute('aria-busy'); }
        var openAfter = attr(form, 'data-open-cart', CFG.cartType === 'page' ? 'false' : 'true');
        if (openAfter !== 'false') {
          var drawer = $('#CartDrawer');
          if (drawer) openPanel(drawer);
        }
      }).catch(function (err) {
        if (btn) { btn.classList.remove('is-loading'); btn.removeAttribute('aria-busy'); }
        var msg = (err && (err.description || err.message)) || (CFG.strings && CFG.strings.cartError) || 'Something went wrong.';
        if (errBox) { errBox.textContent = msg; errBox.hidden = false; }
        form.classList.add('shake');
        setTimeout(function () { form.classList.remove('shake'); }, 600);
      });
    });

    /* quick add from cards */
    delegate(scope, 'click', '[data-quick-add]', function (e, el) {
      e.preventDefault();
      var id = parseInt(el.getAttribute('data-quick-add'), 10);
      if (!id) return;
      el.classList.add('is-loading');
      Cart.add({ id: id, quantity: 1 }).then(function () {
        el.classList.remove('is-loading');
        var drawer = $('#CartDrawer');
        if (drawer && CFG.cartType !== 'page') openPanel(drawer);
      }).catch(function () { el.classList.remove('is-loading'); });
    });

    /* quantity steppers */
    delegate(scope, 'click', '[data-cart-qty]', function (e, el) {
      e.preventDefault();
      var key = el.getAttribute('data-cart-qty');
      var delta = parseInt(attr(el, 'data-qty', '1'), 10);
      var safe = window.CSS && CSS.escape ? CSS.escape(key) : key.replace(/"/g, '\\"');
      var input = $('[data-cart-input="' + safe + '"]', document);
      var current = input ? parseInt(input.value, 10) : 0;
      var next = Math.max(0, current + delta);
      Cart.change({ [key]: next });
    });

    delegate(scope, 'change', '[data-cart-input]', function (e, el) {
      var key = el.getAttribute('data-cart-input');
      var next = Math.max(0, parseInt(el.value, 10) || 0);
      Cart.change({ [key]: next });
    });

    delegate(scope, 'click', '[data-cart-remove]', function (e, el) {
      e.preventDefault();
      var key = el.getAttribute('data-cart-remove');
      Cart.change({ [key]: 0 });
    });

    /* checkout buttons: show a loading state while Shopify processes the post */
    delegate(scope, 'click', '[data-cart-checkout]', function (e, el) {
      if (el.disabled) { e.preventDefault(); return; }
      var terms = $('[data-cart-terms]');
      if (terms && !terms.checked) {
        e.preventDefault();
        var label = terms.closest('label') || terms;
        label.classList.add('shake');
        setTimeout(function () { label.classList.remove('shake'); }, 600);
        terms.focus();
        return;
      }
      el.classList.add('is-loading');
    });

    /* notes */
    delegate(scope, 'change', '[data-cart-note]', function (e, el) {
      fetch((CFG.routes ? CFG.routes.cart + '/update' : '/cart/update') + '.js', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ note: el.value })
      }).catch(function () {});
    });

  }

  KK.cart = Cart;

  /* --------------------------------------------------- predictive search */
  function initSearch(root) {
    var scope = root || document;
    var forms = $$('[data-predictive-search]', scope);
    forms.forEach(function (form) {
      var input = $('input[type="search"], input[name="q"]', form);
      var results = $('[data-search-results]', form);
      if (!input || !results) return;
      var controller = null;
      var limit = parseInt(attr(form, 'data-predictive-limit', '5'), 10);

      function render(data) {
        var html = '';
        var r = data.resources || {};
        var products = r.results ? (r.results.products || []) : [];
        var collections = r.results ? (r.results.collections || []) : [];
        var pages = r.results ? ((r.results.pages || []).concat(r.results.articles || [])) : [];
        var queries = r.results ? (r.results.queries || []) : [];

        if (queries.length) {
          html += '<div class="predictive__group"><p class="predictive__heading">' + escapeHtml(CFG.strings.suggestions || 'Suggestions') + '</p><ul class="predictive__list">';
          queries.slice(0, 4).forEach(function (q) {
            html += '<li><a class="predictive__link" href="' + q.url + '">' + escapeHtml(q.styled_text || q.text) + '</a></li>';
          });
          html += '</ul></div>';
        }
        if (products.length) {
          html += '<div class="predictive__group"><p class="predictive__heading">' + escapeHtml(CFG.strings.products || 'Products') + '</p><ul class="predictive__list predictive__list--products">';
          products.slice(0, limit).forEach(function (p) {
            var img = p.featured_image && p.featured_image.url
              ? '<img src="' + p.featured_image.url.replace(/(\.[a-z]{3,4})$/i, '_80x$1') + '" alt="" width="40" height="50" loading="lazy">'
              : '<span class="predictive__thumb"></span>';
            var price = p.price ? '<span class="predictive__price">' + formatMoney(p.price_min || p.price) + '</span>' : '';
            html += '<li><a class="predictive__link predictive__link--product" href="' + p.url + '">' + img + '<span class="predictive__text"><span class="predictive__title">' + escapeHtml(p.title) + '</span>' + price + '</span></a></li>';
          });
          html += '</ul></div>';
        }
        if (collections.length) {
          html += '<div class="predictive__group"><p class="predictive__heading">' + escapeHtml(CFG.strings.collections || 'Collections') + '</p><ul class="predictive__list">';
          collections.slice(0, 3).forEach(function (c) {
            html += '<li><a class="predictive__link" href="' + c.url + '">' + escapeHtml(c.title) + '</a></li>';
          });
          html += '</ul></div>';
        }
        if (pages.length) {
          html += '<div class="predictive__group"><p class="predictive__heading">' + escapeHtml(CFG.strings.pages || 'Pages & journal') + '</p><ul class="predictive__list">';
          pages.slice(0, 3).forEach(function (pg) {
            html += '<li><a class="predictive__link" href="' + pg.url + '">' + escapeHtml(pg.title) + '</a></li>';
          });
          html += '</ul></div>';
        }
        if (!html) {
          html = '<div class="predictive__group"><p class="predictive__empty">' +
            (CFG.strings.noResults || 'No results for') + ' “' + escapeHtml(input.value) + '”</p></div>';
        }
        html += '<a class="predictive__all btn btn--outline btn--small" href="' + (CFG.routes ? CFG.routes.search : '/search') + '?q=' + encodeURIComponent(input.value) + '">' +
          escapeHtml(CFG.strings.viewAll || 'View all results') + '</a>';
        results.innerHTML = html;
        form.classList.add('is-open');
        results.hidden = false;
      }

      function close() { form.classList.remove('is-open'); results.hidden = true; }

      var run = debounce(function () {
        var q = input.value.trim();
        if (q.length < 2) { close(); return; }
        if (controller) controller.abort();
        controller = new AbortController();
        var types = 'product';
        if (CFG.searchCollections) types += ',collection';
        if (CFG.searchPages) types += ',page,article';
        types += ',query';
        var url = (CFG.routes ? CFG.routes.search || '/search' : '/search') + '/suggest.json?q=' + encodeURIComponent(q) +
          '&resources[type]=' + types + '&resources[limit]=' + limit + '&resources[options][unavailable_products]=last';
        fetch(url, { signal: controller.signal, headers: { Accept: 'application/json' } })
          .then(function (r) { return r.json(); })
          .then(render)
          .catch(function () {});
      }, 240);

      on(input, 'input', run);
      on(input, 'focus', function () { if (input.value.trim().length >= 2) run(); });
      on(form, 'submit', close);
      on(document, 'click', function (e) { if (!form.contains(e.target)) close(); });
      on(input, 'keydown', function (e) { if (e.key === 'Escape') { close(); input.blur(); } });
    });
  }

  /* ------------------------------------------------------ product module */
  function initProduct(root) {
    var scope = root || document;
    $$('[data-product-form]', scope).forEach(function (form) {
      var section = form.closest('[data-product-section]') || document;
      var jsonEl = $('[data-product-json]', section);
      var product;
      try { product = jsonEl ? JSON.parse(jsonEl.textContent) : null; } catch (e) { product = null; }
      if (!product) return;

      var variants = product.variants || [];
      var options = (product.options || []).map(function (o) { return typeof o === 'string' ? { name: o } : o; });
      var idInput = $('input[name="id"]', form);
      var priceCurrent = $$('[data-price-current]', section);
      var priceCompare = $$('[data-price-compare]', section);
      var priceWrap = $$('[data-price]', section);
      var buyBtns = $$('[data-add-to-cart], [type="submit"]', form);
      var qtyInput = $('input[name="quantity"]', form);
      var inventoryEl = $('[data-inventory]', section);
      var skuEl = $('[data-sku]', section);
      var variantLabel = $('[data-variant-title]', section);
      var dynamicBtn = $('.shopify-payment-button', section);
      var mediaItems = $$('[data-media-id]', section);
      var gallery = $('[data-gallery]', section);

      /* Theme settings › Product page switches arrive as data attributes on the
         section root. A missing attribute (section === document) means "on". */
      function flag(name) {
        if (!section.getAttribute) return true;
        var value = section.getAttribute(name);
        return value === null || value === 'true';
      }
      var variantMediaOn = flag('data-variant-media');
      var markUnavailableOn = flag('data-mark-unavailable');

      function selectedOptions() {
        var out = [];
        options.forEach(function (opt, idx) {
          var checked = form.querySelector('input[name="options[' + idx + ']"]:checked') ||
                        form.querySelector('select[name="options[' + idx + ']"]') ||
                        form.querySelector('input[name="options[' + idx + ']"]');
          out.push(checked ? checked.value : null);
        });
        /* also honour hidden single-option selects */
        if (!out.length && form.querySelector('select[name="id"]')) out.push(null);
        return out;
      }

      function matchVariant(opts) {
        return variants.find(function (v) {
          return v.options.every(function (o, i) { return o === opts[i]; });
        });
      }

      function setAvailability(variant) {
        var available = variant && variant.available;
        buyBtns.forEach(function (b) {
          if (!b.hasAttribute('data-always-enabled')) {
            b.disabled = !variant || !available;
            var label = b.querySelector('[data-btn-label]');
            var txt = !variant ? (CFG.strings.unavailable || 'Unavailable')
              : !available ? (CFG.strings.soldOut || 'Sold out')
              : (CFG.strings.addToCart || 'Add to cart');
            if (label) label.textContent = txt;
            else if (!b.querySelector('.spinner')) b.textContent = txt;
          }
        });
        if (idInput) idInput.value = variant ? variant.id : '';
        if (dynamicBtn) dynamicBtn.hidden = !available;
        if (skuEl) skuEl.textContent = variant && variant.sku ? variant.sku : '';
        if (variantLabel) variantLabel.textContent = variant ? variant.title : '';

        if (inventoryEl) {
          var qty = variant ? variant.inventory_quantity : 0;
          var policy = variant ? variant.inventory_policy : 'deny';
          var threshold = parseInt(attr(inventoryEl, 'data-threshold', '5'), 10);
          if (!variant || (!available && policy !== 'continue')) {
            inventoryEl.hidden = true;
          } else if (available && policy === 'continue') {
            inventoryEl.hidden = false;
            inventoryEl.textContent = CFG.strings.backorder || 'Made to order — dispatched when ready';
            inventoryEl.dataset.state = 'backorder';
          } else if (qty > 0 && qty <= threshold) {
            inventoryEl.hidden = false;
            inventoryEl.textContent = (CFG.strings.lowStock || 'Only [count] left').replace('[count]', qty);
            inventoryEl.dataset.state = 'low';
          } else if (qty > threshold) {
            inventoryEl.hidden = false;
            inventoryEl.textContent = CFG.strings.inStock || 'In stock, ready to ship';
            inventoryEl.dataset.state = 'in';
          } else {
            inventoryEl.hidden = true;
          }
        }
      }

      function setPrice(variant) {
        if (!variant) return;
        priceCurrent.forEach(function (el) { el.textContent = formatMoney(variant.price); });
        var onSale = variant.compare_at_price && variant.compare_at_price > variant.price;
        priceCompare.forEach(function (el) {
          el.textContent = onSale ? formatMoney(variant.compare_at_price) : '';
          el.hidden = !onSale;
        });
        priceWrap.forEach(function (el) { el.classList.toggle('price--sale', !!onSale); });
        $$('[data-unit-price]', section).forEach(function (el) {
          if (variant.unit_price) {
            el.hidden = false;
            el.textContent = formatMoney(variant.unit_price) + '/' + (variant.unit_price_measurement && variant.unit_price_measurement.reference_unit ? variant.unit_price_measurement.reference_unit : '');
          } else { el.hidden = true; }
        });
      }

      function focusMedia(variant) {
        if (!variantMediaOn) return;
        if (!variant || !variant.featured_media || !mediaItems.length) return;
        var target = mediaItems.find(function (m) {
          return m.getAttribute('data-media-id') === String(variant.featured_media.id);
        });
        if (!target) return;
        mediaItems.forEach(function (m) { m.classList.toggle('is-active', m === target); });
        var thumbs = $$('[data-thumb-id]', section);
        thumbs.forEach(function (t) { t.classList.toggle('is-active', t.getAttribute('data-thumb-id') === String(variant.featured_media.id)); });
        if (gallery) {
          var idx = mediaItems.indexOf(target);
          if (gallery.scrollTo) gallery.scrollTo({ left: target.offsetLeft - gallery.offsetLeft, behavior: 'smooth' });
          if (gallery.dataset.slider !== undefined && KK.slider) {
            var inst = KK.slider.instanceFor(gallery);
            if (inst) inst.goTo(idx);
          }
        }
      }

      function update() {
        var opts = selectedOptions();
        var variant = matchVariant(opts);
        if (opts.indexOf(null) > -1) variant = variant || variants.find(function (v) { return v.id === parseInt(opts[0], 10); });
        setAvailability(variant);
        setPrice(variant);
        focusMedia(variant);
        if (markUnavailableOn) markUnavailable();
        /* keep the selected-value labels in sync */
        $$('[data-option-value]', form).forEach(function (el) {
          var i = parseInt(el.getAttribute('data-option-value'), 10);
          if (!isNaN(i) && opts[i] != null) el.textContent = opts[i];
        });

        /* keep the URL tidy */
        if (variant && window.history && window.history.replaceState) {
          var url = new URL(window.location.href);
          url.searchParams.set('variant', variant.id);
          window.history.replaceState({}, '', url.toString());
        }
      }

      function markUnavailable() {
        options.forEach(function (opt, idx) {
          var inputs = form.querySelectorAll('input[type="radio"][name="options[' + idx + ']"]');
          if (!inputs.length) return;
          var chosen = selectedOptions();
          inputs.forEach(function (input) {
            var test = chosen.slice();
            test[idx] = input.value;
            var exists = variants.some(function (v) {
              return v.options.every(function (o, i) { return test[i] === null || o === test[i]; });
            });
            var avail = variants.some(function (v) {
              return v.available && v.options.every(function (o, i) { return test[i] === null || o === test[i]; });
            });
            input.classList.toggle('is-unavailable', !exists);
            input.disabled = false;
            input.parentElement.classList.toggle('is-unavailable', !avail && exists);
          });
        });
      }

      on(form, 'change', update);
      on(form, 'input', function (e) { if (e.target.name && e.target.name.indexOf('options[') === 0) update(); });

      /* gallery thumbnails */
      delegate(section, 'click', '[data-thumb-id]', function (e, el) {
        e.preventDefault();
        var id = el.getAttribute('data-thumb-id');
        var target = mediaItems.find(function (m) { return m.getAttribute('data-media-id') === id; });
        if (!target) return;
        mediaItems.forEach(function (m) { m.classList.toggle('is-active', m === target); });
        $$('[data-thumb-id]', section).forEach(function (t) { t.classList.toggle('is-active', t === el); });
        if (target.scrollIntoView) target.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      });

      /* lightbox */
      if (CFG.lightbox !== false) {
        delegate(section, 'click', '[data-lightbox]', function (e, el) {
          e.preventDefault();
          var src = attr(el, 'data-lightbox') || ($('img', el) ? $('img', el).currentSrc : '');
          if (!src) return;
          KK.modal.open('<figure class="lightbox"><img src="' + src + '" alt="' + escapeHtml(attr(el, 'data-lightbox-alt', '')) + '"></figure>', { bare: true });
        });
      }

      /* initial state from ?variant= */
      var params = new URLSearchParams(window.location.search);
      var preset = params.get('variant');
      if (preset) {
        var v = variants.find(function (x) { return String(x.id) === preset; });
        if (v) {
          v.options.forEach(function (o, i) {
            var input = form.querySelector('input[name="options[' + i + ']"][value="' + (window.CSS && CSS.escape ? CSS.escape(o) : o) + '"]');
            if (input) input.checked = true;
            var sel = form.querySelector('select[name="options[' + i + ']"]');
            if (sel) sel.value = o;
          });
        }
      }
      update();
    });
  }

  /* -------------------------------------------------------------- slider */
  var sliders = [];
  function findScroller(el, track) {
    var candidates = [el, track];
    for (var i = 0; i < candidates.length; i++) {
      var c = candidates[i];
      if (!c) continue;
      var ox = window.getComputedStyle(c).overflowX;
      if (ox === 'auto' || ox === 'scroll') return c;
    }
    return el;
  }
  function Slider(el) {
    var self = this;
    this.el = el;
    this.track = $('[data-slider-track]', el) || el;
    this.scroller = findScroller(el, this.track);
    this.slides = $$('[data-slide]', el);
    this.prev = $('[data-slider-prev]', el);
    this.next = $('[data-slider-next]', el);
    this.dots = $('[data-slider-dots]', el);
    this.index = 0;
    this.perView = parseInt(attr(el, 'data-per-view', '1'), 10);
    if (this.slides.length <= this.perView) { el.classList.add('slider--static'); }
    on(this.prev, 'click', function () { self.goTo(self.index - 1, true); });
    on(this.next, 'click', function () { self.goTo(self.index + 1, true); });
    this.buildDots();
    on(this.scroller, 'scroll', debounce(function () { self.syncFromScroll(); }, 90), { passive: true });
    if (attr(el, 'data-autoplay') === 'true') {
      var ms = parseInt(attr(el, 'data-autoplay-speed', '6000'), 10);
      this.timer = setInterval(function () { self.goTo(self.index + 1, true); }, ms);
      on(el, 'mouseenter', function () { clearInterval(self.timer); });
      on(el, 'mouseleave', function () {
        self.timer = setInterval(function () { self.goTo(self.index + 1, true); }, ms);
      });
    }
    this.update();
  }
  Slider.prototype.pages = function () { return Math.max(1, this.slides.length - this.perView + 1); };
  Slider.prototype.buildDots = function () {
    if (!this.dots) return;
    var self = this;
    this.dots.innerHTML = '';
    for (var i = 0; i < this.pages(); i++) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'slider__dot';
      b.setAttribute('aria-label', 'Go to slide ' + (i + 1));
      b.dataset.dot = i;
      on(b, 'click', function (e) { self.goTo(parseInt(e.currentTarget.dataset.dot, 10), true); });
      this.dots.appendChild(b);
    }
  };
  Slider.prototype.goTo = function (i, animate) {
    var max = this.pages() - 1;
    this.index = i < 0 ? (attr(this.el, 'data-loop') === 'true' ? max : 0) : (i > max ? (attr(this.el, 'data-loop') === 'true' ? 0 : max) : i);
    var slide = this.slides[this.index];
    if (slide) slide.scrollIntoView({ behavior: animate === false ? 'auto' : 'smooth', inline: 'start', block: 'nearest' });
    this.update();
  };
  Slider.prototype.syncFromScroll = function () {
    var left = this.scroller.scrollLeft || 0;
    var base = this.slides.length ? this.slides[0].offsetLeft : 0;
    var best = 0, bestDist = Infinity;
    this.slides.forEach(function (s, i) {
      var d = Math.abs((s.offsetLeft - base) - left);
      if (d < bestDist) { bestDist = d; best = i; }
    });
    if (best !== this.index) { this.index = Math.min(best, this.pages() - 1); this.update(); }
  };
;
  Slider.prototype.update = function () {
    var max = this.pages() - 1;
    if (this.prev) this.prev.disabled = this.index <= 0 && attr(this.el, 'data-loop') !== 'true';
    if (this.next) this.next.disabled = this.index >= max && attr(this.el, 'data-loop') !== 'true';
    if (this.dots) {
      $$('[data-dot]', this.dots).forEach(function (d, i) { d.classList.toggle('is-active', i === this.index); }, this);
    }
    this.slides.forEach(function (s, i) { s.classList.toggle('is-active', i === this.index); }, this);
    this.el.setAttribute('data-index', this.index);
  };
  KK.slider = {
    instanceFor: function (el) { return sliders.find(function (s) { return s.el === el; }); },
    init: function (root) {
      $$('[data-slider]', root || document).forEach(function (el) {
        if (el.dataset.sliderInit) return;
        el.dataset.sliderInit = 'true';
        sliders.push(new Slider(el));
      });
    }
  };

  /* ---------------------------------------------------------- marquee js */
  function measureMarquee(track) {
    var groups = track.children;
    if (groups.length < 2) return;
    var style = window.getComputedStyle(track);
    var gap = parseFloat(style.columnGap || style.gap) || 0;
    var half = Math.round(groups.length / 2);
    var shift = 0;
    for (var i = 0; i < half; i++) { shift += groups[i].getBoundingClientRect().width; }
    shift += gap * half;
    track.style.setProperty('--marquee-shift', Math.round(shift) + 'px');
  }

  function initMarquee(root) {
    $$('[data-marquee]', root || document).forEach(function (el) {
      var track = $('[data-marquee-track]', el);
      if (!track) return;
      if (!track.dataset.dup) {
        track.dataset.dup = 'true';
        /* duplicate until the track is wide enough to scroll seamlessly */
        var guard = 0;
        while (track.scrollWidth < el.clientWidth * 2 && guard < 6) {
          track.innerHTML += track.innerHTML;
          guard++;
        }
      }
      measureMarquee(track);
      if (!track.dataset.resizeBound) {
        track.dataset.resizeBound = 'true';
        window.addEventListener('resize', debounce(function () { measureMarquee(track); }, 250));
        window.addEventListener('load', function () { measureMarquee(track); });
      }
    });
  }

  /* ----------------------------------------------------------- countdown */
  function initCountdown(root) {
    $$('[data-countdown]', root || document).forEach(function (el) {
      if (el.dataset.timerInit) return;
      el.dataset.timerInit = 'true';
      var end = new Date(el.getAttribute('data-countdown')).getTime();
      if (isNaN(end)) return;
      function pad(n) { return String(n).padStart(2, '0'); }
      function tick() {
        var diff = end - Date.now();
        if (diff <= 0) {
          el.innerHTML = '';
          el.classList.add('is-finished');
          var done = el.getAttribute('data-finished-text');
          if (done) el.textContent = done;
          clearInterval(t);
          return;
        }
        var d = Math.floor(diff / 86400000);
        var h = Math.floor((diff % 86400000) / 3600000);
        var m = Math.floor((diff % 3600000) / 60000);
        var s = Math.floor((diff % 60000) / 1000);
        $$('[data-cd-value]', el).forEach(function (cell) {
          var unit = cell.getAttribute('data-cd-value');
          var val = unit === 'days' ? d : unit === 'hours' ? h : unit === 'minutes' ? m : s;
          cell.textContent = pad(val);
        });
      }
      tick();
      var t = setInterval(tick, 1000);
    });
  }

  /* ------------------------------------------------------- load more/etc */
  function initLoadMore(root) {
    var scope = root || document;
    delegate(scope, 'click', '[data-load-more]', function (e, el) {
      e.preventDefault();
      var grid = document.querySelector(el.getAttribute('data-load-more'));
      var next = parseInt(attr(el, 'data-page', '1'), 10) + 1;
      var url = attr(el, 'data-url', window.location.href.split('?')[0]) + '?page=' + next;
      el.classList.add('is-loading');
      fetch(url, { headers: { Accept: 'text/html' } })
        .then(function (r) { return r.text(); })
        .then(function (html) {
          var tmp = document.createElement('div');
          tmp.innerHTML = html;
          var source = tmp.querySelector(el.getAttribute('data-load-more'));
          var fresh = source ? $$('[data-load-item]', source) : [];
          if (!fresh.length || !grid) { el.remove(); return; }
          fresh.forEach(function (node) {
            var clone = node.cloneNode(true);
            clone.setAttribute('data-animate', '');
            grid.appendChild(clone);
          });
          el.setAttribute('data-page', String(next));
          var nextLink = tmp.querySelector('[data-load-more]');
          el.classList.remove('is-loading');
          if (!nextLink) el.remove();
          KK.init(grid);
        })
        .catch(function () { el.classList.remove('is-loading'); });
    });

    /* infinite scroll */
    var infinite = $('[data-infinite-scroll]');
    if (infinite && 'IntersectionObserver' in window) {
      var btn = $('[data-load-more]');
      var io = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting && btn && !btn.classList.contains('is-loading')) btn.click();
      }, { rootMargin: '400px' });
      io.observe(infinite);
    }
  }

  /* ------------------------------------------------ product recommendations */
  function initRecommendations(root) {
    $$('product-recommendations', root || document).forEach(function (el) {
      if (el.dataset.loaded === 'true') return;
      el.dataset.loaded = 'true';
      var url = el.getAttribute('data-url');
      if (!url) return;
      fetch(url, { headers: { Accept: 'text/html' } })
        .then(function (r) { return r.text(); })
        .then(function (html) {
          var tmp = document.createElement('div');
          tmp.innerHTML = html;
          var inner = tmp.querySelector('product-recommendations');
          if (inner && inner.innerHTML.replace(/\s/g, '').length > 0) {
            el.innerHTML = inner.innerHTML;
            el.classList.add('has-products');
            KK.init(el);
          } else {
            el.remove();
          }
        })
        .catch(function () {});
    });
  }

  /* --------------------------------------------------------------- misc */
  function initMisc(root) {
    var scope = root || document;

    /* accordion smooth open */
    $$('details[data-accordion]', scope).forEach(function (d) {
      var body = $('[data-accordion-body]', d);
      if (!body || d.dataset.accInit) return;
      d.dataset.accInit = 'true';
      if (d.open) body.style.maxHeight = body.scrollHeight + 'px';
      on(d, 'toggle', function () {
        body.style.maxHeight = d.open ? body.scrollHeight + 'px' : '0px';
      });
    });

    /* quantity inputs on product pages */
    delegate(scope, 'click', '[data-qty-btn]', function (e, el) {
      e.preventDefault();
      var wrap = el.closest('[data-quantity]');
      if (!wrap) return;
      var input = $('input', wrap);
      if (!input) return;
      var step = parseInt(attr(el, 'data-qty-btn', '1'), 10);
      var min = parseInt(attr(input, 'min', '1'), 10);
      var val = (parseInt(input.value, 10) || min) + step;
      input.value = Math.max(min, val);
      input.dispatchEvent(new Event('change', { bubbles: true }));
    });

    /* tabs */
    delegate(scope, 'click', '[data-tab]', function (e, el) {
      e.preventDefault();
      var group = el.closest('[data-tabs]');
      if (!group) return;
      var id = el.getAttribute('data-tab');
      $$('[data-tab]', group).forEach(function (t) {
        t.classList.toggle('is-active', t === el);
        t.setAttribute('aria-selected', String(t === el));
      });
      $$('[data-tab-panel]', group).forEach(function (p) {
        p.hidden = p.getAttribute('data-tab-panel') !== id;
      });
    });

    /* share / copy */
    delegate(scope, 'click', '[data-share-copy]', function (e, el) {
      e.preventDefault();
      var url = attr(el, 'data-share-url', window.location.href);
      if (navigator.share) {
        navigator.share({ title: document.title, url: url }).catch(function () {});
      } else if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(function () {
          var label = el.querySelector('[data-share-label]');
          if (label) { var old = label.textContent; label.textContent = CFG.strings.copied || 'Copied'; setTimeout(function () { label.textContent = old; }, 1800); }
        });
      }
    });

    /* collection sorting */
    delegate(scope, 'change', '[data-sort-select]', function (e, el) {
      var url = new URL(window.location.href);
      url.searchParams.set('sort_by', el.value);
      url.searchParams.delete('page');
      window.location.href = url.toString();
    });

    /* grid / list view toggle */
    var savedView = null;
    try { savedView = window.localStorage.getItem('kk-view'); } catch (err) { savedView = null; }
    if (savedView) document.body.classList.add('view-' + savedView);
    $$('[data-view-toggle]', scope).forEach(function (btn) {
      var v = btn.getAttribute('data-view-toggle');
      btn.classList.toggle('is-active', (savedView || 'grid') === v);
      on(btn, 'click', function () {
        document.body.classList.remove('view-grid', 'view-list');
        document.body.classList.add('view-' + v);
        try { window.localStorage.setItem('kk-view', v); } catch (err) {}
        $$('[data-view-toggle]').forEach(function (b) {
          b.classList.toggle('is-active', b.getAttribute('data-view-toggle') === v);
        });
      });
    });

    /* facet show more */
    delegate(scope, 'click', '[data-facet-more]', function (e, el) {
      e.preventDefault();
      var list = el.parentNode.querySelector('[data-facet-list]');
      if (!list) return;
      var expanded = list.classList.toggle('is-expanded');
      el.textContent = expanded ? el.getAttribute('data-less-label') : el.getAttribute('data-more-label');
    });

    /* click-to-load video facades (keeps YouTube / Vimeo off the page until asked) */
    delegate(scope, 'click', '[data-video-facade]', function (e, el) {
      var src = el.getAttribute('data-video-facade');
      if (!src) return;
      var iframe = document.createElement('iframe');
      iframe.src = src + (src.indexOf('?') === -1 ? '?' : '&') + 'autoplay=1';
      iframe.title = el.getAttribute('data-video-title') || 'Video';
      iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
      iframe.allowFullscreen = true;
      iframe.loading = 'lazy';
      iframe.className = 'video-facade__frame';
      el.parentNode.replaceChild(iframe, el);
    });

    /* lightbox for anything outside a product section (galleries, lookbooks) */
    if (!document.__kkLightboxBound) {
      document.__kkLightboxBound = true;
      document.addEventListener('click', function (e) {
        var el = e.target.closest ? e.target.closest('[data-lightbox]') : null;
        if (!el || el.closest('[data-product-section]')) return;
        e.preventDefault();
        var src = el.getAttribute('data-lightbox');
        if (!src) {
          var img = el.querySelector('img');
          src = img ? (img.currentSrc || img.src) : '';
        }
        if (!src) return;
        var cap = el.getAttribute('data-lightbox-caption') || '';
        var alt = el.getAttribute('data-lightbox-alt') || cap;
        KK.modal.open(
          '<figure class="lightbox"><img src="' + src + '" alt="' + escapeHtml(alt) + '">' +
          (cap ? '<figcaption class="lightbox__caption">' + escapeHtml(cap) + '</figcaption>' : '') +
          '</figure>',
          { bare: true }
        );
      });
    }

    /* generic show / hide toggles (customer area, password recovery) */
    delegate(scope, 'click', '[data-toggle-hidden]', function (e, el) {
      e.preventDefault();
      var target = document.getElementById(el.getAttribute('data-toggle-hidden'));
      if (!target) return;
      target.hidden = !target.hidden;
      if (!target.hidden) {
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        var first = target.querySelector('input, select, textarea, button');
        if (first) setTimeout(function () { first.focus({ preventScroll: true }); }, 300);
      }
      var self = el.getAttribute('data-toggle-self');
      if (self) {
        var selfEl = document.getElementById(self);
        if (selfEl) selfEl.hidden = !target.hidden;
      }
    });

    /* hover zoom origin */
    delegate(scope, 'mousemove', '[data-zoom="true"]', function (e, el) {
      var r = el.getBoundingClientRect();
      el.style.setProperty('--zx', (((e.clientX - r.left) / r.width) * 100).toFixed(2) + '%');
      el.style.setProperty('--zy', (((e.clientY - r.top) / r.height) * 100).toFixed(2) + '%');
    });

    /* size guide / info modal */
    delegate(scope, 'click', '[data-size-guide]', function (e, el) {
      e.preventDefault();
      var src = document.getElementById(el.getAttribute('data-guide-id'));
      var title = el.getAttribute('data-guide-title') || '';
      if (!src) return;
      KK.modal.open('<h3 class="modal__title">' + escapeHtml(title) + '</h3><div class="rte">' + src.innerHTML + '</div>');
    });

    /* smooth in-page anchors */
    delegate(scope, 'click', 'a[href^="#"]', function (e, el) {
      var id = el.getAttribute('href');
      if (!id || id === '#') return;
      var target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    /* customer address forms */
    $$('[data-address-form]', scope).forEach(function (form) {
      var toggle = $('[data-address-toggle]', form);
      var panel = $('[data-address-panel]', form);
      if (toggle && panel) {
        on(toggle, 'click', function (e) { e.preventDefault(); panel.hidden = !panel.hidden; });
      }
    });
  }

  /* --------------------------------------------------------- bootstrapping */
  KK.init = function (root) {
    var scope = root || document;
    initPanels(scope);
    initCart(scope);
    initSearch(scope);
    initProduct(scope);
    KK.slider.init(scope);
    initMarquee(scope);
    initCountdown(scope);
    initLoadMore(scope);
    initRecommendations(scope);
    initMisc(scope);
    initReveal(scope);
  };

  function boot() {
    initHeader();
    KK.init(document);
    Cart.refresh().catch(function () {});
  }

  if (document.readyState === 'loading') on(document, 'DOMContentLoaded', boot);
  else boot();

  /* theme editor support */
  on(document, 'shopify:section:load', function (e) {
    var sec = e.target;
    KK.init(sec);
  });
  on(document, 'shopify:section:unload', function () { Cart.refresh().catch(function () {}); });
  on(document, 'shopify:block:select', function (e) {
    var el = e.target;
    if (el && el.scrollIntoView) el.scrollIntoView({ block: 'center' });
  });
  on(document, 'shopify:inspector:activate', function () { KK.init(document); });
})();
