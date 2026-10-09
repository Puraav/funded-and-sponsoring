"use client";

import { useEffect, useRef } from "react";

type PlotModule = typeof import("@observablehq/plot");

/**
 * Draw an Observable Plot chart into a div and redraw when the div changes width.
 * Plot is loaded on demand so it never blocks the first paint.
 */
export function usePlot(
  draw: (Plot: PlotModule, width: number) => Element,
  deps: unknown[],
) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    let cancelled = false;
    let plot: PlotModule | undefined;

    const render = () => {
      if (cancelled || !plot || node.clientWidth === 0) return;
      const chart = draw(plot, node.clientWidth);
      // Plot labels its internal <g> groups ("bar", "tip"), which is invalid ARIA without a
      // role. The wrapper div carries the chart's real label, so drop the inner ones.
      for (const group of chart.querySelectorAll("g[aria-label]")) {
        group.removeAttribute("aria-label");
      }
      node.replaceChildren(chart);
    };
    import("@observablehq/plot").then((loaded) => {
      plot = loaded;
      render();
    });
    const observer = new ResizeObserver(render);
    observer.observe(node);
    return () => {
      cancelled = true;
      observer.disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return ref;
}
