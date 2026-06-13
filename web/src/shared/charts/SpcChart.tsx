import { useMemo, useRef } from "react";
import type * as echarts from "echarts";
import { formatTime } from "../format";
import type { SpcPoint } from "../types";
import { useChart } from "./useChart";

export function SpcChart({ data }: { data: SpcPoint[] }) {
  const ref = useRef<HTMLDivElement>(null);
  const option = useMemo<echarts.EChartsOption>(
    () => ({
      color: ["#0f766e", "#ef4444", "#f97316", "#64748b"],
      grid: { left: 42, right: 18, top: 28, bottom: 36 },
      tooltip: { trigger: "axis" },
      xAxis: {
        type: "category",
        data: data.map((item) => formatTime(item.sample_time).slice(0, 5)),
        axisLabel: { color: "#64748b" },
      },
      yAxis: {
        type: "value",
        min: 26,
        max: 30,
        axisLabel: { color: "#64748b" },
        splitLine: { lineStyle: { color: "#e2e8f0" } },
      },
      series: [
        { name: "CD", type: "line", data: data.map((item) => item.value), symbolSize: 8 },
        { name: "UCL", type: "line", data: data.map((item) => item.upper_control_limit), showSymbol: false, lineStyle: { type: "dashed" } },
        { name: "CL", type: "line", data: data.map((item) => item.center_line), showSymbol: false, lineStyle: { type: "dotted" } },
        { name: "LCL", type: "line", data: data.map((item) => item.lower_control_limit), showSymbol: false, lineStyle: { type: "dashed" } },
      ],
    }),
    [data],
  );
  useChart(ref, option);
  return <div className="chart" ref={ref} />;
}
