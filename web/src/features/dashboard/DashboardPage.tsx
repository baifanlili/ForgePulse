import { ReloadOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Col, List, Row, Space, Spin, Statistic, Table, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../shared/api/client";
import { BinChart } from "../../shared/charts/BinChart";
import { SpcChart } from "../../shared/charts/SpcChart";
import { YieldTrendChart } from "../../shared/charts/YieldTrendChart";
import { formatTime } from "../../shared/format";
import { AlarmSeverityTag, AlarmStatusTag, DeviceStatusTag } from "../../shared/status";
import type { DashboardData, Device, SpcPoint } from "../../shared/types";

const { Text } = Typography;

export function DashboardPage() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [devices, setDevices] = useState<Device[]>([]);
  const [spc, setSpc] = useState<SpcPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (showLoading: boolean) => {
    try {
      if (showLoading) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }
      const [dashboardData, devicesData, spcData] = await Promise.all([
        api.dashboard(),
        api.devices(),
        api.spc(),
      ]);
      setDashboard(dashboardData);
      setDevices(devicesData);
      setSpc(spcData);
      setLastUpdatedAt(new Date().toISOString());
      setError(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "加载数据失败");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    load(true);
    const timer = window.setInterval(() => load(false), 10000);
    return () => window.clearInterval(timer);
  }, [load]);

  const columns: ColumnsType<Device> = [
    {
      title: "设备",
      dataIndex: "device_name",
      render: (name, row) => (
        <Space direction="vertical" size={0}>
          <Link to={`/devices/${row.device_code}`}>{name}</Link>
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
      render: (status) => <DeviceStatusTag status={status} />,
    },
    {
      title: "最近心跳",
      dataIndex: "last_heartbeat_at",
      render: (value: string) => formatTime(value),
    },
  ];

  if (loading) {
    return (
      <div className="loading">
        <Spin size="large" />
      </div>
    );
  }

  if (error || !dashboard) {
    return (
      <Alert
        type="error"
        message="仪表盘数据加载失败"
        description={error ?? "请确认 platform-api 已启动。"}
        showIcon
      />
    );
  }

  return (
    <Space direction="vertical" size={18} className="stack">
      <div className="page-toolbar">
        <Space wrap>
          {lastUpdatedAt ? <Text type="secondary">更新于 {formatTime(lastUpdatedAt)}</Text> : null}
        </Space>
        <Button icon={<ReloadOutlined />} loading={refreshing} onClick={() => load(false)}>
          刷新
        </Button>
      </div>

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
            <Table<Device> rowKey="device_code" columns={columns} dataSource={devices} pagination={false} size="middle" />
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
                        <AlarmSeverityTag severity={alarm.severity} />
                        <Text strong>{alarm.title}</Text>
                      </Space>
                    }
                    description={
                      <Space wrap>
                        <Link to={`/devices/${alarm.device_code}`}>{alarm.device_code}</Link>
                        <AlarmStatusTag status={alarm.status} />
                        <Text type="secondary">{formatTime(alarm.started_at)}</Text>
                      </Space>
                    }
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
                    <Link to={`/devices/${metric.device_code}`}>{metric.device_code} · {metric.metric_name}</Link>
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
  );
}
