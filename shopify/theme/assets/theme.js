/* Hearth theme · Snug & Co. */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  function formatMoney(cents, format = (window.theme && window.theme.moneyFormat) || '${{amount}}') {
    const value = Number(cents) / 100;
    const fmt = (n, dec, thou = ',', dot = '.') => {
      const [i, d] = n.toFixed(dec).split('.');
      return i.replace(/\B(?=(\d{3})+(?!\d))/g, thou) + (d ? dot + d : '');
    };
    return format.replace(/\{\{\s*(\w+)\s*\}\}/, (_, key) => ({
      amount: fmt(value, 2),
      amount_no_decimals: fmt(value, 0),
      amount_with_comma_separator: fmt(value, 2, '.', ','),
      amount_no_decimals_with_comma_separator: fmt(value, 0, '.', ','),
    }[key] || fmt(value, 2)));
  }

  /* Announcement rotator */
  $$('[data-rotator]').forEach((bar) => {
    const msgs = $$('.announce__msg', bar);
    if (msgs.length < 2) return;
    let i = 0;
    setInterval(() => {
      msgs[i].classList.remove('is-active');
      i = (i + 1) % msgs.length;
      msgs[i].classList.add('is-active');
    }, 4500);
  });

  /* Mobile menu */
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-menu-toggle]');
    if (!btn) return;
    const menu = document.getElementById(btn.getAttribute('aria-controls'));
    const open = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', String(!open));
    menu.hidden = open;
  });

  /* Cart drawer */
  const drawer = $('#CartDrawer');
  let lastFocus = null;
  const openDrawer = () => {
    if (!drawer) return;
    lastFocus = document.activeElement;
    drawer.classList.add('is-open');
    drawer.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    const close = $('[data-drawer-close].icon-btn', drawer);
    if (close) close.focus();
  };
  const closeDrawer = () => {
    if (!drawer) return;
    drawer.classList.remove('is-open');
    drawer.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    if (lastFocus) lastFocus.focus();
  };
  document.addEventListener('click', (e) => {
    if (e.target.closest('[data-cart-open]') && drawer) { e.preventDefault(); openDrawer(); }
    if (e.target.closest('[data-drawer-close]')) closeDrawer();
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeDrawer(); });

  async function refreshCart() {
    const [html, cart] = await Promise.all([
      fetch(`${window.theme.routes.cart_url}?section_id=cart-drawer`).then((r) => r.text()),
      fetch(`${window.theme.routes.cart_url}.js`).then((r) => r.json()),
    ]);
    const doc = new DOMParser().parseFromString(html, 'text/html');
    const inner = doc.querySelector('.shopify-section') || doc.body;
    const body = $('[data-cart-body]');
    if (body) body.innerHTML = inner.innerHTML;
    $$('[data-cart-count]').forEach((el) => {
      el.textContent = cart.item_count;
      el.classList.toggle('is-empty', cart.item_count === 0);
    });
    return cart;
  }

  /* Ajax add to cart */
  document.addEventListener('submit', async (e) => {
    const form = e.target.closest('[data-ajax-add]');
    if (!form || !drawer) return;
    e.preventDefault();
    const buttons = $$(`[type="submit"], [form="${form.id}"][type="submit"]`, document).filter((b) => b.form === form);
    buttons.forEach((b) => b.setAttribute('aria-busy', 'true'));
    try {
      const res = await fetch(`${window.theme.routes.cart_add_url}.js`, {
        method: 'POST',
        headers: { Accept: 'application/json' },
        body: new FormData(form),
      });
      const data = await res.json();
      if (!res.ok) { alert(data.description || data.message || 'Could not add to bag.'); return; }
      await refreshCart();
      openDrawer();
    } catch (err) {
      form.submit();
    } finally {
      buttons.forEach((b) => b.removeAttribute('aria-busy'));
    }
  });

  /* Cart quantity buttons in drawer */
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-qty-change]');
    if (!btn) return;
    const line = Number(btn.closest('[data-line]').dataset.line);
    btn.disabled = true;
    await fetch(`${window.theme.routes.cart_change_url}.js`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ line, quantity: Number(btn.dataset.qtyChange) }),
    });
    await refreshCart();
  });

  /* Product page */
  $$('[data-product-section]').forEach((section) => {
    const jsonEl = $('[data-product-json]', section);
    if (!jsonEl) return;
    const product = JSON.parse(jsonEl.textContent);
    const idInput = $('[data-variant-id]', section);
    const addButtons = $$('[data-add-button]', section);
    const priceWrap = $('[data-price-wrap] [data-price]', section);
    const stickyPrice = $('[data-sticky-price]', section);
    const track = $('[data-gallery-track]', section);
    const dots = $$('.gallery__dots span', section);

    const selected = () => {
      const values = [];
      $$('[data-variant-picker] input:checked', section).forEach((i) => { values[Number(i.dataset.optionIndex)] = i.value; });
      return values;
    };

    const markUnavailable = (values) => {
      $$('[data-variant-picker] input', section).forEach((input) => {
        const idx = Number(input.dataset.optionIndex);
        const test = values.slice(); test[idx] = input.value;
        const v = product.variants.find((x) => x.options.every((o, i) => o === test[i]));
        input.classList.toggle('is-unavailable', !v || !v.available);
      });
    };

    const update = () => {
      const values = selected();
      $$('[data-option-label]', section).forEach((el) => { el.textContent = values[Number(el.dataset.optionLabel)] || ''; });
      const variant = product.variants.find((v) => v.options.every((o, i) => o === values[i]));
      markUnavailable(values);
      addButtons.forEach((b) => {
        b.disabled = !variant || !variant.available;
        b.textContent = !variant ? 'Unavailable' : variant.available ? 'Add to bag' : 'Sold out';
      });
      if (!variant) return;
      idInput.value = variant.id;
      const url = new URL(window.location.href);
      url.searchParams.set('variant', variant.id);
      window.history.replaceState({}, '', url.toString());
      if (priceWrap) {
        const onSale = variant.compare_at_price > variant.price;
        priceWrap.classList.toggle('price--sale', onSale);
        priceWrap.innerHTML = `<span class="price__current">${formatMoney(variant.price)}</span>` +
          (onSale ? `<s class="price__compare">${formatMoney(variant.compare_at_price)}</s><span class="price__badge">Save ${formatMoney(variant.compare_at_price - variant.price).replace(/\.00(?!\d)/, '')}</span>` : '');
      }
      if (stickyPrice) stickyPrice.textContent = formatMoney(variant.price);
      if (variant.featured_media && track) {
        const slide = $(`[data-media-id="${variant.featured_media.id}"]`, track);
        if (slide) {
          if (window.matchMedia('(min-width: 990px)').matches) {
            track.prepend(slide);
          } else {
            track.scrollTo({ left: slide.offsetLeft - track.offsetLeft, behavior: 'smooth' });
          }
        }
      }
    };
    section.addEventListener('change', (e) => { if (e.target.matches('[data-variant-picker] input')) update(); });
    if ($('[data-variant-picker]', section)) markUnavailable(selected());

    section.addEventListener('click', (e) => {
      const step = e.target.closest('[data-qty-step]');
      if (!step) return;
      const input = $('[data-qty-input]', section);
      input.value = Math.max(1, Number(input.value || 1) + Number(step.dataset.qtyStep));
    });

    if (track && dots.length) {
      track.addEventListener('scroll', () => {
        const i = Math.round(track.scrollLeft / track.clientWidth);
        dots.forEach((d, n) => d.classList.toggle('is-active', n === i));
      }, { passive: true });
    }

    const sticky = $('[data-sticky-atc]', section);
    const buy = $('.buy', section);
    if (sticky && buy && 'IntersectionObserver' in window) {
      new IntersectionObserver(([entry]) => {
        sticky.hidden = entry.isIntersecting || entry.boundingClientRect.top > 0;
      }).observe(buy);
    }
  });

  /* Product recommendations */
  $$('[data-recommendations]').forEach(async (el) => {
    if (el.children.length) return;
    try {
      const html = await fetch(el.dataset.url).then((r) => r.text());
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const fresh = doc.querySelector('[data-recommendations]');
      if (fresh && fresh.innerHTML.trim()) el.innerHTML = fresh.innerHTML;
      else el.remove();
    } catch (err) { el.remove(); }
  });

  /* Collection sort */
  document.addEventListener('change', (e) => {
    if (!e.target.matches('[data-sort]')) return;
    const url = new URL(window.location.href);
    url.searchParams.set('sort_by', e.target.value);
    window.location.href = url.toString();
  });
})();
