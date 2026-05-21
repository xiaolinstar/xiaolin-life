interface SearchResult {
  url: string;
  meta: {
    title?: string;
  };
  excerpt: string;
}

interface PagefindInstance {
  search(query: string): Promise<{
    results: Array<{
      data(): Promise<SearchResult>;
    }>;
  }>;
}

declare global {
  interface Window {
    pagefind: () => Promise<PagefindInstance>;
  }
}

class SearchApp {
  private modal: HTMLElement | null = null;
  private input: HTMLInputElement | null = null;
  private resultsContainer: HTMLElement | null = null;
  private pagefindLoaded: boolean = false;
  private pagefindInstance: PagefindInstance | null = null;
  private debounceTimer: ReturnType<typeof setTimeout> | null = null;

  constructor() {
    this.init();
  }

  private init(): void {
    document.addEventListener('DOMContentLoaded', () => {
      this.cacheElements();
      this.bindEvents();
      this.initPagefind();
    });
  }

  private cacheElements(): void {
    this.modal = document.getElementById('search-modal');
    this.input = document.getElementById('search-input') as HTMLInputElement;
    this.resultsContainer = document.getElementById('search-results');
  }

  private bindEvents(): void {
    document.addEventListener('keydown', (e: KeyboardEvent) => {
      if (e.key === 'Escape' && this.modal && !this.modal.classList.contains('hidden')) {
        this.close();
      }
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        this.toggle();
      }
    });

    if (this.modal) {
      this.modal.addEventListener('click', (e: Event) => {
        if (e.target === this.modal) {
          this.close();
        }
      });
    }

    if (this.input) {
      this.input.addEventListener('input', (e: Event) => {
        const query = (e.target as HTMLInputElement).value;
        this.debounceSearch(query);
      });
    }
  }

  public toggle(): void {
    if (!this.modal || !this.input) return;

    if (this.modal.classList.contains('hidden')) {
      this.modal.classList.remove('hidden');
      this.input.focus();
      document.body.style.overflow = 'hidden';
    } else {
      this.close();
    }
  }

  public close(): void {
    if (!this.modal || !this.input) return;

    this.modal.classList.add('hidden');
    this.input.value = '';
    if (this.resultsContainer) {
      this.resultsContainer.innerHTML = '';
    }
    document.body.style.overflow = '';
  }

  private async initPagefind(): Promise<void> {
    if (this.pagefindLoaded) return;

    try {
      const script = document.createElement('script');
      script.src = '/pagefind/pagefind.js';
      script.onload = async () => {
        if (window.pagefind) {
          this.pagefindInstance = await window.pagefind();
          this.pagefindLoaded = true;
        }
      };
      script.onerror = () => {
        console.error('Failed to load Pagefind');
      };
      document.body.appendChild(script);
    } catch (e) {
      console.error('Failed to initialize Pagefind:', e);
    }
  }

  private debounceSearch(query: string, delay: number = 300): void {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }

    this.debounceTimer = setTimeout(() => {
      this.performSearch(query);
    }, delay);
  }

  private async performSearch(query: string): Promise<void> {
    if (!this.resultsContainer) return;

    if (!query) {
      this.resultsContainer.innerHTML = '';
      return;
    }

    if (!this.pagefindLoaded) {
      await this.initPagefind();
    }

    if (!this.pagefindInstance) {
      this.resultsContainer.innerHTML = '<div class="search-results__empty">搜索功能加载中...</div>';
      return;
    }

    try {
      const search = await this.pagefindInstance.search(query);

      if (!search.results.length) {
        this.resultsContainer.innerHTML = '<div class="search-results__empty">未找到相关内容</div>';
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
      this.resultsContainer.innerHTML = html;
    } catch (e) {
      console.error('Search error:', e);
      this.resultsContainer.innerHTML = '<div class="search-results__empty">搜索出错，请重试</div>';
    }
  }
}

(window as unknown as { searchApp: SearchApp }).searchApp = new SearchApp();

function toggleSearch(): void {
  (window as unknown as { searchApp: SearchApp }).searchApp.toggle();
}
