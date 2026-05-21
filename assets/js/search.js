"use strict";
(() => {
  // assets/js/search.ts
  var SearchApp = class {
    constructor() {
      this.modal = null;
      this.input = null;
      this.resultsContainer = null;
      this.pagefindLoaded = false;
      this.pagefindInstance = null;
      this.debounceTimer = null;
      this.init();
    }
    init() {
      document.addEventListener("DOMContentLoaded", () => {
        this.cacheElements();
        this.bindEvents();
        this.initPagefind();
      });
    }
    cacheElements() {
      this.modal = document.getElementById("search-modal");
      this.input = document.getElementById("search-input");
      this.resultsContainer = document.getElementById("search-results");
    }
    bindEvents() {
      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && this.modal && !this.modal.classList.contains("hidden")) {
          this.close();
        }
        if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
          e.preventDefault();
          this.toggle();
        }
      });
      if (this.modal) {
        this.modal.addEventListener("click", (e) => {
          if (e.target === this.modal) {
            this.close();
          }
        });
      }
      if (this.input) {
        this.input.addEventListener("input", (e) => {
          const query = e.target.value;
          this.debounceSearch(query);
        });
      }
    }
    toggle() {
      if (!this.modal || !this.input) return;
      if (this.modal.classList.contains("hidden")) {
        this.modal.classList.remove("hidden");
        this.input.focus();
        document.body.style.overflow = "hidden";
      } else {
        this.close();
      }
    }
    close() {
      if (!this.modal || !this.input) return;
      this.modal.classList.add("hidden");
      this.input.value = "";
      if (this.resultsContainer) {
        this.resultsContainer.innerHTML = "";
      }
      document.body.style.overflow = "";
    }
    async initPagefind() {
      if (this.pagefindLoaded) return;
      try {
        const script = document.createElement("script");
        script.src = "/pagefind/pagefind.js";
        script.onload = async () => {
          if (window.pagefind) {
            this.pagefindInstance = await window.pagefind();
            this.pagefindLoaded = true;
          }
        };
        script.onerror = () => {
          console.error("Failed to load Pagefind");
        };
        document.body.appendChild(script);
      } catch (e) {
        console.error("Failed to initialize Pagefind:", e);
      }
    }
    debounceSearch(query, delay = 300) {
      if (this.debounceTimer) {
        clearTimeout(this.debounceTimer);
      }
      this.debounceTimer = setTimeout(() => {
        this.performSearch(query);
      }, delay);
    }
    async performSearch(query) {
      if (!this.resultsContainer) return;
      if (!query) {
        this.resultsContainer.innerHTML = "";
        return;
      }
      if (!this.pagefindLoaded) {
        await this.initPagefind();
      }
      if (!this.pagefindInstance) {
        this.resultsContainer.innerHTML = '<div class="search-results__empty">\u641C\u7D22\u529F\u80FD\u52A0\u8F7D\u4E2D...</div>';
        return;
      }
      try {
        const search = await this.pagefindInstance.search(query);
        if (!search.results.length) {
          this.resultsContainer.innerHTML = '<div class="search-results__empty">\u672A\u627E\u5230\u76F8\u5173\u5185\u5BB9</div>';
          return;
        }
        let html = "";
        for (const result of search.results) {
          const data = await result.data();
          html += `
          <div class="search-result" onclick="window.location.href='${data.url}'">
            <div class="search-result__title">${data.meta.title || "\u65E0\u6807\u9898"}</div>
            <div class="search-result__url">${data.url}</div>
            <div class="search-result__excerpt">${data.excerpt}</div>
          </div>
        `;
        }
        this.resultsContainer.innerHTML = html;
      } catch (e) {
        console.error("Search error:", e);
        this.resultsContainer.innerHTML = '<div class="search-results__empty">\u641C\u7D22\u51FA\u9519\uFF0C\u8BF7\u91CD\u8BD5</div>';
      }
    }
  };
  window.searchApp = new SearchApp();
})();
