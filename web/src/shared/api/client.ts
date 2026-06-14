import { demoDashboard, demoDevices, demoSpc } from "../../demoData";
import type { Alarm, AlarmDetail, AlarmStatus, DashboardData, Device, DeviceDetail, DeviceTelemetry, SpcPoint } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === "true";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
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

  async alarms(filters: { status?: AlarmStatus | "all"; severity?: string; deviceCode?: string } = {}): Promise<Alarm[]> {
    if (DEMO_MODE) {
      const dashboard = demoDashboard as unknown as DashboardData;
      return dashboard.recent_alarms.filter((alarm) => {
        if (filters.status && filters.status !== "all" && alarm.status !== filters.status) {
          return false;
        }
        if (filters.severity && alarm.severity !== filters.severity) {
          return false;
        }
        if (filters.deviceCode && alarm.device_code !== filters.deviceCode) {
          return false;
        }
        return true;
      });
    }
    const params = new URLSearchParams({ limit: "100" });
    if (filters.status && filters.status !== "all") {
      params.set("status", filters.status);
    }
    if (filters.severity) {
      params.set("severity", filters.severity);
    }
    if (filters.deviceCode) {
      params.set("device_code", filters.deviceCode);
    }
    return request<Alarm[]>(`/api/alarms?${params.toString()}`);
  },

  async alarmDetail(alarmCode: string): Promise<AlarmDetail> {
    if (DEMO_MODE) {
      const dashboard = demoDashboard as unknown as DashboardData;
      const alarm = dashboard.recent_alarms.find((item) => item.alarm_code === alarmCode);
      if (!alarm) {
        throw new Error("告警不存在");
      }
      return {
        alarm,
        events: [
          { event_type: "created", operator: "system", note: "演示告警由规则触发。", created_at: alarm.started_at },
        ],
      };
    }
    return request<AlarmDetail>(`/api/alarms/${encodeURIComponent(alarmCode)}`);
  },

  async acknowledgeAlarm(alarmCode: string, note: string): Promise<AlarmDetail> {
    return request<AlarmDetail>(`/api/alarms/${encodeURIComponent(alarmCode)}/acknowledge`, {
      method: "PATCH",
      body: JSON.stringify({ operator: "demo-operator", note }),
    });
  },

  async clearAlarm(alarmCode: string, note: string): Promise<AlarmDetail> {
    return request<AlarmDetail>(`/api/alarms/${encodeURIComponent(alarmCode)}/clear`, {
      method: "PATCH",
      body: JSON.stringify({ operator: "demo-operator", note }),
    });
  },
};
