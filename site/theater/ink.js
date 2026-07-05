/* 程序化水墨 — 章節背景層(V05-A;工單 docs/plans/theater_ink_wash_rendering_2026-07-06.md)
   純渲染層:讀狀態、不寫狀態、不碰任何判定。
   決定論:同 (撤回碼, 章節, 資源) → 同一幅畫;回讀你的軌痕=看見你當時的城。
   零資產零網路:純 SVG 字串,feTurbulence 做墨暈。 */

(function () {
  "use strict";

  // xorshift32 — 可重現的偽隨機(Math.random 不決定論,禁用)
  function rng(seedStr) {
    let h = 2166136261;
    for (let i = 0; i < seedStr.length; i++) {
      h ^= seedStr.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    let x = h || 88675123;
    return function () {
      x ^= x << 13; x ^= x >>> 17; x ^= x << 5;
      return ((x >>> 0) % 10000) / 10000;
    };
  }

  /* 聯動表(工單 v0):
     能源 → 亮窗數與天空留白(低=城暗)
     信任 → 輪廓收斂(低=墨緣毛散,turbulence 強)
     章節+撤回碼 → 構圖種子 */
  function chapterBackdrop(code, chapter, resources) {
    const r = rng(String(code || "anon") + "#" + String(chapter));
    const energy = Math.max(0, Math.min(10, (resources && resources.energy) ?? 5));
    const trust = Math.max(0, Math.min(10, (resources && resources.trust) ?? 5));

    const W = 800, H = 180;
    const horizon = 120 + Math.floor(r() * 20);
    const blur = (10 - trust) * 0.35;            // 信任低 → 墨緣散
    const skyInk = 0.06 + (10 - energy) * 0.028; // 能源低 → 天更沉

    // 城市剪影:12-18 棟樓,高低由種子定
    let buildings = "";
    let windows = "";
    const n = 12 + Math.floor(r() * 7);
    let x = 0;
    for (let i = 0; i < n && x < W; i++) {
      const w = 28 + Math.floor(r() * 55);
      const h = 20 + Math.floor(r() * (horizon - 30));
      const y = horizon - h;
      const shade = 0.55 + r() * 0.35;
      buildings += `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="black" opacity="${shade.toFixed(2)}"/>`;
      // 亮窗:能源驅動(城暗=燈滅)
      const lit = Math.round((energy / 10) * (1 + r() * 3));
      for (let j = 0; j < lit; j++) {
        const wx = x + 4 + Math.floor(r() * Math.max(1, w - 8));
        const wy = y + 6 + Math.floor(r() * Math.max(1, h - 12));
        windows += `<rect x="${wx}" y="${wy}" width="3" height="4" fill="white" opacity="0.85"/>`;
      }
      x += w + 2 + Math.floor(r() * 10);
    }

    // 岔軌:自畫面底收攏向城門(每章角度隨種子微變)
    const vx = W * (0.3 + r() * 0.4);
    let rails = "";
    for (let i = 0; i < 3; i++) {
      const sx = W * (0.1 + 0.35 * i + r() * 0.08);
      rails += `<path d="M ${sx.toFixed(0)} ${H} L ${vx.toFixed(0)} ${horizon}" stroke="black" stroke-width="${(1.6 - i * 0.4).toFixed(1)}" opacity="0.5" fill="none"/>`;
    }

    const fid = "inkf" + String(chapter).replace(/[^a-z0-9]/gi, "");
    return (
      `<svg class="chapter-ink" viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMax slice" role="img" aria-label="本章的城(水墨,由你的資源狀態繪成)">` +
      `<defs><filter id="${fid}"><feTurbulence type="fractalNoise" baseFrequency="0.012 0.03" numOctaves="2" seed="${Math.floor(r() * 999)}"/>` +
      `<feDisplacementMap in="SourceGraphic" scale="${(3 + blur * 4).toFixed(1)}"/>` +
      `<feGaussianBlur stdDeviation="${blur.toFixed(2)}"/></filter></defs>` +
      `<rect width="${W}" height="${horizon}" fill="black" opacity="${skyInk.toFixed(3)}"/>` +
      `<g filter="url(#${fid})">${buildings}</g>${windows}${rails}` +
      `<rect y="${horizon}" width="${W}" height="1.5" fill="black" opacity="0.6"/>` +
      `</svg>`
    );
  }

  window.TheaterInk = { chapterBackdrop: chapterBackdrop };
})();
