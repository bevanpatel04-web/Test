(function () {
  const C = window.STORE_CONFIG, P = window.PRODUCTS, B = window.BUNDLES;
  const $ = (s) => document.querySelector(s);
  const money = (n) => new Intl.NumberFormat("en-US", { style: "currency", currency: C.currency }).format(n);
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const byId = Object.fromEntries(P.map((p) => [p.id, p]));

  // ---- tracking (only loads when an ID is set) ----
  function track(event, data) {
    if (window.fbq) window.fbq("track", event, data);
    if (window.ttq) window.ttq.track(event === "InitiateCheckout" ? "InitiateCheckout" : event, data);
  }
  if (C.metaPixelId) {
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq("init", C.metaPixelId); fbq("track", "PageView");
  }
  if (C.tiktokPixelId) {
    !function(w,d,t){w.TiktokAnalyticsObject=t;var ttq=w[t]=w[t]||[];ttq.methods=["page","track","identify"];ttq.setAndDefer=function(t,e){t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}};for(var i=0;i<ttq.methods.length;i++)ttq.setAndDefer(ttq,ttq.methods[i]);ttq.load=function(e){var s=d.createElement("script");s.async=!0;s.src="https://analytics.tiktok.com/i18n/pixel/events.js?sdkid="+e+"&lib="+t;var f=d.getElementsByTagName("script")[0];f.parentNode.insertBefore(s,f)};ttq.load(C.tiktokPixelId);ttq.page()}(window,document,"ttq");
  }

  // ---- text from config ----
  document.title = `${C.name} · ${C.tagline}`;
  document.querySelectorAll("[data-store-name]").forEach((el) => (el.textContent = C.name));
  $("#tagline").textContent = C.tagline;
  $("#promo").textContent = `${C.freeShippingNote} · ${C.promo.text}`;
  $("#ship").textContent = C.shippingTime;
  document.querySelectorAll("[data-support]").forEach((el) => { el.textContent = C.supportEmail; el.href = "mailto:" + C.supportEmail; });

  function buyButton(item, label) {
    if (!item.checkoutUrl) return `<button class="buy" disabled>Coming soon</button>`;
    return `<a class="buy" href="${esc(item.checkoutUrl)}" data-id="${esc(item.id)}" data-price="${item.price}">${label}</a>`;
  }
  const media = (p) => p.image ? `<img src="${esc(p.image)}" alt="${esc(p.name)}" loading="lazy">` : `<span aria-hidden="true">${p.emoji}</span>`;
  const off = (p) => Math.round((1 - p.price / p.compareAt) * 100);

  // ---- products (supports ?p=<id> to feature one product from an ad) ----
  const featured = new URLSearchParams(location.search).get("p");
  const ordered = featured && byId[featured] ? [byId[featured], ...P.filter((p) => p.id !== featured)] : P;
  $("#grid").innerHTML = ordered.map((p) => `
    <article class="card${p.id === featured ? " featured" : ""}" id="${esc(p.id)}">
      <div class="media">${media(p)}<span class="badge">-${off(p)}%</span></div>
      <div class="body">
        <h3>${esc(p.name)}</h3>
        <p class="hook">${esc(p.hook)}</p>
        <ul>${p.bullets.map((b) => `<li>${esc(b)}</li>`).join("")}</ul>
        <div class="price"><strong>${money(p.price)}</strong> <s>${money(p.compareAt)}</s></div>
        ${buyButton(p, "Buy now")}
      </div>
    </article>`).join("");

  $("#bundles").innerHTML = B.map((b) => {
    const parts = b.includes.map((id) => byId[id]);
    const value = parts.reduce((s, p) => s + p.price, 0);
    return `<article class="card bundle">
      <div class="media small">${parts.map((p) => `<span aria-hidden="true">${p.emoji}</span>`).join("")}</div>
      <div class="body">
        <h3>${esc(b.name)}</h3>
        <p class="hook">${parts.map((p) => esc(p.name)).join(" + ")}</p>
        <div class="price"><strong>${money(b.price)}</strong> <s>${money(value)}</s></div>
        <p class="fine">${esc(b.note)}</p>
        ${buyButton(b, "Get the bundle")}
      </div></article>`;
  }).join("");

  document.addEventListener("click", (e) => {
    const a = e.target.closest("a.buy");
    if (a) track("InitiateCheckout", { content_ids: [a.dataset.id], value: Number(a.dataset.price), currency: C.currency });
  });
  if (featured && byId[featured]) {
    track("ViewContent", { content_ids: [featured], value: byId[featured].price, currency: C.currency });
    document.getElementById(featured).scrollIntoView({ block: "center" });
  }
})();
