import { useMemo, useRef } from "react";
import type * as echarts from "echarts";
import type { LotYield } from "../types";
import { useChart } from "./useChart";

export function YieldTrendChart({ data }: { data: LotYield[] }) {
  const ref = useRef<HTMLDivElement>(null);
  const option = useMemo<echarts.EChartsOption>(
    () => ({
      color: ["#2563eb"],
      grid: { left: 40, right: 18, top: 28, bottom: 36 },
      tooltip: { trigger: "axis", valueFormatter: (value) => `${value}%` },
      xAxis: {
        type: "category",
        data: data.map((item) => item.lot_code.replace("LOT-", "")),
        axisLabel: { color: "#64748b" },
      },
      yAxis: {
        type: "value",
        min: 90,
        max: 98,
        axisLabel: { formatter: "{value}%", color: "#64748b" },
        splitLine: { lineStyle: { color: "#e2e8f0" } },
      },
      series: [
        {
          name: "良率",
          type: "line",
          smooth: true,
          symbolSize: 8,
          data: data.map((item) => item.yield_rate),
          markLine: {
            symbol: "none",
            lineStyle: { color: "#ef4444", type: "dashed" },
            data: [{ yAxis: 94 }],
          },
        },
      ],
    }),
    [data],
  );
  useChart(ref, option);
  return <div className="chart" ref={ref} />;
}
