(function () {
  "use strict";
  const dialog = document.getElementById("section-tree-dialog");
  const trigger = document.querySelector(".section-tree-trigger");
  if (!dialog || !trigger) return;
  const wideScreen = window.matchMedia("(min-width: 1400px)");
  function revealCurrent(container) {
    container = container.querySelector(".section-tree-list");
    const current = container.querySelector('[aria-current="page"]');
    if (!current) return;
    const box = container.getBoundingClientRect();
    const item = current.getBoundingClientRect();
    container.scrollTop += item.top - box.top - container.clientHeight / 2;
  }
  if (wideScreen.matches) revealCurrent(document.querySelector(".section-tree"));
  trigger.addEventListener("click", () => {
    dialog.showModal();
    document.body.classList.add("section-tree-dialog-open");
    revealCurrent(dialog);
  });
  dialog.querySelector("[data-close-section-tree]").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) {
      const bounds = dialog.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
    }
  });
  dialog.addEventListener("close", () => {
    document.body.classList.remove("section-tree-dialog-open");
    if (!wideScreen.matches) trigger.focus();
  });
  wideScreen.addEventListener("change", () => {
    if (dialog.open) dialog.close();
    if (wideScreen.matches) revealCurrent(document.querySelector(".section-tree"));
  });
})();
