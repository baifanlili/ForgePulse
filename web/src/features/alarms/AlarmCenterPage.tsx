import { CheckCircleOutlined, ReloadOutlined, StopOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Descriptions, Drawer, Input, List, Select, Space, Spin, Table, Timeline, Typography, message } from "antd";
import type { ColumnsType } from "antd/es/table";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../shared/api/client";
import { formatDateTime } from "../../shared/format";
import { AlarmSeverityTag, AlarmStatusTag } from "../../shared/status";
import type { Alarm, AlarmDetail, AlarmStatus } from "../../shared/types";

const { Text, Title } = Typography;

export function AlarmCenterPage() {
  const [alarms, setAlarms] = useState<Alarm[]>([]);
  const [status, setStatus] = useState<AlarmStatus | "all">("all");
  const [selected, setSelected] = useState<AlarmDetail | null>(null);
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [acting, setActing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (showLoading: boolean) => {
    try {
      if (showLoading) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }
      setAlarms(await api.alarms({ status }));
      setError(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "加载告警失败");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [status]);

  const openDetail = useCallback(async (alarmCode: string) => {
    try {
      setSelected(await api.alarmDetail(alarmCode));
      setNote("");
    } catch (caught) {
      message.error(caught instanceof Error ? caught.message : "加载告警详情失败");
    }
  }, []);

  const runAction = useCallback(async (action: "acknowledge" | "clear") => {
    if (!selected) {
      return;
    }
    try {
      setActing(true);
      const detail = action === "acknowledge"
        ? await api.acknowledgeAlarm(selected.alarm.alarm_code, note)
        : await api.clearAlarm(selected.alarm.alarm_code, note);
      setSelected(detail);
      setNote("");
      await load(false);
      message.success(action === "acknowledge" ? "告警已确认" : "告警已关闭");
    } catch (caught) {
      message.error(caught instanceof Error ? caught.message : "操作失败");
    } finally {
      setActing(false);
    }
  }, [load, note, selected]);

  useEffect(() => {
    load(true);
  }, [load]);

  const columns: ColumnsType<Alarm> = [
    {
      title: "告警",
      dataIndex: "title",
      render: (title, row) => (
        <Space direction="vertical" size={0}>
          <Button type="link" className="table-link-button" onClick={() => openDetail(row.alarm_code)}>
            {title}
          </Button>
          <Text type="secondary">{row.alarm_code}</Text>
        </Space>
      ),
    },
    {
      title: "等级",
      dataIndex: "severity",
      render: (severity) => <AlarmSeverityTag severity={severity} />,
    },
    {
      title: "状态",
      dataIndex: "status",
      render: (alarmStatus) => <AlarmStatusTag status={alarmStatus} />,
    },
    {
      title: "设备",
      dataIndex: "device_code",
      render: (deviceCode) => <Link to={`/devices/${deviceCode}`}>{deviceCode}</Link>,
    },
    {
      title: "开始时间",
      dataIndex: "started_at",
      render: (value) => formatDateTime(value),
    },
    {
      title: "负责人",
      dataIndex: "acknowledged_by",
      render: (value) => value || "-",
    },
  ];

  if (loading) {
    return (
      <div className="loading">
        <Spin size="large" />
      </div>
    );
  }

  return (
    <Space direction="vertical" size={18} className="stack">
      <div className="page-toolbar">
        <Space direction="vertical" size={4}>
          <Title level={3}>告警中心</Title>
          <Text type="secondary">处理活动告警、记录确认与关闭操作，形成可追溯的运维闭环。</Text>
        </Space>
        <Space wrap>
          <Select
            value={status}
            style={{ width: 140 }}
            options={[
              { value: "all", label: "全部状态" },
              { value: "active", label: "待处理" },
              { value: "acknowledged", label: "已确认" },
              { value: "cleared", label: "已关闭" },
            ]}
            onChange={setStatus}
          />
          <Button icon={<ReloadOutlined />} loading={refreshing} onClick={() => load(false)}>
            刷新
          </Button>
        </Space>
      </div>

      {error ? <Alert type="error" message="告警加载失败" description={error} showIcon /> : null}

      <Card>
        <Table<Alarm>
          rowKey="alarm_code"
          columns={columns}
          dataSource={alarms}
          pagination={{ pageSize: 12 }}
          size="middle"
        />
      </Card>

      <Drawer
        width={640}
        title="告警详情"
        open={Boolean(selected)}
        onClose={() => setSelected(null)}
        extra={
          selected ? (
            <Space>
              <Button
                icon={<CheckCircleOutlined />}
                disabled={selected.alarm.status !== "active"}
                loading={acting}
                onClick={() => runAction("acknowledge")}
              >
                确认
              </Button>
              <Button
                danger
                icon={<StopOutlined />}
                disabled={selected.alarm.status === "cleared"}
                loading={acting}
                onClick={() => runAction("clear")}
              >
                关闭
              </Button>
            </Space>
          ) : null
        }
      >
        {selected ? (
          <Space direction="vertical" size={16} className="stack">
            <Descriptions bordered column={1} size="small">
              <Descriptions.Item label="告警编码">{selected.alarm.alarm_code}</Descriptions.Item>
              <Descriptions.Item label="标题">{selected.alarm.title}</Descriptions.Item>
              <Descriptions.Item label="设备">
                <Link to={`/devices/${selected.alarm.device_code}`}>{selected.alarm.device_code}</Link>
              </Descriptions.Item>
              <Descriptions.Item label="等级"><AlarmSeverityTag severity={selected.alarm.severity} /></Descriptions.Item>
              <Descriptions.Item label="状态"><AlarmStatusTag status={selected.alarm.status} /></Descriptions.Item>
              <Descriptions.Item label="说明">{selected.alarm.description}</Descriptions.Item>
              <Descriptions.Item label="开始时间">{formatDateTime(selected.alarm.started_at)}</Descriptions.Item>
              <Descriptions.Item label="确认人">{selected.alarm.acknowledged_by || "-"}</Descriptions.Item>
              <Descriptions.Item label="关闭人">{selected.alarm.cleared_by || "-"}</Descriptions.Item>
            </Descriptions>

            <Input.TextArea
              rows={3}
              value={note}
              onChange={(event) => setNote(event.target.value)}
              placeholder="填写处理备注，例如：已通知现场工程师检查冷却水流量。"
            />

            <Card title="处理轨迹" size="small">
              <Timeline
                items={selected.events.map((event) => ({
                  children: (
                    <Space direction="vertical" size={2}>
                      <Text strong>{event.event_type}</Text>
                      <Text>{event.note || "无备注"}</Text>
                      <Text type="secondary">{event.operator} · {formatDateTime(event.created_at)}</Text>
                    </Space>
                  ),
                }))}
              />
            </Card>
          </Space>
        ) : null}
      </Drawer>
    </Space>
  );
}
