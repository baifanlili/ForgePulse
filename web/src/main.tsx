import React, { useEffect, useMemo, useRef, useState } from "react";
import ReactDOM from "react-dom/client";
import { Alert, Card, Col, ConfigProvider, Layout, List, Row, Space, Spin, Statistic, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import * as echarts from "echarts";
import "antd/dist/reset.css";
import { demoDashboard, demoDevices, demoSpc } from "./demoData";
import "./styles.css";

const { Header, Content } = Layout;
const { Text, Title } = Typography;

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === "true";

type DeviceStatus = "running" | "warning" | "offline";
type AlarmSeverity = "critical" | "warning" | "info";
type AlarmStatus = "active" | "cleared";

type Device = {
  device_code: string;
  device_name: string;
  device_type: string;
  area: string;
  line: string;
  status: DeviceStatus;
  last_heartbeat_at: string;
};

type Alarm = {
  alarm_code: string;
  device_code: string;
  severity: AlarmSeverity;
  title: string;
  status: AlarmStatus;
  started_at: string;
};

type LotYield = {
  lot_code: string;
  product_code: string;
  yield_rate: number;
  started_at: string;
};

type BinCount = {
  bin_name: string;
  die_count: number;
};

type MetricPoint = {
  device_code: string;
  metric_name: string;
  metric_value: number;
  time: string;
};

type SpcPoint = {
  sample_time: string;
  value: number;
  center_line: number;
  upper_control_limit: number;
  lower_control_limit: number;
};

type DashboardData = {
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

const statusLabel: Record<DeviceStatus, string> = {
  running: "运行中",
  warning: "预警",
  offline: "离线",
};

const statusColor: Record<DeviceStatus, string> = {
  running: "green",
  warning: "gold",
  offline: "default",
};

const severityColor: Record<AlarmSeverity, string> = {
  critical: "red",
  warning: "gold",
  info: "blue",
};

function formatTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(value));
}

