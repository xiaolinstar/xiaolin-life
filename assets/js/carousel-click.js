// assets/js/carousel-click.js
// 补全 tw-elements FREE 2.0.0 carousel 缺失的 click handler。
//
// 背景：blowfish v2.104.0 依赖的 lib/tw-elements/index.min.js（FREE 2.0.0）
// 虽然定义了 Carousel 类（cycle / next / prev / to / getOrCreateInstance 等），
// 但完全没有注册 click / pointerdown 等事件监听 —— 仅靠构造函数里的 cycle()
// 定时器实现自动轮播，prev/next / indicator 按钮的点击完全不响应。
// 这个脚本桥接 button click 到 Carousel 实例方法。
//
// 依赖：window.twe.Carousel（由 tw-elements UMD 暴露）
// 加载顺序：必须在 tw-elements/index.min.js 之后（两者都用 defer，
// Hugo 按声明顺序执行）

(function () {
  if (typeof window === "undefined") return;
  // 等到 DOM 与 tw-elements 都就绪后再绑定（defer 脚本本身就在 DOMContentLoaded 前执行）
  var bind = function () {
    var Twe = window.twe;
    if (!Twe || !Twe.Carousel) {
      console.warn("[carousel-click] window.twe.Carousel 不可用，跳过 click 桥接");
      return;
    }
    var Carousel = Twe.Carousel;

    document.addEventListener(
      "click",
      function (event) {
        var btn = event.target.closest('[data-twe-slide], [data-twe-slide-to]');
        if (!btn) return;
        var targetSelector = btn.getAttribute("data-twe-target");
        if (!targetSelector) return;
        var carouselEl = document.querySelector(targetSelector);
        if (!carouselEl) return;
        var instance = Carousel.getOrCreateInstance(carouselEl);
        if (!instance) return;

        var slide = btn.getAttribute("data-twe-slide");
        if (slide === "prev") {
          instance.prev();
        } else if (slide === "next") {
          instance.next();
        } else {
          var slideTo = btn.getAttribute("data-twe-slide-to");
          if (slideTo !== null && slideTo !== "") {
            instance.to(parseInt(slideTo, 10));
          }
        }
      },
      false,
    );
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
})();