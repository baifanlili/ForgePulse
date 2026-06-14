export type DeviceStatus = "running" | "warning" | "offline";
export type AlarmSeverity = "critical" | "warning" | "info";
export type AlarmStatus = "active" | "acknowledged" | "cleared";

export type Device = {
  device_code: string;
  device_name: string;
  device_type: string;
  area: string;
  line: string;
  status: DeviceStatus;
  last_heartbeat_at: string;
  created_at?: string;
  updated_at?: string;
};

export type Alarm = {
  alarm_code: string;
  device_code: string;
  severity: AlarmSeverity;
  title: string;
  description?: string;
  status: AlarmStatus;
  started_at: string;
  acknowledged_at?: string | null;
  acknowledged_by?: string | null;
  cleared_at?: string | null;
  cleared_by?: string | null;
};

export type AlarmEvent = {
  event_type: string;
  operator: string;
  note?: string | null;
  created_at: string;
};

export type AlarmDetail = {
  alarm: Alarm;
  events: AlarmEvent[];
};

export type LotYield = {
  lot_code: string;
  product_code: string;
  wafer_count?: number;
  total_die?: number;
  pass_die?: number;
  fail_die?: number;
  yield_rate: number;
  started_at: string;
  completed_at?: string | null;
};

export type BinCount = {
  bin_name: string;
  die_count: number;
};

export type MetricPoint = {
  device_code: string;
  metric_name: string;
  metric_value: number;
  time: string;
  tags?: Record<string, unknown>;
};

export type SpcPoint = {
  metric_name?: string;
  sample_time: string;
  value: number;
  center_line: number;
  upper_control_limit: number;
  lower_control_limit: number;
};

export type DashboardData = {
  summary: {
    device_count: number;
    running_count: number;
    warning_count: number;
    offline_count: number;
    active_alarm_count: number;
    average_yield: number;
  };
  latest_metrics: MetricPoint[];
  recent_alarms: Alarm[];
  yield_trend: LotYield[];
  bin_distribution: BinCount[];
};

export type DeviceDetail = {
  device: Device;
  latest_metrics: Array<Pick<MetricPoint, "metric_name" | "metric_value" | "time">>;
  alarms: Alarm[];
};

export type DeviceTelemetry = {
  device_code: string;
  metric_name: string | null;
  all_history: boolean;
  hours: number;
  limit: number;
  metrics: string[];
  points: MetricPoint[];
};
