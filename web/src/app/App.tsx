import { ConfigProvider } from "antd";
import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./AppShell";
import { AlarmCenterPage } from "../features/alarms/AlarmCenterPage";
import { DashboardPage } from "../features/dashboard/DashboardPage";
import { DeviceDetailPage } from "../features/devices/DeviceDetailPage";

export function App() {
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
      <Routes>
        <Route element={<AppShell />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/alarms" element={<AlarmCenterPage />} />
          <Route path="/devices/:deviceCode" element={<DeviceDetailPage />} />
        </Route>
      </Routes>
    </ConfigProvider>
  );
}
