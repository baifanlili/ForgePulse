import { useMemo, useRef } from "react";
import type * as echarts from "echarts";
import type { BinCount } from "../types";
import { useChart } from "./useChart";

export function BinChart({ data }: { data: BinCount[] }) {
  const ref = useRef<HTMLDivElement>(null);
  const option = useMemo<echarts.EChartsOption>(
    () => ({
      color: ["#14b8a6", "#f97316", "#8b5cf6", "#ef4444", "#64748b"],
      tooltip: { trigger: "item" },
      legend: { bottom: 0, textStyle: { color: "#475569" } },
      series: [
        {
          name: "Bin 分布",
          type: "pie",
          radius: ["46%", "70%"],
          center: ["50%", "42%"],
          avoidLabelOverlap: true,
          label: { formatter: "{b}\n{d}%" },
          data: data.map((item) => ({ name: item.bin_name, value: item.die_count })),
        },
      ],
    }),
    [data],
  );
  useChart(ref, option);
  return <div className="chart" ref={ref} />;
}
