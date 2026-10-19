/* 项目级覆盖：保留 Blowfish 搜索入口，补充多词匹配、栏目及加载状态。 */
(function (root) {
  "use strict";

  const prepared = new WeakMap();
  function normalize(value) {
    return String(value || "").normalize("NFKC").toLowerCase().replace(/\s+/g, " ").trim();
  }
  const compact = (value) => normalize(value).replace(/\s/g, "");

  function prepare(data) {
    if (prepared.has(data)) return prepared.get(data);
    const entries = data.map((item) => ({
      item,
      title: compact(item.title),
      keywords: compact((item.keywords || []).join(" ")),
      trail: compact(item.breadcrumb || item.section),
      summary: compact(item.summary),
      body: compact(item.content),
    }));
    prepared.set(data, entries);
    return entries;
  }

  function rank(entries, terms, phrase) {
    return entries.map((entry) => {
      let score = 0;
      for (const term of terms) {
        if (entry.title === term) score += 140;
        else if (entry.title.includes(term)) score += 65;
        else if (entry.keywords.includes(term)) score += 45;
        else if (entry.trail.includes(term)) score += 35;
        else if (entry.summary.includes(term)) score += 15;
        else if (entry.body.includes(term)) score += 2;
        else return null;
      }
      if (entry.title === phrase) score += 200;
      else if (entry.title.includes(phrase)) score += 80;
      return { item: entry.item, score };
    }).filter(Boolean).sort((a, b) => b.score - a.score || a.item.title.localeCompare(b.item.title, "zh-CN"));
  }

  function find(data, query, section, FuseClass) {
    const text = normalize(query).slice(0, 160);
    const entries = prepare(data).filter((entry) => !section || entry.item.sectionId === section);
    if (!text) return entries.map((entry) => entry.item);
    let terms = text.split(" ").map(compact).filter(Boolean);
    let results = rank(entries, terms, compact(text));
    // 连写的中文品牌/名称也参与分词；正文偶然出现完整短语不应挡住其他相关标题。
    if (/\p{Script=Han}/u.test(text) && typeof Intl.Segmenter === "function") {
      const segments = Array.from(new Intl.Segmenter("zh-CN", { granularity: "word" }).segment(text))
        .filter((part) => part.isWordLike).map((part) => compact(part.segment));
      if (segments.length > terms.length) {
        const merged = new Map(results.map((result) => [result.item.permalink, result]));
        for (const result of rank(entries, segments, compact(text))) {
          const previous = merged.get(result.item.permalink);
          if (!previous || previous.score < result.score) merged.set(result.item.permalink, result);
        }
        results = Array.from(merged.values()).sort((a, b) => b.score - a.score || a.item.title.localeCompare(b.item.title, "zh-CN"));
      }
    }
    if (results.length || !FuseClass) return results.map((result) => result.item);
    // 容错仅用于没有直接命中的拉丁文字；不放宽中文营养数字的匹配。
    if (!/^[a-z][a-z -]{2,79}$/.test(text)) return [];
    const fuzzy = new FuseClass(entries.map((entry) => entry.item), {
      ignoreLocation: true, threshold: 0.28, minMatchCharLength: 3,
      keys: [{ name: "title", weight: 0.7 }, { name: "keywords", weight: 0.3 }],
    });
    return fuzzy.search(text).map((result) => result.item);
  }

  let indexPromise;
  function loadIndex(url) {
    if (!indexPromise) {
      indexPromise = fetch(url).then((response) => {
        if (!response.ok) throw new Error("Search index unavailable");
        return response.json();
      }).then((data) => {
        if (!Array.isArray(data)) throw new Error("Invalid search index");
        prepare(data);
        return data;
      }).catch((error) => {
        indexPromise = undefined;
        throw error;
      });
    }
    return indexPromise;
  }

  const api = { normalize, find, loadIndex };
  if (typeof module === "object" && module.exports) module.exports = api;
  root.SiteSearch = api;
  if (typeof document === "undefined") return;

  const wrapper = document.getElementById("search-wrapper");
  if (!wrapper) return;
  const modal = document.getElementById("search-modal");
  const input = document.getElementById("search-query");
  const output = document.getElementById("search-results");
  const section = document.getElementById("search-section");
  const status = document.getElementById("search-status");
  const retry = document.getElementById("search-retry");
  const shortcutHint = document.getElementById("search-shortcut-hint");
  if (shortcutHint && !/Mac|iPhone|iPad/.test(navigator.platform)) shortcutHint.textContent = "Ctrl K";
  const indexUrl = wrapper.dataset.url.replace(/\/?$/, "/") + "index.json";
  let visible = false;
  let returnFocus;
  let oldOverflow;
  let generation = 0;
  let composing = false;

  function element(tag, className, text) {
    const node = document.createElement(tag);
    node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  function render(items) {
    output.replaceChildren();
    for (const item of items.slice(0, 60)) {
      const li = element("li", "mb-2");
      const link = element("a", "search-result");
      link.href = item.permalink;
      link.append(element("div", "text-lg font-bold", item.title));
      link.append(element("div", "text-sm text-neutral-500", [item.breadcrumb || item.section, item.date].filter(Boolean).join(" · ")));
      link.append(element("div", "text-sm", String(item.summary || "").slice(0, 150)));
      li.append(link);
      output.append(li);
    }
  }

  async function update() {
    const current = ++generation;
    const query = input.value;
    document.getElementById("search-suggestions").hidden = !!normalize(query);
    retry.hidden = true;
    if (!normalize(query)) {
      output.replaceChildren();
      status.textContent = "输入关键词；多个关键词用空格分开，也支持标签和常用别称。";
      return;
    }
    output.replaceChildren();
    status.textContent = "正在搜索…";
    try {
      const data = await loadIndex(indexUrl);
      if (current !== generation || !visible) return;
      const items = find(data, query, section.value, root.Fuse);
      render(items);
      status.textContent = items.length
        ? `找到 ${items.length} 篇文章${items.length > 60 ? "，显示前 60 篇，请按栏目缩小范围" : ""}`
        : "没有找到匹配文章。可换用标题中的词、用空格分开关键词，或浏览文章目录。草稿不在公开搜索中。";
    } catch (_) {
      if (current !== generation || !visible) return;
      status.textContent = "搜索索引加载失败，请重试或通过文章目录浏览。";
      retry.hidden = false;
    }
  }

  function show() {
    if (visible) return;
    returnFocus = document.activeElement;
    oldOverflow = document.body.style.overflow;
    visible = true;
    wrapper.style.visibility = "visible";
    wrapper.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    input.focus();
    update();
  }

  function hide() {
    if (!visible) return;
    visible = false;
    generation += 1;
    wrapper.style.visibility = "hidden";
    wrapper.setAttribute("aria-hidden", "true");
    document.body.style.overflow = oldOverflow;
    input.value = "";
    output.replaceChildren();
    if (returnFocus && returnFocus.isConnected) returnFocus.focus();
  }

  ["search-button", "search-button-mobile"].forEach((id) => {
    const button = document.getElementById(id);
    if (button) button.addEventListener("click", show);
  });
  document.getElementById("close-search-button").addEventListener("click", hide);
  wrapper.addEventListener("click", (event) => { if (event.target === wrapper) hide(); });
  modal.addEventListener("submit", (event) => event.preventDefault());
  input.addEventListener("compositionstart", () => { composing = true; });
  input.addEventListener("compositionend", () => { composing = false; update(); });
  input.addEventListener("input", () => { if (!composing) update(); });
  section.addEventListener("change", update);
  retry.addEventListener("click", update);
  document.querySelectorAll("[data-search-suggestion]").forEach((button) => {
    button.addEventListener("click", () => { input.value = button.dataset.searchSuggestion; input.focus(); update(); });
  });
  document.addEventListener("keydown", (event) => {
    if (event.isComposing) return;
    if ((event.metaKey || event.ctrlKey) && !event.altKey && event.key.toLowerCase() === "k") {
      event.preventDefault();
      if (visible) hide(); else show();
      return;
    }
    const active = document.activeElement;
    const typing = active && (active.matches("input, textarea, select") || active.isContentEditable);
    if (event.key === "/" && !visible && !typing) { event.preventDefault(); show(); }
    if (!visible || event.isComposing) return;
    if (event.key === "Escape") { event.preventDefault(); hide(); }
    const links = Array.from(output.querySelectorAll("a"));
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      if (active !== input && !links.includes(active)) return;
      event.preventDefault();
      const index = links.indexOf(active);
      const target = event.key === "ArrowDown" ? links[Math.min(index + 1, links.length - 1)] : (index <= 0 ? input : links[index - 1]);
      if (target) target.focus();
    }
    if (event.key === "Enter" && active === input && links.length) { event.preventDefault(); links[0].click(); }
    if (event.key === "Tab") {
      const focusable = Array.from(modal.querySelectorAll("input, select, button, a[href]"))
        .filter((node) => !node.hidden && !node.disabled && node.getClientRects().length > 0);
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (event.shiftKey && active === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && active === last) { event.preventDefault(); first.focus(); }
    }
  });
})(typeof window === "undefined" ? globalThis : window);
