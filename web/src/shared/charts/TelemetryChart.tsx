import { useMemo, useRef } from "react";
import type * as echarts from "echarts";
import { formatTime } from "../format";
import type { MetricPoint } from "../types";
import { useChart } from "./useChart";

export function TelemetryChart({ data }: { data: MetricPoint[] }) {
  const ref = useRef<HTMLDivElement>(null);
  const option = useMemo<echarts.EChartsOption>(
    () => ({
      color: ["#0f766e"],
      grid: { left: 46, right: 18, top: 24, bottom: 36 },
      tooltip: { trigger: "axis" },
      xAxis: {
        type: "category",
        data: data.map((item) => formatTime(item.time).slice(0, 5)),
        axisLabel: { color: "#64748b" },
      },
      yAxis: {
        type: "value",
        scale: true,
        axisLabel: { color: "#64748b" },
        splitLine: { lineStyle: { color: "#e2e8f0" } },
      },
      series: [
        {
          name: data[0]?.metric_name ?? "metric",
          type: "line",
          smooth: true,
          symbolSize: 6,
          data: data.map((item) => Number(item.metric_value.toFixed(3))),
        },
      ],
    }),
    [data],
  );
  useChart(ref, option);
  return <div className="chart" ref={ref} />;
}
