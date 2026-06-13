const now = Date.now();

function minutesAgo(minutes: number) {
  return new Date(now - minutes * 60 * 1000).toISOString();
}

function hoursAgo(hours: number) {
  return new Date(now - hours * 60 * 60 * 1000).toISOString();
}

export const demoDevices = [
  {
    device_code: "ETCH-01",
    device_name: "刻蚀机 01",
    device_type: "Etcher",
    area: "FAB-A",
    line: "Line-01",
    status: "running",
    last_heartbeat_at: minutesAgo(1),
  },
  {
    device_code: "CVD-02",
    device_name: "薄膜沉积 02",
    device_type: "CVD",
    area: "FAB-A",
    line: "Line-01",
    status: "running",
    last_heartbeat_at: minutesAgo(2),
  },
  {
    device_code: "PHOTO-03",
    device_name: "光刻机 03",
    device_type: "Lithography",
    area: "FAB-A",
    line: "Line-02",
    status: "warning",
    last_heartbeat_at: minutesAgo(7),
  },
  {
    device_code: "TEST-04",
    device_name: "晶圆测试 04",
    device_type: "Wafer Tester",
    area: "TEST-B",
    line: "Line-07",
    status: "running",
    last_heartbeat_at: minutesAgo(1),
  },
  {
    device_code: "PACK-05",
    device_name: "封装检测 05",
    device_type: "Inspection",
    area: "PACK-C",
    line: "Line-03",
    status: "offline",
    last_heartbeat_at: minutesAgo(35),
  },
] as const;

export const demoDashboard = {
  summary: {
    device_count: 5,
    running_count: 3,
    warning_count: 1,
    offline_count: 1,
    active_alarm_count: 3,
    average_yield: 94.3,
  },
  latest_metrics: [
    { device_code: "ETCH-01", metric_name: "temperature", metric_value: 73.7, time: minutesAgo(1) },
    { device_code: "CVD-02", metric_name: "pressure", metric_value: 2.5, time: minutesAgo(1) },
    { device_code: "PHOTO-03", metric_name: "overlay_error", metric_value: 4.2, time: minutesAgo(8) },
    { device_code: "TEST-04", metric_name: "pass_rate", metric_value: 95.4, time: minutesAgo(2) },
  ],
  recent_alarms: [
    {
      alarm_code: "ALM-DEMO-001",
      device_code: "PHOTO-03",
      severity: "warning",
      title: "心跳延迟",
      status: "active",
      started_at: minutesAgo(7),
    },
    {
      alarm_code: "ALM-DEMO-002",
      device_code: "ETCH-01",
      severity: "critical",
      title: "腔体温度偏高",
      status: "active",
      started_at: minutesAgo(11),
    },
    {
      alarm_code: "ALM-DEMO-003",
      device_code: "PACK-05",
      severity: "warning",
      title: "设备离线",
      status: "active",
      started_at: minutesAgo(35),
    },
  ],
  yield_trend: [
    { lot_code: "LOT-A240613-01", product_code: "FP-7N-ASIC", yield_rate: 94.48, started_at: hoursAgo(8) },
    { lot_code: "LOT-A240613-02", product_code: "FP-7N-ASIC", yield_rate: 93.11, started_at: hoursAgo(6) },
    { lot_code: "LOT-B240613-03", product_code: "FP-PMIC-28", yield_rate: 95.3, started_at: hoursAgo(4) },
    { lot_code: "LOT-B240613-04", product_code: "FP-PMIC-28", yield_rate: 94.3, started_at: hoursAgo(2) },
  ],
  bin_distribution: [
    { bin_name: "Bin 1 Pass", die_count: 7242 },
    { bin_name: "Bin 2 Leakage", die_count: 126 },
    { bin_name: "Bin 3 Timing", die_count: 184 },
    { bin_name: "Bin 4 Open/Short", die_count: 79 },
    { bin_name: "Bin 5 Other", die_count: 49 },
  ],
} as const;

export const demoSpc = [
  { sample_time: hoursAgo(8), value: 27.8, center_line: 28.0, upper_control_limit: 29.2, lower_control_limit: 26.8 },
  { sample_time: hoursAgo(7), value: 28.1, center_line: 28.0, upper_control_limit: 29.2, lower_control_limit: 26.8 },
  { sample_time: hoursAgo(6), value: 28.4, center_line: 28.0, upper_control_limit: 29.2, lower_control_limit: 26.8 },
  { sample_time: hoursAgo(5), value: 28.0, center_line: 28.0, upper_control_limit: 29.2, lower_control_limit: 26.8 },
  { sample_time: hoursAgo(4), value: 28.6, center_line: 28.0, upper_control_limit: 29.2, lower_control_limit: 26.8 },
  { sample_time: hoursAgo(3), value: 28.9, center_line: 28.0, upper_control_limit: 29.2, lower_control_limit: 26.8 },
  { sample_time: hoursAgo(2), value: 29.4, center_line: 28.0, upper_control_limit: 29.2, lower_control_limit: 26.8 },
  { sample_time: hoursAgo(1), value: 28.7, center_line: 28.0, upper_control_limit: 29.2, lower_control_limit: 26.8 },
] as const;
