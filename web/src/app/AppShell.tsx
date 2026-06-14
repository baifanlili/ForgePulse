import { AlertOutlined, ApiOutlined, DashboardOutlined, DeploymentUnitOutlined, MonitorOutlined } from "@ant-design/icons";
import { Layout, Menu, Space, Tag, Typography } from "antd";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

const { Header, Content, Sider } = Layout;
const { Text, Title } = Typography;

export function AppShell() {
  const navigate = useNavigate();
  const location = useLocation();
  const selectedKey = location.pathname.startsWith("/devices") ? "/dashboard" : location.pathname;

  return (
    <Layout className="app">
      <Sider className="sidebar" width={232} breakpoint="lg" collapsedWidth={0}>
        <div className="sidebar-brand">
          <Text className="brand">ForgePulse</Text>
          <Text className="sidebar-title">工业数据平台</Text>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={[
            { key: "/dashboard", icon: <DashboardOutlined />, label: "运行总览" },
            { key: "/alarms", icon: <AlertOutlined />, label: "告警中心" },
            { key: "/edge", icon: <ApiOutlined />, label: "边缘网关" },
            { key: "/system", icon: <MonitorOutlined />, label: "系统运营" },
            { key: "devices", icon: <DeploymentUnitOutlined />, label: "设备监控", disabled: true },
          ]}
          onClick={(item) => navigate(item.key)}
        />
      </Sider>
      <Layout>
        <Header className="topbar">
          <div>
            <Title level={3}>半导体设备数据平台</Title>
            <Text type="secondary">设备遥测、告警、良率与 SPC 的实时运营工作台</Text>
          </div>
          <Space wrap>
            <Tag color="cyan">MVP 数据闭环</Tag>
            <Tag color="blue">Docker Compose</Tag>
          </Space>
        </Header>
        <Content className="content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