function useChart(ref: React.RefObject<HTMLDivElement>, option: echarts.EChartsOption | null) {
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

function YieldTrendChart({ data }: { data: LotYield[] }) {
  const ref = useRef<HTMLDivElement>(null);
  const option = useMemo<echarts.EChartsOption>(
    () => ({
      color: ["#2563eb"],
      grid: { left: 40, right: 18, top: 28, bottom: 36 },
      tooltip: { trigger: "axis", valueFormatter: (value) => `${value}%` },
      xAxis: {
        type: "category",
        data: data.map((item) => item.lot_code.replace("LOT-", "")),
        axisLabel: { color: "#64748b" },
      },
      yAxis: {
        type: "value",
        min: 90,
        max: 98,
        axisLabel: { formatter: "{value}%", color: "#64748b" },
        splitLine: { lineStyle: { color: "#e2e8f0" } },
      },
      series: [
        {
          name: "良率",
          type: "line",
          smooth: true,
          symbolSize: 8,
          data: data.map((item) => item.yield_rate),
          markLine: {
            symbol: "none",
            lineStyle: { color: "#ef4444", type: "dashed" },
            data: [{ yAxis: 94 }],
          },
        },
      ],
    }),
    [data],
  );
  useChart(ref, option);
  return <div className="chart" ref={ref} />;
}

function BinChart({ data }: { data: BinCount[] }) {
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

function SpcChart({ data }: { data: SpcPoint[] }) {
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

function App() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [devices, setDevices] = useState<Device[]>([]);
  const [spc, setSpc] = useState<SpcPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load(showLoading: boolean) {
      try {
        if (showLoading) {
          setLoading(true);
        }
        if (DEMO_MODE) {
          setDashboard(demoDashboard as unknown as DashboardData);
          setDevices([...demoDevices] as unknown as Device[]);
          setSpc([...demoSpc] as unknown as SpcPoint[]);
          setLastUpdatedAt(new Date().toISOString());
          setError(null);
          return;
        }

        const [dashboardRes, devicesRes, spcRes] = await Promise.all([
          fetch(`${API_BASE}/api/dashboard`),
          fetch(`${API_BASE}/api/devices`),
          fetch(`${API_BASE}/api/analytics/spc`),
        ]);

        if (!dashboardRes.ok || !devicesRes.ok || !spcRes.ok) {
          throw new Error("API 返回异常");
        }

        const [dashboardData, devicesData, spcData] = await Promise.all([
          dashboardRes.json(),
          devicesRes.json(),
          spcRes.json(),
        ]);

        if (!active) {
          return;
        }

        setDashboard(dashboardData);
        setDevices(devicesData);
        setSpc(spcData);
        setLastUpdatedAt(new Date().toISOString());
        setError(null);
      } catch (caught) {
        if (active) {
          setError(caught instanceof Error ? caught.message : "加载数据失败");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    load(true);
    const timer = window.setInterval(() => load(false), 10000);

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  const columns: ColumnsType<Device> = [
    {
      title: "设备",
      dataIndex: "device_name",
      render: (name, row) => (
        <Space direction="vertical" size={0}>
          <Text strong>{name}</Text>
          <Text type="secondary">{row.device_code}</Text>
        </Space>
      ),
    },
    { title: "类型", dataIndex: "device_type" },
    { title: "区域", dataIndex: "area" },
    { title: "产线", dataIndex: "line" },
    {
      title: "状态",
      dataIndex: "status",
      render: (status: DeviceStatus) => <Tag color={statusColor[status]}>{statusLabel[status]}</Tag>,
    },
    {
      title: "最近心跳",
      dataIndex: "last_heartbeat_at",
      render: (value: string) => formatTime(value),
    },
  ];

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: "#0f766e",
          borderRadius: 6,
          fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
        },
      }}
    >
      <Layout className="app">
        <Header className="topbar">
          <div>
            <Text className="brand">ForgePulse</Text>
            <Title level={3}>半导体设备数据平台</Title>
          </div>
          <Space wrap>
            {lastUpdatedAt ? <Tag color="blue">更新于 {formatTime(lastUpdatedAt)}</Tag> : null}
            <Tag color="cyan">MVP 数据闭环</Tag>
          </Space>
        </Header>
        <Content className="content">
          {loading ? (
            <div className="loading">
              <Spin size="large" />
            </div>
          ) : error || !dashboard ? (
            <Alert
              type="error"
              message="仪表盘数据加载失败"
              description={`请确认 platform-api 已启动并可访问 ${API_BASE}。${error ?? ""}`}
              showIcon
            />
          ) : (
            <Space direction="vertical" size={18} className="stack">
              <Row gutter={[16, 16]}>
                <Col xs={12} lg={4}>
                  <Card>
                    <Statistic title="设备总数" value={dashboard.summary.device_count} />
                  </Card>
                </Col>
                <Col xs={12} lg={4}>
                  <Card>
                    <Statistic title="运行中" value={dashboard.summary.running_count} valueStyle={{ color: "#15803d" }} />
                  </Card>
                </Col>
                <Col xs={12} lg={4}>
                  <Card>
                    <Statistic title="预警设备" value={dashboard.summary.warning_count} valueStyle={{ color: "#ca8a04" }} />
                  </Card>
                </Col>
                <Col xs={12} lg={4}>
                  <Card>
                    <Statistic title="离线设备" value={dashboard.summary.offline_count} valueStyle={{ color: "#64748b" }} />
                  </Card>
                </Col>
                <Col xs={12} lg={4}>
                  <Card>
                    <Statistic title="活动告警" value={dashboard.summary.active_alarm_count} valueStyle={{ color: "#dc2626" }} />
                  </Card>
                </Col>
                <Col xs={12} lg={4}>
                  <Card>
                    <Statistic title="24h 平均良率" value={dashboard.summary.average_yield} suffix="%" precision={2} valueStyle={{ color: "#2563eb" }} />
                  </Card>
                </Col>
              </Row>

              <Row gutter={[16, 16]}>
                <Col xs={24} xl={14}>
                  <Card title="设备状态">
                    <Table<Device>
                      rowKey="device_code"
                      columns={columns}
                      dataSource={devices}
                      pagination={false}
                      size="middle"
                    />
                  </Card>
                </Col>
                <Col xs={24} xl={10}>
                  <Card title="最近告警">
                    <List
                      dataSource={dashboard.recent_alarms}
                      renderItem={(alarm) => (
                        <List.Item>
                          <List.Item.Meta
                            title={
                              <Space wrap>
                                <Tag color={severityColor[alarm.severity]}>{alarm.severity.toUpperCase()}</Tag>
                                <Text strong>{alarm.title}</Text>
                              </Space>
                            }
                            description={`${alarm.device_code} · ${alarm.status === "active" ? "处理中" : "已恢复"} · ${formatTime(alarm.started_at)}`}
                          />
                        </List.Item>
                      )}
                    />
                  </Card>
                </Col>
              </Row>

              <Row gutter={[16, 16]}>
                <Col xs={24} xl={12}>
                  <Card title="Lot 良率趋势">
                    <YieldTrendChart data={dashboard.yield_trend} />
                  </Card>
                </Col>
                <Col xs={24} xl={12}>
                  <Card title="最新 Lot Bin 分布">
                    <BinChart data={dashboard.bin_distribution} />
                  </Card>
                </Col>
              </Row>

              <Row gutter={[16, 16]}>
                <Col xs={24} xl={14}>
                  <Card title="SPC 控制图">
                    <SpcChart data={spc} />
                  </Card>
                </Col>
                <Col xs={24} xl={10}>
                  <Card title="最新遥测">
                    <List
                      dataSource={dashboard.latest_metrics}
                      renderItem={(metric) => (
                        <List.Item>
                          <Space direction="vertical" size={0}>
                            <Text strong>
                              {metric.device_code} · {metric.metric_name}
                            </Text>
                            <Text type="secondary">
                              {metric.metric_value.toFixed(2)} · {formatTime(metric.time)}
                            </Text>
                          </Space>
                        </List.Item>
                      )}
                    />
                  </Card>
                </Col>
              </Row>
            </Space>
          )}
        </Content>
      </Layout>
    </ConfigProvider>
  );
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
