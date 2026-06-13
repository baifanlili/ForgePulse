import { useEffect } from "react";
import * as echarts from "echarts";

export function useChart(ref: React.RefObject<HTMLDivElement>, option: echarts.EChartsOption | null) {
  useEffect(() => {
    if (!ref.current || !option) {
      return;
    }

    const chart = echarts.init(ref.current);
    chart.setOption(option);

    const resize = () => chart.resize();
    window.addEventListener("resize", resize);

    return () => {
      window.removeEventListener("resize", resize);
      chart.dispose();
    };
  }, [option, ref]);
}
