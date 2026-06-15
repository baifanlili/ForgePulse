import { ConfigProvider } from "antd";
import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "../shared/auth";
import { AppShell } from "./AppShell";
import { AlarmCenterPage } from "../features/alarms/AlarmCenterPage";
import { DashboardPage } from "../features/dashboard/DashboardPage";
import { DeviceDetailPage } from "../features/devices/DeviceDetailPage";
import { EdgeGatewayPage } from "../features/edge/EdgeGatewayPage";
import { SystemOverviewPage } from "../features/system/SystemOverviewPage";
import { LoginPage } from "../features/auth/LoginPage";

function ProtectedRoutes() {
  const { isLoggedIn } = useAuth();
  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/alarms" element={<AlarmCenterPage />} />
        <Route path="/edge" element={<EdgeGatewayPage />} />
        <Route path="/system" element={<SystemOverviewPage />} />
        <Route path="/devices/:deviceCode" element={<DeviceDetailPage />} />
      </Route>
    </Routes>
  );
}

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
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/*" element={<ProtectedRoutes />} />
        </Routes>
      </AuthProvider>
    </ConfigProvider>
  );
}
