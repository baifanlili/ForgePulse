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
  return <Tag color={status === "active" ? "red" : "green"}>{status === "active" ? "处理中" : "已恢复"}</Tag>;
}
