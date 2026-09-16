/* ==========================================================================
   HOUSE OF KALA KATHA — Theme JavaScript
   ========================================================================== */
(function () {
  'use strict';

  var doc = document;

  /* ------------------------------------------------------------------ */
  /* Helpers                                                             */
  /* ------------------------------------------------------------------ */
  function moneyFormatValue(cents, format) {
    if (typeof cents === 'string') cents = cents.replace('.', '');
    var value = '';
    var placeholderRegex = /\{\{\s*(\w+)\s*\}\}/;
    var match = (format || '').match(placeholderRegex);
    if (!match) return String(cents);

    function withDelimiters(number, precision, thousands, decimal) {
      precision = precision == null ? 2 : precision;
      thousands = thousands == null ? ',' : thousands;
      decimal = decimal == null ? '.' : decimal;
      if (isNaN(number) || number == null) return '0';
      number = (number / 100.0).toFixed(precision);
      var parts = number.split('.');
      var dollars = parts[0].replace(/(\d)(?=(\d\d\d)+(?!\d))/g, '$1' + thousands);
      return dollars + (parts[1] ? decimal + parts[1] : '');
    }

    switch (match[1]) {
      case 'amount':
        value = withDelimiters(cents, 2);
        break;
      case 'amount_no_decimals':
        value = withDelimiters(cents, 0);
        break;
      case 'amount_with_comma_separator':
        value = withDelimiters(cents, 2, '.', ',');
        break;
      case 'amount_no_decimals_with_comma_separator':
        value = withDelimiters(cents, 0, '.', ',');
        break;
      case 'amount_with_space_separator':
        value = withDelimiters(cents, 2, ' ', '.');
        break;
      default:
        value = withDelimiters(cents, 2);
    }
    return format.replace(placeholderRegex, value);
  }

  function debounce(fn, wait) {
    var t;
    return function () {
      var args = arguments;
      var ctx = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(ctx, args); }, wait);
    };
  }

  /* ------------------------------------------------------------------ */
  /* Drawers                                                             */
  /* ------------------------------------------------------------------ */
  var drawers = {
    menu: doc.querySelector('[data-menu-drawer]'),
    search: doc.querySelector('[data-search-drawer]'),
    cart: doc.getElementById('CartDrawer')
  };

  function openDrawer(el) {
    if (!el) return;
    el.classList.add('is-open');
    el.setAttribute('aria-hidden', 'false');
    doc.documentElement.classList.add('drawer-open');
    doc.body.style.overflow = 'hidden';
  }
  function closeDrawer(el) {
    if (!el) return;
    el.classList.remove('is-open');
    el.setAttribute('aria-hidden', 'true');
    doc.documentElement.classList.remove('drawer-open');
    doc.body.style.overflow = '';
  }
  function closeAllDrawers() {
    closeDrawer(drawers.menu);
    closeDrawer(drawers.search);
    closeDrawer(drawers.cart);
  }

  doc.addEventListener('click', function (e) {
    if (e.target.closest('[data-menu-open]')) {
      openDrawer(drawers.menu);
      return;
    }
    if (e.target.closest('[data-menu-close]')) {
      closeDrawer(drawers.menu);
      return;
    }
    if (e.target.closest('[data-search-open]')) {
      openDrawer(drawers.search);
      var input = drawers.search && drawers.search.querySelector('[data-search-input]');
      if (input) setTimeout(function () { input.focus(); }, 150);
      return;
    }
    if (e.target.closest('[data-search-close]')) {
      closeDrawer(drawers.search);
      return;
    }
    if (e.target.closest('[data-cart-drawer-toggle]')) {
      if (drawers.cart) {
        e.preventDefault();
        openDrawer(drawers.cart);
      }
      return;
    }
    if (e.target.closest('[data-cart-drawer-close]')) {
      closeDrawer(drawers.cart);
      return;
    }
  });

  doc.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { closeAllDrawers(); closeRegionModals(); }
  });

  /* ------------------------------------------------------------------ */
  /* Sticky header shadow                                                */
  /* ------------------------------------------------------------------ */
  var header = doc.querySelector('.site-header--sticky');
  if (header) {
    var onScroll = function () {
      header.classList.toggle('is-scrolled', window.scrollY > 8);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ------------------------------------------------------------------ */
  /* Announcement bar rotation                                           */
  /* ------------------------------------------------------------------ */
  var announcement = doc.querySelector('[data-announcement-bar]');
  if (announcement) {
    var messages = announcement.querySelectorAll('[data-announcement-message]');
    if (messages.length > 1) {
      var current = 0;
      setInterval(function () {
        messages[current].classList.remove('is-active');
        current = (current + 1) % messages.length;
        messages[current].classList.add('is-active');
      }, 4500);
    }
  }

  /* ------------------------------------------------------------------ */
  /* Reveal on scroll                                                    */
  /* ------------------------------------------------------------------ */
  var revealObserver = null;
  var isDesignMode = !!(window.Shopify && window.Shopify.designMode);

  function revealElement(el) {
    el.classList.add('is-visible');
  }

  var revealEls = doc.querySelectorAll('[data-reveal]');

  if (isDesignMode) {
    // Never hide content in the Shopify theme editor — sections must stay
    // visible while the merchant is editing them.
    revealEls.forEach(revealElement);
  } else if ('IntersectionObserver' in window && revealEls.length) {
    revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          revealElement(entry.target);
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function (el) { revealObserver.observe(el); });
  } else {
    revealEls.forEach(revealElement);
  }

  // Shopify re-renders a section in place whenever the merchant changes a
  // setting. Newly-inserted [data-reveal] nodes would otherwise stay at
  // opacity:0 (a "blank" section), so keep them in sync with a MutationObserver.
  if ('MutationObserver' in window) {
    var revealMutationObserver = new MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        mutation.addedNodes.forEach(function (node) {
          if (node.nodeType !== 1) return;
          var newlyAdded = [];
          if (node.matches && node.matches('[data-reveal]')) newlyAdded.push(node);
          if (node.querySelectorAll) {
            node.querySelectorAll('[data-reveal]').forEach(function (el) { newlyAdded.push(el); });
          }
          newlyAdded.forEach(function (el) {
            if (isDesignMode || !revealObserver) {
              revealElement(el);
            } else {
              revealObserver.observe(el);
            }
          });
        });
      });
    });
    revealMutationObserver.observe(doc.body, { childList: true, subtree: true });
  }

  /* ------------------------------------------------------------------ */
  /* Quantity inputs                                                     */
  /* ------------------------------------------------------------------ */
  function syncQuantity(input, delta) {
    var value = parseInt(input.value, 10);
    if (isNaN(value)) value = 1;
    value = Math.max(1, value + delta);
    input.value = value;
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }

  doc.addEventListener('click', function (e) {
    var btn = e.target.closest('.quantity__btn');
    if (!btn) return;
    var wrap = btn.closest('.quantity');
    if (!wrap) return;
    var input = wrap.querySelector('.quantity__input');
    if (!input) return;
    var delta = btn.getAttribute('name') === 'plus' ? 1 : -1;
    syncQuantity(input, delta);
  });

  /* ------------------------------------------------------------------ */
  /* Cart drawer updates                                                 */
  /* ------------------------------------------------------------------ */
  function updateCartCount(count) {
    doc.querySelectorAll('[data-cart-count]').forEach(function (el) {
      el.textContent = count;
      if (count === 0) el.setAttribute('hidden', '');
      else el.removeAttribute('hidden');
    });
  }

  async function refreshCartDrawer() {
    if (!window.routes || !window.routes.cart_url) return;
    var res = await fetch(window.routes.cart_url + '?sections=cart-drawer', {
      headers: { Accept: 'application/json' }
    });
    var data = await res.json();
    var html = data['cart-drawer'];
    if (!html) return;
    var current = doc.getElementById('CartDrawer');
    if (!current) return;
    var wasOpen = current.classList.contains('is-open');
    var tmp = doc.createElement('div');
    tmp.innerHTML = html;
    var fresh = tmp.querySelector('#CartDrawer');
    if (fresh) {
      if (wasOpen) fresh.classList.add('is-open');
      current.replaceWith(fresh);
      drawers.cart = fresh;
    }
  }

  async function changeCartLine(line, quantity) {
    if (!window.routes || !window.routes.cart_change_url) return;
    var res = await fetch(window.routes.cart_change_url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ line: line, quantity: quantity })
    });
    var state = await res.json();
    if (state.item_count != null) updateCartCount(state.item_count);
    await refreshCartDrawer();
    return state;
  }

  /* ------------------------------------------------------------------ */
  /* Ajax add to cart                                                    */
  /* ------------------------------------------------------------------ */
  doc.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form || !form.matches || !form.matches('form[action*="/cart/add"]')) return;
    if (!window.routes || !window.routes.cart_add_url) return;
    e.preventDefault();

    var addBtn = form.querySelector('[name="add"]');
    var errorEl = form.querySelector('[data-cart-error]');
    var idInput = form.querySelector('input[name="id"]');
    var qtyInput = form.querySelector('input[name="quantity"]');
    var originalLabel = addBtn ? addBtn.textContent : '';

    if (!idInput) return;
    if (errorEl) {
      errorEl.textContent = '';
      errorEl.hidden = true;
    }
    if (addBtn) {
      addBtn.disabled = true;
      addBtn.textContent = (window.cartStrings && window.cartStrings.adding) || 'Adding…';
    }

    var body = new URLSearchParams();
    body.set('id', idInput.value);
    body.set('quantity', qtyInput ? (qtyInput.value || 1) : 1);

    fetch(window.routes.cart_add_url + '.js', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', Accept: 'application/json' },
      body: body.toString()
    })
      .then(function (res) {
        return res.json().then(function (data) { return { ok: res.ok, data: data }; });
      })
      .then(function (result) {
        if (!result.ok) {
          throw (result.data && (result.data.description || result.data.message)) ||
            (window.cartStrings && window.cartStrings.error) ||
            'Could not add to bag. Please try again.';
        }
        return fetch(window.routes.cart_url + '.js', { headers: { Accept: 'application/json' } })
          .then(function (r) { return r.json(); });
      })
      .then(function (cart) {
        if (cart && cart.item_count != null) updateCartCount(cart.item_count);
        return refreshCartDrawer();
      })
      .then(function () {
        drawers.cart = doc.getElementById('CartDrawer');
        openDrawer(drawers.cart);
      })
      .catch(function (err) {
        if (errorEl) {
          errorEl.textContent = err && err.length ? err : 'Could not add to bag. Please try again.';
          errorEl.hidden = false;
        }
      })
      .then(function () {
        if (addBtn) {
          addBtn.disabled = false;
          addBtn.textContent = originalLabel;
        }
      });
  });

  doc.addEventListener('change', function (e) {
    var input = e.target.closest('.cart-drawer__item .quantity__input');
    if (!input) return;
    var item = input.closest('[data-cart-item]');
    var index = item ? parseInt(item.getAttribute('data-index'), 10) : null;
    if (!index) return;
    changeCartLine(index, parseInt(input.value, 10) || 1);
  });

  doc.addEventListener('click', function (e) {
    var remove = e.target.closest('[data-cart-remove]');
    if (!remove) return;
    e.preventDefault();
    var item = remove.closest('[data-cart-item]');
    var index = item ? parseInt(item.getAttribute('data-index'), 10) : null;
    if (!index) return;
    changeCartLine(index, 0);
  });

  /* ------------------------------------------------------------------ */
  /* Variant picker                                                      */
  /* ------------------------------------------------------------------ */
  function getVariantData(picker) {
    var jsonEl = picker.querySelector('[data-variant-json]');
    if (!jsonEl) return [];
    try { return JSON.parse(jsonEl.textContent); } catch (err) { return []; }
  }

  function getSelectedOptions(picker) {
    var selected = [];
    picker.querySelectorAll('.variant-picker__option').forEach(function (fieldset, i) {
      var checked = fieldset.querySelector('input[type="radio"]:checked');
      selected.push(checked ? checked.value : null);
    });
    return selected;
  }

  function findVariant(variants, options) {
    return variants.find(function (v) {
      return v.options.every(function (opt, i) { return opt === options[i]; });
    });
  }

  function updateVariantState(picker, variant, options) {
    var variants = getVariantData(picker);
    var sectionId = picker.getAttribute('data-section');

    // Update hidden id input
    var idInput = doc.querySelector('input[data-product-id][data-section="' + sectionId + '"]') ||
                   doc.querySelector('input[name="id"]');
    if (idInput && variant) idInput.value = variant.id;

    // Update add-to-cart button
    var form = picker.closest('form') || doc.querySelector('form[action*="/cart/add"]');
    var addBtn = form ? form.querySelector('[name="add"]') : null;
    if (addBtn) {
      if (variant && variant.available) {
        addBtn.disabled = false;
        addBtn.textContent = (window.cartStrings && window.cartStrings.addToCart) || 'Add to bag';
      } else {
        addBtn.disabled = true;
        addBtn.textContent = (window.cartStrings && window.cartStrings.soldOut) || 'Sold out';
      }
    }

    // Update option value labels
    picker.querySelectorAll('[data-option-value]').forEach(function (el) {
      var idx = parseInt(el.getAttribute('data-index'), 10);
      if (options[idx]) el.textContent = options[idx];
    });

    // Update price
    if (variant) {
      var priceWrap = doc.querySelector('[data-product-price]');
      if (priceWrap && window.moneyFormat) {
        var current = priceWrap.querySelector('.price__current');
        var compare = priceWrap.querySelector('.price__compare');
        if (current) current.textContent = moneyFormatValue(variant.price, window.moneyFormat);
        if (variant.compare_at_price && variant.compare_at_price > variant.price) {
          if (!compare) {
            compare = doc.createElement('s');
            compare.className = 'price__compare';
            priceWrap.querySelector('.price').prepend(compare);
          }
          compare.textContent = moneyFormatValue(variant.compare_at_price, window.moneyFormat);
          current.classList.add('price__current--sale');
        } else {
          if (compare) compare.remove();
          current.classList.remove('price__current--sale');
        }
      }
    }

    // Mark unavailable pills
    picker.querySelectorAll('.variant-pill').forEach(function (pill) {
      var pillOptionIndex = parseInt(pill.getAttribute('data-index'), 10);
      var pillValue = pill.getAttribute('data-value');
      var available = variants.some(function (v) {
        if (!v.available) return false;
        if (v.options[pillOptionIndex] !== pillValue) return false;
        return options.every(function (sel, i) {
          if (i === pillOptionIndex) return true;
          return sel == null || v.options[i] === sel;
        });
      });
      pill.classList.toggle('is-unavailable', !available);
    });
  }

  doc.addEventListener('change', function (e) {
    var radio = e.target.closest('.variant-picker input[type="radio"]');
    if (!radio) return;
    var picker = radio.closest('.variant-picker');
    if (!picker) return;
    var variants = getVariantData(picker);
    var options = getSelectedOptions(picker);
    var variant = findVariant(variants, options);
    updateVariantState(picker, variant, options);

    // Mark selected pills
    picker.querySelectorAll('.variant-pill').forEach(function (pill) {
      var idx = pill.getAttribute('data-index');
      var value = pill.getAttribute('data-value');
      pill.classList.toggle('is-selected', options[idx] === value);
    });
  });

  // Initial unavailable state
  doc.querySelectorAll('.variant-picker').forEach(function (picker) {
    var variants = getVariantData(picker);
    if (!variants.length) return;
    var options = getSelectedOptions(picker);
    var variant = findVariant(variants, options);
    if (!variant) variant = variants[0];
    updateVariantState(picker, variant, options);
  });

  /* ------------------------------------------------------------------ */
  /* Facets / sort                                                       */
  /* ------------------------------------------------------------------ */
  doc.addEventListener('click', function (e) {
    var toggle = e.target.closest('[data-filters-toggle]');
    if (toggle) {
      var form = toggle.closest('[data-filter-form]');
      var panel = form ? form.querySelector('[data-filters-panel]') : null;
      if (panel) panel.hidden = !panel.hidden;
      var sortMenu = form ? form.querySelector('[data-sort-menu]') : null;
      if (sortMenu && !panel.hidden) sortMenu.removeAttribute('open');
      return;
    }

    var sortOption = e.target.closest('[data-sort-value]');
    if (sortOption) {
      var sortForm = sortOption.closest('form');
      if (sortForm) {
        var hidden = sortForm.querySelector('[data-sort-hidden]');
        if (hidden) hidden.value = sortOption.getAttribute('data-sort-value');
        sortForm.submit();
      }
      return;
    }

    // Close any open sort menu when clicking outside of it
    doc.querySelectorAll('[data-sort-menu][open]').forEach(function (menu) {
      if (!menu.contains(e.target)) menu.removeAttribute('open');
    });
  });

  doc.addEventListener('change', function (e) {
    if (e.target.matches('[data-sort-select]')) {
      var form = e.target.closest('form');
      if (form) form.submit();
      return;
    }
    if (e.target.matches('[data-auto-submit]')) {
      var f = e.target.closest('form');
      if (f) f.submit();
    }
  });

  /* ------------------------------------------------------------------ */
  /* Predictive search                                                   */
  /* ------------------------------------------------------------------ */
  var searchInput = doc.querySelector('[data-search-input]');
  var predictive = doc.querySelector('[data-predictive-search]');
  var predictiveBody = doc.querySelector('[data-predictive-results]');

  if (searchInput && predictiveBody) {
    var handleSearch = debounce(function (term) {
      term = term.trim();
      if (term.length < 2) {
        predictive.hidden = true;
        predictiveBody.innerHTML = '';
        return;
      }
      var url = (window.shopUrl || '') + '/search/suggest.json?q=' + encodeURIComponent(term) +
        '&resources[type]=product&resources[limit]=4&resources[options][unavailable_products]=last';
      fetch(url)
        .then(function (r) { return r.json(); })
        .then(function (data) {
          var products = (data.resources && data.resources.results && data.resources.results.products) || [];
          predictiveBody.innerHTML = '';
          if (!products.length) {
            predictiveBody.innerHTML = '<p class="predictive-search__empty">No results for “' + term + '”.</p>';
          } else {
            products.forEach(function (p) {
              var a = doc.createElement('a');
              a.className = 'predictive-search__item';
              a.href = p.url;
              var img = p.image ? '<img src="' + p.image + '" alt="' + (p.title || '') + '" loading="lazy">' : '';
              a.innerHTML = img + '<span>' + (p.title || '') + '</span><span class="price__current">' + (p.price || '') + '</span>';
              predictiveBody.appendChild(a);
            });
          }
          predictive.hidden = false;
        })
        .catch(function () { predictive.hidden = true; });
    }, 250);

    searchInput.addEventListener('input', function () { handleSearch(searchInput.value); });
  }

  /* ------------------------------------------------------------------ */
  /* Interactive craft map & region modals                               */
  /* ------------------------------------------------------------------ */
  function openRegionModal(key) {
    var modal = doc.querySelector('[data-region-modal="' + key + '"]');
    if (!modal) return;
    doc.querySelectorAll('.region-modal.is-open').forEach(function (m) {
      m.classList.remove('is-open');
      m.hidden = true;
    });
    modal.hidden = false;
    modal.classList.add('is-open');
    doc.body.style.overflow = 'hidden';
  }

  function closeRegionModals() {
    var anyOpen = false;
    doc.querySelectorAll('.region-modal.is-open').forEach(function (m) {
      m.classList.remove('is-open');
      m.hidden = true;
      anyOpen = true;
    });
    if (anyOpen && !doc.querySelector('.cart-drawer.is-open, .menu-drawer.is-open, .search-drawer.is-open')) {
      doc.body.style.overflow = '';
    }
  }

  doc.addEventListener('click', function (e) {
    var zone = e.target.closest('[data-region]');
    if (zone) {
      openRegionModal(zone.getAttribute('data-region'));
      return;
    }
    var openBtn = e.target.closest('[data-region-open]');
    if (openBtn) {
      openRegionModal(openBtn.getAttribute('data-region-open'));
      return;
    }
    if (e.target.closest('[data-region-close]')) {
      closeRegionModals();
    }
  });

  doc.addEventListener('keydown', function (e) {
    if ((e.key === 'Enter' || e.key === ' ') && e.target && e.target.matches && e.target.matches('[data-region]')) {
      e.preventDefault();
      openRegionModal(e.target.getAttribute('data-region'));
    }
  });

  /* ------------------------------------------------------------------ */
  /* Testimonials slider                                                 */
  /* ------------------------------------------------------------------ */
  function initTestimonialSlider(track) {
    if (!track || track.dataset.sliderInit) return;
    track.dataset.sliderInit = 'true';

    var wrap = track.closest('.testimonials');
    var prev = wrap ? wrap.querySelector('[data-slider-prev]') : null;
    var next = wrap ? wrap.querySelector('[data-slider-next]') : null;
    var dots = wrap ? Array.prototype.slice.call(wrap.querySelectorAll('[data-slider-dot]')) : [];
    var autoplay = track.getAttribute('data-autoplay') === 'true';
    var delay = parseInt(track.getAttribute('data-delay'), 10) || 5000;
    var timer = null;

    function cardStep() {
      var first = track.querySelector('.testimonial');
      if (!first) return 0;
      var gap = parseFloat(getComputedStyle(track).columnGap);
      if (isNaN(gap)) gap = 0;
      var basis = parseFloat(getComputedStyle(first).flexBasis);
      if (!basis || isNaN(basis)) basis = first.offsetWidth;
      return basis + gap;
    }

    function scrollBy(dir) {
      var step = cardStep();
      if (!step) return;
      track.scrollBy({ left: dir * step, behavior: 'smooth' });
    }

    function goTo(i) {
      var cards = track.querySelectorAll('.testimonial');
      if (!cards.length) return;
      i = Math.max(0, Math.min(i, cards.length - 1));
      track.scrollTo({ left: cards[i].offsetLeft, behavior: 'smooth' });
    }

    function updateDots() {
      var cards = track.querySelectorAll('.testimonial');
      if (!dots.length || !cards.length) return;
      var left = track.scrollLeft + 1;
      var active = 0;
      for (var i = 0; i < cards.length; i++) {
        if (cards[i].offsetLeft <= left) active = i;
      }
      dots.forEach(function (d, idx) {
        d.classList.toggle('is-active', idx === active);
      });
    }

    function stop() {
      if (timer) { clearInterval(timer); timer = null; }
    }

    function start() {
      if (!autoplay) return;
      stop();
      timer = setInterval(function () {
        var maxLeft = track.scrollWidth - track.clientWidth;
        if (track.scrollLeft >= maxLeft - 4) {
          track.scrollTo({ left: 0, behavior: 'smooth' });
        } else {
          scrollBy(1);
        }
      }, delay);
    }

    if (prev) prev.addEventListener('click', function () { stop(); scrollBy(-1); });
    if (next) next.addEventListener('click', function () { stop(); scrollBy(1); });
    dots.forEach(function (dot) {
      dot.addEventListener('click', function () {
        stop();
        goTo(parseInt(dot.getAttribute('data-slider-dot'), 10) || 0);
      });
    });

    track.addEventListener('scroll', debounce(updateDots, 60), { passive: true });

    if (autoplay) {
      track.addEventListener('pointerenter', stop);
      track.addEventListener('pointerleave', start);
      track.addEventListener('touchstart', stop, { passive: true });
    }

    updateDots();
    start();
  }

  doc.querySelectorAll('[data-testimonial-slider]').forEach(initTestimonialSlider);

  // Re-init when the section is re-rendered in the Shopify theme editor.
  if ('MutationObserver' in window) {
    var sliderObserver = new MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        mutation.addedNodes.forEach(function (node) {
          if (node.nodeType !== 1) return;
          if (node.matches && node.matches('[data-testimonial-slider]')) initTestimonialSlider(node);
          if (node.querySelectorAll) node.querySelectorAll('[data-testimonial-slider]').forEach(initTestimonialSlider);
          if (node.matches && node.matches('[data-hero-slider]')) initHeroSlider(node);
          if (node.querySelectorAll) node.querySelectorAll('[data-hero-slider]').forEach(initHeroSlider);
        });
      });
    });
    sliderObserver.observe(doc.body, { childList: true, subtree: true });
  }

  /* ------------------------------------------------------------------ */
  /* Hero banner slideshow                                               */
  /* ------------------------------------------------------------------ */
  function initHeroSlider(track) {
    if (!track || track.dataset.heroInit) return;
    track.dataset.heroInit = 'true';

    var wrap = track.closest('.hero');
    if (!wrap) return;
    var slides = Array.prototype.slice.call(track.querySelectorAll('[data-hero-slide]'));
    if (slides.length < 2) return;

    var prev = wrap.querySelector('[data-hero-prev]');
    var next = wrap.querySelector('[data-hero-next]');
    var dots = Array.prototype.slice.call(wrap.querySelectorAll('[data-hero-dot]'));
    var autoplay = track.getAttribute('data-autoplay') === 'true';
    var delay = parseInt(track.getAttribute('data-delay'), 10) || 5000;
    var index = 0;
    var timer = null;
    var hovering = false;

    function render() {
      slides.forEach(function (slide, i) {
        slide.classList.toggle('is-active', i === index);
        slide.setAttribute('aria-hidden', i === index ? 'false' : 'true');
      });
      dots.forEach(function (d, i) {
        d.classList.toggle('is-active', i === index);
      });
    }

    function goTo(i) {
      index = (i + slides.length) % slides.length;
      render();
    }

    function stop() {
      if (timer) { clearInterval(timer); timer = null; }
    }

    function start() {
      if (!autoplay || hovering) return;
      stop();
      timer = setInterval(function () { goTo(index + 1); }, delay);
    }

    if (prev) prev.addEventListener('click', function () { goTo(index - 1); start(); });
    if (next) next.addEventListener('click', function () { goTo(index + 1); start(); });
    dots.forEach(function (d, i) {
      d.addEventListener('click', function () { goTo(i); start(); });
    });

    // Touch swipe
    var startX = null;
    track.addEventListener('touchstart', function (e) {
      startX = e.touches[0].clientX;
      stop();
    }, { passive: true });
    track.addEventListener('touchend', function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 40) goTo(dx < 0 ? index + 1 : index - 1);
      startX = null;
      start();
    }, { passive: true });

    // Pause on hover
    wrap.addEventListener('mouseenter', function () { hovering = true; stop(); });
    wrap.addEventListener('mouseleave', function () { hovering = false; start(); });

    render();
    start();
  }

  doc.querySelectorAll('[data-hero-slider]').forEach(initHeroSlider);

  /* ------------------------------------------------------------------ */
  /* Product gallery: click a thumbnail to feature it                    */
  /* ------------------------------------------------------------------ */
  doc.addEventListener('click', function (e) {
    var thumb = e.target.closest('[data-thumb]');
    if (!thumb) return;
    var gallery = thumb.closest('[data-product-gallery]');
    if (!gallery) return;
    var mediaId = thumb.getAttribute('data-media-id');
    if (!mediaId) return;

    gallery.querySelectorAll('[data-thumb]').forEach(function (t) {
      var active = t === thumb;
      t.classList.toggle('is-active', active);
      if (active) {
        t.setAttribute('aria-current', 'true');
      } else {
        t.removeAttribute('aria-current');
      }
    });

    gallery.querySelectorAll('[data-feature-item]').forEach(function (item) {
      item.classList.toggle('is-active', item.getAttribute('data-media-id') === mediaId);
    });
  });

  /* ------------------------------------------------------------------ */
  /* Recover password toggle                                             */
  /* ------------------------------------------------------------------ */
  doc.addEventListener('click', function (e) {
    var open = e.target.closest('[data-recover-toggle]');
    if (open) {
      var recover = doc.getElementById('recover');
      if (recover) {
        recover.hidden = false;
        var loginForm = doc.querySelector('form[action*="/account/login"]');
        if (loginForm && loginForm.id !== 'recover') loginForm.hidden = true;
        var firstInput = recover.querySelector('input');
        if (firstInput) firstInput.focus();
      }
      return;
    }
    var closeBtn = e.target.closest('[data-recover-close]');
    if (closeBtn) {
      var r = doc.getElementById('recover');
      if (r) r.hidden = true;
      var lf = doc.querySelector('form[action*="/account/login"]');
      if (lf && lf.id !== 'recover') lf.hidden = false;
    }
  });
})();
