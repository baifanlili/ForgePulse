import { AlertOutlined, ControlOutlined, PauseCircleOutlined, PlayCircleOutlined, ThunderboltOutlined } from "@ant-design/icons";
import { Button, Card, Col, Empty, InputNumber, List, Row, Space, Statistic, Table, Tag, Typography, message } from "antd";
import { useEffect, useMemo, useState } from "react";

import { api } from "../../shared/api/client";
import { formatDateTime } from "../../shared/format";
import type { EdgeCommand, EdgeGateway } from "../../shared/types";

const { Text, Title } = Typography;

function qualityColor(quality?: string | null) {
  if (quality === "degraded") {
    return "orange";
  }
  if (quality === "good") {
    return "green";
  }
  return "default";
}

export function EdgeGatewayPage() {
  const [gateways, setGateways] = useState<EdgeGateway[]>([]);
  const [commands, setCommands] = useState<EdgeCommand[]>([]);
  const [selectedGatewayId, setSelectedGatewayId] = useState("");
  const [intervalSeconds, setIntervalSeconds] = useState(5);
  const [loading, setLoading] = useState(false);
  const [commandLoading, setCommandLoading] = useState("");

  const selectedGateway = useMemo(
    () => gateways.find((gateway) => gateway.gateway_id === selectedGatewayId) ?? gateways[0],
    [gateways, selectedGatewayId],
  );

  async function load() {
    const data = await api.edgeGateways();
    setGateways(data);
    const nextGatewayId = selectedGatewayId || data[0]?.gateway_id || "";
    setSelectedGatewayId(nextGatewayId);
    if (nextGatewayId) {
      setCommands(await api.edgeCommands(nextGatewayId));
    }
  }

  useEffect(() => {
    setLoading(true);
    load()
      .catch((error) => message.error(error instanceof Error ? error.message : "边缘网关数据加载失败"))
      .finally(() => setLoading(false));

    const timer = window.setInterval(() => {
      load().catch(() => undefined);
    }, 8000);
    return () => window.clearInterval(timer);
  }, []);

  async function sendCommand(commandType: EdgeCommand["command_type"], parameters: Record<string, unknown> = {}) {
    if (!selectedGateway) {
      return;
    }
    setCommandLoading(commandType);
    try {
      await api.sendEdgeCommand(selectedGateway.gateway_id, commandType, parameters);
      message.success("命令已下发到边缘网关");
      await load();
    } catch (error) {
      message.error(error instanceof Error ? error.message : "命令下发失败");
    } finally {
      setCommandLoading("");
    }
  }

  return (
    <Space direction="vertical" size={20} style={{ width: "100%" }}>
      <div>
        <Title level={3}>边缘网关</Title>
        <Text type="secondary">查看 C++ 网关状态，并通过 MQTT command topic 下发运行控制命令。</Text>
      </div>

      {selectedGateway ? (
        <>
          <Row gutter={[16, 16]}>
            <Col xs={24} md={6}>
              <Card>
                <Statistic title="网关" value={selectedGateway.gateway_id} />
                <Text type="secondary">{selectedGateway.line_id ?? "未上报产线"}</Text>
              </Card>
            </Col>
            <Col xs={24} md={6}>
              <Card>
                <Statistic title="最新序列号" value={selectedGateway.latest_sequence ?? 0} />
                <Text type="secondary">{formatDateTime(selectedGateway.latest_seen_at)}</Text>
              </Card>
            </Col>
            <Col xs={24} md={6}>
              <Card>
                <Statistic title="采样周期" value={(selectedGateway.sample_period_ms ?? 0) / 1000} suffix="秒" />
                <Text type="secondary">来自 C++ payload</Text>
              </Card>
            </Col>
            <Col xs={24} md={6}>
              <Card>
                <Statistic title="质量异常点" value={selectedGateway.degraded_point_count} />
                <Tag color={qualityColor(selectedGateway.latest_quality)}>{selectedGateway.latest_quality ?? "unknown"}</Tag>
              </Card>
            </Col>
          </Row>

          <Card title="控制台" loading={loading}>
            <Space wrap>
              <Button icon={<PauseCircleOutlined />} loading={commandLoading === "pause"} onClick={() => sendCommand("pause")}>
                暂停上报
              </Button>
              <Button type="primary" icon={<PlayCircleOutlined />} loading={commandLoading === "resume"} onClick={() => sendCommand("resume")}>
                恢复上报
              </Button>
              <InputNumber min={1} max={60} value={intervalSeconds} onChange={(value) => setIntervalSeconds(value ?? 5)} />
              <Button
                icon={<ControlOutlined />}
                loading={commandLoading === "set_interval"}
                onClick={() => sendCommand("set_interval", { interval_seconds: intervalSeconds })}
              >
                更新采样周期
              </Button>
              <Button danger icon={<ThunderboltOutlined />} loading={commandLoading === "inject_fault"} onClick={() => sendCommand("inject_fault", { fault_cycles: 6 })}>
                注入故障
              </Button>
            </Space>
          </Card>

          <Row gutter={[16, 16]}>
            <Col xs={24} xl={10}>
              <Card title="网关列表">
                <List
                  dataSource={gateways}
                  renderItem={(gateway) => (
                    <List.Item
                      actions={[
                        <Button key="select" type="link" onClick={() => setSelectedGatewayId(gateway.gateway_id)}>
                          选择
                        </Button>,
                      ]}
                    >
                      <List.Item.Meta
                        avatar={<AlertOutlined />}
                        title={gateway.gateway_id}
                        description={`${gateway.line_id ?? "unknown"} · ${gateway.telemetry_point_count} 个遥测点`}
                      />
                      <Tag color={qualityColor(gateway.latest_quality)}>{gateway.latest_quality ?? "unknown"}</Tag>
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
            <Col xs={24} xl={14}>
              <Card title="命令记录">
                <Table
                  rowKey="command_id"
                  size="small"
                  dataSource={commands}
                  pagination={{ pageSize: 6 }}
                  columns={[
                    { title: "命令", dataIndex: "command_type" },
                    { title: "状态", dataIndex: "status", render: (value) => <Tag color="blue">{value}</Tag> },
                    { title: "操作人", dataIndex: "operator" },
                    { title: "发布时间", dataIndex: "published_at", render: (value) => formatDateTime(value) },
                  ]}
                  locale={{ emptyText: <Empty description="暂无命令" /> }}
                />
              </Card>
            </Col>
          </Row>
        </>
      ) : (
        <Card>
          <Empty description="还没有发现边缘网关遥测" />
        </Card>
      )}
    </Space>
  );
}
