// Search Modal Toggle
function toggleSearch() {
  const modal = document.getElementById('search-modal');
  const input = document.getElementById('search-input');

  if (modal.classList.contains('hidden')) {
    modal.classList.remove('hidden');
    input.focus();
    document.body.style.overflow = 'hidden';
  } else {
    modal.classList.add('hidden');
    input.value = '';
    document.getElementById('search-results').innerHTML = '';
    document.body.style.overflow = '';
  }
}

// Close modal on escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    const modal = document.getElementById('search-modal');
    if (!modal.classList.contains('hidden')) {
      toggleSearch();
    }
  }
});

// Close modal on backdrop click
document.getElementById('search-modal').addEventListener('click', (e) => {
  if (e.target === document.getElementById('search-modal')) {
    toggleSearch();
  }
});

// Pagefind Search Integration
let pagefindLoaded = false;
let pagefindInstance = null;

async function initPagefind() {
  if (pagefindLoaded) return;
  try {
    const script = document.createElement('script');
    script.src = '/pagefind/pagefind.js';
    script.onload = async () => {
      if (window.pagefind) {
        pagefindInstance = await window.pagefind();
        pagefindLoaded = true;
      }
    };
    document.body.appendChild(script);
  } catch (e) {
    console.error('Failed to load Pagefind:', e);
  }
}

async function performSearch(query) {
  const resultsContainer = document.getElementById('search-results');
  if (!query) {
    resultsContainer.innerHTML = '';
    return;
  }

  if (!pagefindLoaded) {
    await initPagefind();
  }

  if (!pagefindInstance) {
    resultsContainer.innerHTML = '<div class="search-results__empty">搜索功能加载中...</div>';
    return;
  }

  const search = await pagefindInstance.search(query);
  if (!search.results.length) {
    resultsContainer.innerHTML = '<div class="search-results__empty">未找到相关内容</div>';
    return;
  }

  let html = '';
  for (const result of search.results) {
    const data = await result.data();
    html += `
      <div class="search-result" onclick="window.location.href='${data.url}'">
        <div class="search-result__title">${data.meta.title || '无标题'}</div>
        <div class="search-result__url">${data.url}</div>
        <div class="search-result__excerpt">${data.excerpt}</div>
      </div>
    `;
  }
  resultsContainer.innerHTML = html;
}

// Initialize search on page load
document.addEventListener('DOMContentLoaded', () => {
  initPagefind();
});

// Bind search input
document.getElementById('search-input').addEventListener('input', (e) => {
  performSearch(e.target.value);
});
