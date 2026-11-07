(() => {
  function init() {
    const labelsNode = document.getElementById('screen-toc-labels');
    if (!labelsNode) return;
    const labels = JSON.parse(labelsNode.textContent);
    const tocs = [...document.querySelectorAll('#TableOfContents, #TableOfContentsMobile')];

    tocs.forEach((toc) => {
      // “影评正文”只负责分组，具体论点作为目录的主要章节。
      const root = toc.querySelector(':scope > ul');
      if (!root) return;
      [...root.children].forEach((item) => {
        const link = item.querySelector(':scope > a');
        const children = item.querySelector(':scope > ul');
        if (link?.textContent.trim() === '影评正文' && children) {
          item.replaceWith(...children.children);
        }
      });
      toc.querySelectorAll('a[href^="#"]').forEach((link) => {
        const title = link.textContent.trim();
        link.textContent = labels[title] || title;
        link.title = title;
      });
      toc.classList.add('screen-toc');
    });

    const desktop = document.getElementById('TableOfContents');
    if (!desktop) return;
    const sync = () => {
      const active = desktop.querySelector('a.active');
      const root = desktop.querySelector(':scope > ul');
      if (!root) return;
      [...root.children].forEach((item) => {
        const current = Boolean(active && item.contains(active));
        if (item.classList.contains('is-current') !== current) {
          item.classList.toggle('is-current', current);
        }
      });
    };
    // 复用主题的阅读位置高亮，只同步当前章节的展开状态。
    const observer = new MutationObserver((records) => {
      if (records.some((record) => record.target.tagName === 'A')) sync();
    });
    observer.observe(desktop, { attributes: true, attributeFilter: ['class'], subtree: true });
    sync();
  }
  document.readyState === 'loading'
    ? document.addEventListener('DOMContentLoaded', init)
    : init();
})();
