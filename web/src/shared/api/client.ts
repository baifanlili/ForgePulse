import { demoDashboard, demoDevices, demoSpc } from "../../demoData";
import type {
  Alarm,
  AlarmDetail,
  AlarmStatus,
  DashboardData,
  Device,
  DeviceDetail,
  DeviceTelemetry,
  EdgeCommand,
  EdgeGateway,
  SpcPoint,
  SystemOverview,
} from "../types";

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
        alarms: (dashboard.recent_alarms as unknown as Array<{
          alarm_code: string;
          device_code: string;
          severity: string;
          title: string;
          description?: string | null;
          status: string;
          started_at: string;
          cleared_at?: string | null;
        }>)
          .filter((item) => item.device_code === deviceCode)
          .map((item) => ({
            alarm_code: item.alarm_code,
            severity: item.severity as Alarm["severity"],
            title: item.title,
            description: item.description ?? null,
            status: item.status as Alarm["status"],
            started_at: item.started_at,
            cleared_at: item.cleared_at ?? null,
          })),
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
        tags: null,
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

  async systemOverview(): Promise<SystemOverview> {
    if (DEMO_MODE) {
      return {
        services: [
          { name: "platform-api", status: "ok", detail: "静态 Demo 模式" },
          { name: "postgres", status: "ok", detail: "使用内置演示数据" },
          { name: "stream-worker", status: "stale", detail: "静态 Demo 不连接实时 worker" },
          { name: "edge-gateway", status: "stale", detail: "静态 Demo 不连接边缘网关" },
        ],
        summary: {
          device_count: 5,
          running_count: 3,
          warning_count: 1,
          offline_count: 1,
          active_alarm_count: 2,
          acknowledged_alarm_count: 1,
          cleared_alarm_count: 0,
          telemetry_count: 4280,
          latest_telemetry_at: new Date().toISOString(),
          telemetry_lag_seconds: 12,
        },
        recent_device_ingestion: [
          { device_code: "ETCH-01", latest_time: new Date().toISOString(), point_count: 240 },
          { device_code: "CVD-02", latest_time: new Date().toISOString(), point_count: 238 },
          { device_code: "TEST-04", latest_time: new Date().toISOString(), point_count: 236 },
        ],
        metric_ingestion: [
          { metric_name: "temperature", point_count: 320 },
          { metric_name: "pressure", point_count: 320 },
          { metric_name: "voltage", point_count: 320 },
          { metric_name: "yield_rate", point_count: 320 },
        ],
        table_counts: [
          { table_name: "devices", row_count: 5 },
          { table_name: "telemetry_points", row_count: 4280 },
          { table_name: "alarms", row_count: 8 },
          { table_name: "alarm_events", row_count: 16 },
          { table_name: "worker_heartbeats", row_count: 360 },
        ],
        worker: {
          worker_id: "stream-worker-01",
          status: "healthy",
          last_heartbeat_at: new Date().toISOString(),
          telemetry_processed: 4280,
          alarms_triggered: 8,
          lag_seconds: 2,
        },
      };
    }
    return request<SystemOverview>("/api/system/overview");
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
      }) as unknown as Alarm[];
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
      const alarm = dashboard.recent_alarms.find((item) => item.alarm_code === alarmCode) as unknown as
        | Alarm
        | undefined;
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

  async edgeGateways(): Promise<EdgeGateway[]> {
    if (DEMO_MODE) {
      return [
        {
          gateway_id: "EDGE-GW-01",
          line_id: "FAB-A-RT",
          latest_seen_at: new Date().toISOString(),
          latest_sequence: 128,
          sample_period_ms: 5000,
          telemetry_point_count: 4800,
          degraded_point_count: 64,
          latest_quality: "good",
          latest_status_reason: "normal",
          latest_command: null,
        },
      ];
    }
    return request<EdgeGateway[]>("/api/edge/gateways");
  },

  async edgeCommands(gatewayId: string): Promise<EdgeCommand[]> {
    if (DEMO_MODE) {
      return [];
    }
    return request<EdgeCommand[]>(`/api/edge/gateways/${encodeURIComponent(gatewayId)}/commands`);
  },

  async sendEdgeCommand(
    gatewayId: string,
    commandType: EdgeCommand["command_type"],
    parameters: Record<string, unknown> = {},
  ): Promise<EdgeCommand> {
    return request<EdgeCommand>(`/api/edge/gateways/${encodeURIComponent(gatewayId)}/commands`, {
      method: "POST",
      body: JSON.stringify({
        command_type: commandType,
        parameters,
        operator: "demo-operator",
      }),
    });
  },
};
