import { Tag } from "antd";
import type { AlarmSeverity, AlarmStatus, DeviceStatus } from "./types";

export const statusLabel: Record<DeviceStatus, string> = {
  running: "运行中",
  warning: "预警",
  offline: "离线",
};

export const statusColor: Record<DeviceStatus, string> = {
  running: "green",
  warning: "gold",
  offline: "default",
};

export const severityColor: Record<AlarmSeverity, string> = {
  critical: "red",
  warning: "gold",
  info: "blue",
};

export function DeviceStatusTag({ status }: { status: DeviceStatus }) {
  return <Tag color={statusColor[status]}>{statusLabel[status]}</Tag>;
}

export function AlarmSeverityTag({ severity }: { severity: AlarmSeverity }) {
  return <Tag color={severityColor[severity]}>{severity.toUpperCase()}</Tag>;
}

export function AlarmStatusTag({ status }: { status: AlarmStatus }) {
  const config: Record<AlarmStatus, { color: string; label: string }> = {
    active: { color: "red", label: "待处理" },
    acknowledged: { color: "gold", label: "已确认" },
    cleared: { color: "green", label: "已关闭" },
  };
  return <Tag color={config[status].color}>{config[status].label}</Tag>;
}
