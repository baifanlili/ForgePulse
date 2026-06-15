export type DeviceStatus = "running" | "warning" | "offline";
export type AlarmSeverity = "critical" | "warning" | "info";
export type AlarmStatus = "active" | "acknowledged" | "cleared";
export type ServiceStatus = "ok" | "stale" | "no_data" | "error";
export type CommandType = "pause" | "resume" | "set_interval" | "inject_fault";

export type Device = {
  device_code: string;
  device_name: string;
  device_type: string;
  area: string | null;
  line: string | null;
  status: DeviceStatus;
  last_heartbeat_at: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type Alarm = {
  alarm_code: string;
  device_code: string;
  severity: AlarmSeverity;
  title: string;
  description: string | null;
  status: AlarmStatus;
  started_at: string;
  acknowledged_at: string | null;
  acknowledged_by: string | null;
  cleared_at: string | null;
  cleared_by: string | null;
};

export type AlarmEvent = {
  event_type: string;
  operator: string;
  note: string | null;
  created_at: string;
};

export type AlarmDetail = {
  alarm: Alarm;
  events: AlarmEvent[];
};

export type AlarmSummary = {
  alarm_code: string;
  device_code?: string | null;
  severity?: AlarmSeverity | null;
  title?: string | null;
  description?: string | null;
  status?: AlarmStatus | null;
  started_at?: string | null;
  acknowledged_at?: string | null;
  acknowledged_by?: string | null;
  cleared_at?: string | null;
  cleared_by?: string | null;
};

export type LotYield = {
  lot_code: string;
  product_code: string;
  wafer_count: number | null;
  total_die: number | null;
  pass_die: number | null;
  fail_die: number | null;
  yield_rate: number;
  started_at: string | null;
  completed_at: string | null;
};

export type WaferYield = {
  wafer_id: string;
  yield_rate: number;
  pass_die: number | null;
  fail_die: number | null;
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
  tags: Record<string, unknown> | null;
};

export type LatestMetric = {
  metric_name: string;
  metric_value: number;
  time: string;
};

export type SpcPoint = {
  metric_name: string;
  sample_time: string;
  value: number;
  center_line: number;
  upper_control_limit: number;
  lower_control_limit: number;
};

export type DashboardSummary = {
  device_count: number;
  running_count: number;
  warning_count: number;
  offline_count: number;
  active_alarm_count: number;
  average_yield: number;
};

export type LatestMetricPoint = {
  device_code: string;
  metric_name: string;
  metric_value: number;
  time: string;
};

export type RecentAlarm = {
  alarm_code: string;
  device_code: string;
  severity: AlarmSeverity;
  title: string;
  status: AlarmStatus;
  started_at: string;
};

export type YieldTrend = {
  lot_code: string;
  product_code: string;
  yield_rate: number;
  started_at: string;
};

export type BinDistItem = {
  bin_name: string;
  die_count: number;
};

export type DashboardData = {
  summary: DashboardSummary;
  latest_metrics: LatestMetricPoint[];
  recent_alarms: RecentAlarm[];
  yield_trend: LotYield[];
  bin_distribution: BinDistItem[];
};

export type DeviceDetail = {
  device: Device;
  latest_metrics: LatestMetric[];
  alarms: AlarmSummary[];
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

export type SystemServiceStatus = {
  name: string;
  status: ServiceStatus;
  detail: string;
};

export type SystemOverviewSummary = {
  device_count: number;
  running_count: number;
  warning_count: number;
  offline_count: number;
  active_alarm_count: number;
  acknowledged_alarm_count: number;
  cleared_alarm_count: number;
  telemetry_count: number;
  latest_telemetry_at: string | null;
  telemetry_lag_seconds: number | null;
};

export type RecentDeviceIngestion = {
  device_code: string;
  latest_time: string;
  point_count: number;
};

export type MetricIngestion = {
  metric_name: string;
  point_count: number;
};

export type TableCount = {
  table_name: string;
  row_count: number;
};

export type SystemOverview = {
  services: SystemServiceStatus[];
  summary: SystemOverviewSummary;
  recent_device_ingestion: RecentDeviceIngestion[];
  metric_ingestion: MetricIngestion[];
  table_counts: TableCount[];
  worker: WorkerHealth | null;
};

export type WorkerHealth = {
  worker_id: string | null;
  status: string | null;
  last_heartbeat_at: string | null;
  telemetry_processed: number;
  alarms_triggered: number;
  lag_seconds: number | null;
};

export type EdgeCommand = {
  command_id: string;
  gateway_id: string;
  command_type: CommandType;
  parameters: Record<string, unknown>;
  status: string;
  operator: string;
  created_at: string;
  published_at: string | null;
};

export type EdgeGateway = {
  gateway_id: string;
  line_id: string | null;
  latest_seen_at: string;
  latest_sequence: number | null;
  sample_period_ms: number | null;
  telemetry_point_count: number;
  degraded_point_count: number;
  latest_quality: string | null;
  latest_status_reason: string | null;
  latest_command: EdgeCommand | null;
};

export type EdgeCommandRequest = {
  command_type: CommandType;
  parameters: Record<string, unknown>;
  operator: string;
};
