/* 首页 Vanta.js Birds 背景：透明画布叠加在极光渐变之上 */
(function () {
  function init() {
    if (!window.VANTA || !window.THREE) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var el = document.getElementById("home-vanta");
    if (!el) return;

    window.VANTA.BIRDS({
      el: el,
      THREE: window.THREE,
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.0,
      minWidth: 200.0,
      scale: 1.0,
      scaleMobile: 1.0,
      backgroundAlpha: 0.0,
      colorMode: "lerpGradient",
      color1: 0x3b82f6,
      color2: 0x8b5cf6,
      quantity: 3.0,
      birdSize: 1.4,
      wingSpan: 25.0,
      speedLimit: 4.0,
      separation: 60.0,
      alignment: 40.0,
      cohesion: 30.0
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
