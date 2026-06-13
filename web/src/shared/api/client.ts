import { demoDashboard, demoDevices, demoSpc } from "../../demoData";
import type { DashboardData, Device, DeviceDetail, DeviceTelemetry, SpcPoint } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === "true";

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`API 请求失败：${path}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  async dashboard(): Promise<DashboardData> {
    if (DEMO_MODE) {
      return demoDashboard as unknown as DashboardData;
    }
    return request<DashboardData>("/api/dashboard");
  },

  async devices(): Promise<Device[]> {
    if (DEMO_MODE) {
      return [...demoDevices] as unknown as Device[];
    }
    return request<Device[]>("/api/devices");
  },

  async deviceDetail(deviceCode: string): Promise<DeviceDetail> {
    if (DEMO_MODE) {
      const device = (demoDevices as readonly Device[]).find((item) => item.device_code === deviceCode);
      if (!device) {
        throw new Error("设备不存在");
      }
      const dashboard = demoDashboard as unknown as DashboardData;
      return {
        device,
        latest_metrics: dashboard.latest_metrics.filter((item) => item.device_code === deviceCode),
        alarms: dashboard.recent_alarms.filter((item) => item.device_code === deviceCode),
      };
    }
    return request<DeviceDetail>(`/api/devices/${encodeURIComponent(deviceCode)}`);
  },

  async deviceTelemetry(deviceCode: string, metricName?: string): Promise<DeviceTelemetry> {
    if (DEMO_MODE) {
      const points = Array.from({ length: 16 }, (_, index) => ({
        device_code: deviceCode,
        metric_name: metricName ?? "temperature",
        metric_value: 68 + Math.sin(index / 2) * 4,
        time: new Date(Date.now() - (16 - index) * 5 * 60 * 1000).toISOString(),
      }));
      return {
        device_code: deviceCode,
        metric_name: metricName ?? "temperature",
        all_history: false,
        hours: 1,
        limit: 200,
        metrics: ["temperature", "pressure", "voltage", "yield_rate"],
        points,
      };
    }
    const params = new URLSearchParams({ hours: "1", limit: "200" });
    if (metricName) {
      params.set("metric_name", metricName);
    }
    return request<DeviceTelemetry>(`/api/devices/${encodeURIComponent(deviceCode)}/telemetry?${params.toString()}`);
  },

  async spc(): Promise<SpcPoint[]> {
    if (DEMO_MODE) {
      return [...demoSpc] as unknown as SpcPoint[];
    }
    return request<SpcPoint[]>("/api/analytics/spc");
  },
};
