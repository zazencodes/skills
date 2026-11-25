// Loaded by render.sh into a copy of the diagram page. Writes layout faults, or "OK",
// into <pre id="layout-report"> for render.sh to read from the dumped DOM.
(() => {
  const faults = [];
  const frame = document.querySelector(".frame");
  const canvas = document.querySelector(".dg");
  const h1 = document.querySelector(".frame h1");

  const label = (el) => `${el.className || el.tagName.toLowerCase()} "${el.innerText.trim().replace(/\s*\n\s*/g, " / ").replace(/\s+/g, " ").slice(0, 40)}"`;
  const inside = (a, b) => a.left >= b.left - 1 && a.right <= b.right + 1 && a.top >= b.top - 1 && a.bottom <= b.bottom + 1;
  const overlap = (a, b) => a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1;
  const grow = (r, x, y) => ({ left: r.left - x, right: r.right + x, top: r.top - y, bottom: r.bottom + y });

  // One rect per rendered line of an element's text.
  const lineRects = (el) => {
    const range = document.createRange();
    range.selectNodeContents(el);
    const rects = [...range.getClientRects()].filter((r) => r.width > 0).sort((a, b) => a.top - b.top);
    const lines = [];
    for (const r of rects) {
      const line = lines[lines.length - 1];
      if (line && r.top < line.bottom - 2) {
        line.left = Math.min(line.left, r.left); line.right = Math.max(line.right, r.right);
        line.top = Math.min(line.top, r.top); line.bottom = Math.max(line.bottom, r.bottom);
      } else {
        lines.push({ left: r.left, right: r.right, top: r.top, bottom: r.bottom });
      }
    }
    return lines;
  };

  // A font is installed when naming it changes the width of text set in a fallback face.
  const installed = (family) => {
    const probe = document.createElement("span");
    probe.textContent = "mmmmmmmmmmlli1WQ@#";
    probe.style.cssText = "position: absolute; visibility: hidden; font-size: 72px; white-space: nowrap";
    document.body.appendChild(probe);
    const differs = ["monospace", "serif"].some((fallback) => {
      probe.style.fontFamily = fallback;
      const base = probe.getBoundingClientRect().width;
      probe.style.fontFamily = `"${family}", ${fallback}`;
      return probe.getBoundingClientRect().width !== base;
    });
    probe.remove();
    return differs;
  };
  for (const family of ["Inter", "JetBrainsMono Nerd Font"]) {
    if (!installed(family)) faults.push(`font not installed: ${family}`);
  }

  if (!frame || !canvas || !h1) {
    faults.push("page is not built from template.html (.frame, h1 or .dg missing)");
  } else {
    const f = frame.getBoundingClientRect();
    const content = { left: f.left + 72, right: f.right - 72, top: f.top + 56, bottom: f.bottom - 84 };
    if (!inside(h1.getBoundingClientRect(), content) || !inside(canvas.getBoundingClientRect(), content)) {
      faults.push("title plus canvas are taller than the frame: lower the .dg height or shorten the title");
    }
    const c = canvas.getBoundingClientRect();
    for (const el of canvas.querySelectorAll(":scope > div")) {
      if (!inside(el.getBoundingClientRect(), c)) faults.push(`outside the canvas, raise the .dg height or move it: ${label(el)}`);
    }

    const maxLines = [
      [".t, .cap, .sum, .chips span, .rows .s, .item, .ev .d", 1],
      [".ev .m, .ev .n", 2],
    ];
    for (const [selector, max] of maxLines) {
      for (const el of canvas.querySelectorAll(selector)) {
        const n = lineRects(el).length;
        if (n > max) faults.push(`wraps to ${n} lines (max ${max}), widen it or shorten the words: ${label(el)}`);
      }
    }

    for (const el of canvas.querySelectorAll(".box")) {
      if (el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1) {
        faults.push(`content overflows the box, make it larger or the text shorter: ${label(el)}`);
      }
    }

    const texts = [...canvas.querySelectorAll(".t, .s, .cap, .sum, .chips span, .item, .ev .d, .ev .m, .ev .n")]
      .flatMap((el) => lineRects(el).map((r) => ({ el, r })));
    const boxes = [...canvas.querySelectorAll(".box")].map((el) => ({ el, r: el.getBoundingClientRect() }));
    const strokes = [...canvas.querySelectorAll(".arr, .varr, .spine, .axis, .bracket")].map((el) => {
      const r = el.getBoundingClientRect();
      const head = el.matches(".arr") ? [2, 5] : el.matches(".varr") ? [5, 2] : [0, 0];
      return { el, r: grow(r, head[0], head[1]) };
    });

    for (let i = 0; i < texts.length; i++) {
      for (let j = i + 1; j < texts.length; j++) {
        const a = texts[i], b = texts[j];
        if (a.el !== b.el && !a.el.contains(b.el) && !b.el.contains(a.el) && overlap(a.r, b.r)) {
          faults.push(`text collides: ${label(a.el)} and ${label(b.el)}`);
        }
      }
      for (const s of strokes) {
        if (overlap(texts[i].r, s.r)) faults.push(`text crosses a line: ${label(texts[i].el)} and ${s.el.className}`);
      }
      for (const b of boxes) {
        if (!b.el.contains(texts[i].el) && overlap(texts[i].r, b.r)) faults.push(`text runs into a box: ${label(texts[i].el)} and ${label(b.el)}`);
      }
    }
    for (const s of strokes.filter((s) => s.el.matches(".arr, .varr"))) {
      for (const b of boxes) {
        if (overlap(s.r, b.r)) faults.push(`arrow touches a box, leave a 6px gap: ${label(b.el)}`);
      }
    }
  }

  const report = document.createElement("pre");
  report.id = "layout-report";
  report.textContent = faults.length ? [...new Set(faults)].join("\n") : "OK";
  document.body.appendChild(report);
})();
