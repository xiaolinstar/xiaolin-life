(function () {
  "use strict";
  const directory = document.getElementById("article-directory");
  if (!directory || !window.SiteSearch) return;
  const query = document.getElementById("directory-query");
  let section = "";
  let topic = "";
  const topics = Array.from(directory.querySelectorAll("[data-topic-filter]"));
  const topicGroups = Array.from(directory.querySelectorAll("[data-topics-section]"));
  const status = document.getElementById("directory-status");
  const heading = document.getElementById("directory-heading");
  const retry = document.getElementById("directory-retry");
  const more = document.getElementById("directory-more");
  const empty = document.getElementById("directory-empty");
  const rows = Array.from(directory.querySelectorAll("[data-article-url]"));
  const channels = Array.from(directory.querySelectorAll("[data-section-filter]"));
  const pageSize = 12;
  let generation = 0;
  let composing = false;
  let visibleCount = pageSize;
  let currentRows = rows;

  function render() {
    const visible = new Set(currentRows.slice(0, visibleCount));
    rows.forEach((row) => { row.hidden = !visible.has(row); });
    more.hidden = visibleCount >= currentRows.length;
    empty.hidden = currentRows.length > 0;
    status.textContent = currentRows.length
      ? `共 ${currentRows.length} 篇，已展示 ${Math.min(visibleCount, currentRows.length)} 篇`
      : "没有找到匹配的文章";
    const channel = channels.find((button) => button.dataset.sectionFilter === section);
    const selectedTopic = topics.find((button) => button.dataset.topicFilter === topic);
    const label = (button) => button.firstChild.textContent.trim();
    heading.textContent = query.value.trim() ? "搜索结果" : (selectedTopic ? label(selectedTopic) : label(channel));
    channels.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.sectionFilter === section)));
    topics.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.topicFilter === topic)));
    topicGroups.forEach((group) => { group.hidden = group.dataset.topicsSection !== section; });
    document.getElementById("directory-clear").hidden = !section && !query.value.trim();
  }

  async function filter() {
    const current = ++generation;
    const text = query.value;
    retry.hidden = true;
    let matching;
    if (window.SiteSearch.normalize(text)) {
      status.textContent = "正在查找文章…";
      try {
        const data = await window.SiteSearch.loadIndex(directory.dataset.indexUrl);
        if (current !== generation) return;
        matching = new Set(window.SiteSearch.find(data, text, section, window.Fuse).map((item) => item.permalink));
      } catch (_) {
        if (current !== generation) return;
        status.textContent = "搜索暂不可用，请重试或按栏目浏览。";
        retry.hidden = false;
        return;
      }
    }
    currentRows = rows.filter((row) => (!section || row.dataset.section === section)
      && (!topic || row.dataset.topic === topic)
      && (!matching || matching.has(row.dataset.articleUrl)));
    visibleCount = pageSize;
    render();
  }
  function reset() {
    query.value = "";
    section = "";
    topic = "";
    filter();
  }
  directory.querySelector("form").addEventListener("submit", (event) => event.preventDefault());
  query.addEventListener("compositionstart", () => { composing = true; });
  query.addEventListener("compositionend", () => { composing = false; filter(); });
  query.addEventListener("input", () => { if (!composing) filter(); });
  channels.forEach((button) => button.addEventListener("click", () => {
    section = button.dataset.sectionFilter;
    topic = "";
    filter();
  }));
  topics.forEach((button) => button.addEventListener("click", () => {
    section = button.dataset.section;
    topic = topic === button.dataset.topicFilter ? "" : button.dataset.topicFilter;
    filter();
  }));
  document.getElementById("directory-clear").addEventListener("click", reset);
  document.getElementById("directory-reset").addEventListener("click", reset);
  more.addEventListener("click", () => {
    const next = currentRows[visibleCount];
    visibleCount += pageSize;
    render();
    if (next) next.querySelector(".article-link--card a").focus();
  });
  retry.addEventListener("click", filter);
  render();
})();
