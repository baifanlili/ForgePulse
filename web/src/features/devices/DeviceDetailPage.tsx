import { ArrowLeftOutlined, ReloadOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Descriptions, List, Select, Space, Spin, Typography } from "antd";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../../shared/api/client";
import { TelemetryChart } from "../../shared/charts/TelemetryChart";
import { formatDateTime } from "../../shared/format";
import { AlarmSeverityTag, AlarmStatusTag, DeviceStatusTag } from "../../shared/status";
import type { DeviceDetail, DeviceTelemetry } from "../../shared/types";

const { Text, Title } = Typography;

export function DeviceDetailPage() {
  const { deviceCode = "" } = useParams();
  const [detail, setDetail] = useState<DeviceDetail | null>(null);
  const [telemetry, setTelemetry] = useState<DeviceTelemetry | null>(null);
  const [metricName, setMetricName] = useState<string | undefined>();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedMetric = useMemo(
    () => metricName ?? telemetry?.metrics[0],
    [metricName, telemetry?.metrics],
  );

  const load = useCallback(async (showLoading: boolean, nextMetric?: string) => {
    try {
      if (showLoading) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }
      const detailData = await api.deviceDetail(deviceCode);
      const metric = nextMetric ?? metricName ?? detailData.latest_metrics[0]?.metric_name;
      const telemetryData = await api.deviceTelemetry(deviceCode, metric);
      setDetail(detailData);
      setTelemetry(telemetryData);
      setMetricName(metric);
      setError(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "加载设备详情失败");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [deviceCode, metricName]);

  useEffect(() => {
    load(true);
  }, [load]);

  if (loading) {
    return (
      <div className="loading">
        <Spin size="large" />
      </div>
    );
  }

  if (error || !detail || !telemetry) {
    return <Alert type="error" message="设备详情加载失败" description={error ?? "请稍后重试。"} showIcon />;
  }

  return (
    <Space direction="vertical" size={18} className="stack">
      <div className="page-toolbar">
        <Space direction="vertical" size={4}>
          <Link to="/dashboard"><ArrowLeftOutlined /> 返回运行总览</Link>
          <Title level={3}>{detail.device.device_name}</Title>
          <Text type="secondary">{detail.device.device_code}</Text>
        </Space>
        <Button icon={<ReloadOutlined />} loading={refreshing} onClick={() => load(false)}>
          刷新
        </Button>
      </div>

      <Card title="设备画像">
        <Descriptions column={{ xs: 1, md: 2, xl: 3 }} bordered size="small">
          <Descriptions.Item label="设备编码">{detail.device.device_code}</Descriptions.Item>
          <Descriptions.Item label="设备类型">{detail.device.device_type}</Descriptions.Item>
          <Descriptions.Item label="状态"><DeviceStatusTag status={detail.device.status} /></Descriptions.Item>
          <Descriptions.Item label="区域">{detail.device.area}</Descriptions.Item>
          <Descriptions.Item label="产线">{detail.device.line}</Descriptions.Item>
          <Descriptions.Item label="最近心跳">{formatDateTime(detail.device.last_heartbeat_at ?? "")}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card
        title="遥测趋势"
        extra={
          <Select
            value={selectedMetric}
            style={{ width: 180 }}
            options={telemetry.metrics.map((metric) => ({ value: metric, label: metric }))}
            onChange={(value) => {
              setMetricName(value);
              load(false, value);
            }}
          />
        }
      >
        <TelemetryChart data={telemetry.points} />
      </Card>

      <Card title="设备告警">
        <List
          dataSource={detail.alarms}
          locale={{ emptyText: "暂无告警" }}
          renderItem={(alarm) => (
            <List.Item>
              <List.Item.Meta
                title={
                  <Space wrap>
                    {alarm.severity && <AlarmSeverityTag severity={alarm.severity} />}
                    <Text strong>{alarm.title}</Text>
                    {alarm.status && <AlarmStatusTag status={alarm.status} />}
                  </Space>
                }
                description={
                  <Space direction="vertical" size={2}>
                    <Text>{alarm.description}</Text>
                    <Text type="secondary">开始于 {formatDateTime(alarm.started_at ?? "")}</Text>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </Card>
    </Space>
  );
}
