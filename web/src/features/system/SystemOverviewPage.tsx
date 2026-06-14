import { ReloadOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Col, Descriptions, List, Row, Space, Spin, Statistic, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { useCallback, useEffect, useState } from "react";
import { api } from "../../shared/api/client";
import { formatDateTime } from "../../shared/format";
import type { SystemOverview, SystemServiceStatus } from "../../shared/types";

const { Text, Title } = Typography;

const serviceColor: Record<SystemServiceStatus["status"], string> = {
  ok: "green",
  stale: "gold",
  no_data: "default",
  error: "red",
};

const serviceLabel: Record<SystemServiceStatus["status"], string> = {
  ok: "正常",
  stale: "延迟",
  no_data: "无数据",
  error: "异常",
};

type TableCount = SystemOverview["table_counts"][number];

export function SystemOverviewPage() {
  const [overview, setOverview] = useState<SystemOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (showLoading: boolean) => {
    try {
      if (showLoading) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }
      setOverview(await api.systemOverview());
      setError(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "加载系统状态失败");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    load(true);
    const timer = window.setInterval(() => load(false), 15000);
    return () => window.clearInterval(timer);
  }, [load]);

  const tableColumns: ColumnsType<TableCount> = [
    { title: "表名", dataIndex: "table_name" },
    { title: "行数", dataIndex: "row_count" },
  ];

  if (loading) {
    return (
      <div className="loading">
        <Spin size="large" />
      </div>
    );
  }

  if (error || !overview) {
    return <Alert type="error" message="系统状态加载失败" description={error ?? "请稍后重试。"} showIcon />;
  }

  return (
    <Space direction="vertical" size={18} className="stack">
      <div className="page-toolbar">
        <Space direction="vertical" size={4}>
          <Title level={3}>系统运营</Title>
          <Text type="secondary">查看核心服务状态、遥测入库延迟、数据规模和近期吞吐。</Text>
        </Space>
        <Button icon={<ReloadOutlined />} loading={refreshing} onClick={() => load(false)}>
          刷新
        </Button>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={12} xl={4}>
          <Card>
            <Statistic title="设备总数" value={overview.summary.device_count} />
          </Card>
        </Col>
        <Col xs={12} xl={4}>
          <Card>
            <Statistic title="活动告警" value={overview.summary.active_alarm_count} valueStyle={{ color: "#dc2626" }} />
          </Card>
        </Col>
        <Col xs={12} xl={4}>
          <Card>
            <Statistic title="已确认告警" value={overview.summary.acknowledged_alarm_count} valueStyle={{ color: "#ca8a04" }} />
          </Card>
        </Col>
        <Col xs={12} xl={4}>
          <Card>
            <Statistic title="遥测点数" value={overview.summary.telemetry_count} />
          </Card>
        </Col>
        <Col xs={12} xl={4}>
          <Card>
            <Statistic
              title="入库延迟"
              value={overview.summary.telemetry_lag_seconds ?? 0}
              suffix="秒"
              valueStyle={{ color: (overview.summary.telemetry_lag_seconds ?? 999) > 120 ? "#dc2626" : "#15803d" }}
            />
          </Card>
        </Col>
        <Col xs={12} xl={4}>
          <Card>
            <Statistic title="离线设备" value={overview.summary.offline_count} valueStyle={{ color: "#64748b" }} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} xl={12}>
          <Card title="服务状态">
            <List
              dataSource={overview.services}
              renderItem={(service) => (
                <List.Item>
                  <List.Item.Meta
                    title={
                      <Space>
                        <Text strong>{service.name}</Text>
                        <Tag color={serviceColor[service.status]}>{serviceLabel[service.status]}</Tag>
                      </Space>
                    }
                    description={service.detail}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col xs={24} xl={12}>
          <Card title="最近入库设备">
            <Descriptions column={1} size="small" bordered>
              {overview.recent_device_ingestion.map((item) => (
                <Descriptions.Item key={item.device_code} label={item.device_code}>
                  {item.point_count} 点 · {formatDateTime(item.latest_time)}
                </Descriptions.Item>
              ))}
            </Descriptions>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} xl={12}>
          <Card title="近 15 分钟指标吞吐">
            <List
              dataSource={overview.metric_ingestion}
              renderItem={(item) => (
                <List.Item>
                  <Text>{item.metric_name}</Text>
                  <Text strong>{item.point_count}</Text>
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col xs={24} xl={12}>
          <Card title="数据表规模">
            <Table<TableCount>
              rowKey="table_name"
              columns={tableColumns}
              dataSource={overview.table_counts}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </Space>
  );
}
