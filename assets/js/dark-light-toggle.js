// Dark/Light Theme Toggle
function toggleTheme() {
  const html = document.documentElement;
  const button = document.querySelector('.theme-toggle');
  const currentMode = html.getAttribute('data-mode');
  
  if (currentMode === 'light') {
    html.setAttribute('data-mode', 'dark');
    button.textContent = '☀️';
    localStorage.setItem('theme', 'dark');
  } else {
    html.setAttribute('data-mode', 'light');
    button.textContent = '🌙';
    localStorage.setItem('theme', 'light');
  }
}

// Load saved theme on page load
(function() {
  const savedTheme = localStorage.getItem('theme');
  const html = document.documentElement;
  const button = document.querySelector('.theme-toggle');
  
  if (savedTheme) {
    html.setAttribute('data-mode', savedTheme);
    if (savedTheme === 'dark') {
      button.textContent = '☀️';
    } else {
      button.textContent = '🌙';
    }
  } else {
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      html.setAttribute('data-mode', 'dark');
      button.textContent = '☀️';
    }
  }
})();
