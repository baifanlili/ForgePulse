"""
ForgePulse API 测试脚本
运行：python tests/test_api.py
目标：验证所有 API 端点的响应结构和数据正确性
"""

import json
import os
import sys
import traceback

try:
    import requests
except ImportError:
    print("请先安装 requests: pip install requests")
    sys.exit(1)

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
PASSED = 0
FAILED = 0


def assert_status(resp, expected, label=""):
    global PASSED, FAILED
    if resp.status_code == expected:
        PASSED += 1
        print(f"  PASS [{resp.status_code}] {label}")
    else:
        FAILED += 1
        print(f"  FAIL [{resp.status_code} expected {expected}] {label} — {resp.text[:200]}")


def assert_field(obj, field, label=""):
    global PASSED, FAILED
    if field in obj:
        PASSED += 1
        print(f"  PASS field '{field}' {label}")
    else:
        FAILED += 1
        print(f"  FAIL field '{field}' missing {label}")


def assert_type(obj, field, expected_type, label=""):
    global PASSED, FAILED
    if field not in obj:
        FAILED += 1
        print(f"  FAIL field '{field}' missing {label}")
        return
    value = obj[field]
    types = expected_type if isinstance(expected_type, tuple) else (expected_type,)
    if isinstance(value, types):
        PASSED += 1
        type_name = "|".join(t.__name__ for t in types)
        print(f"  PASS type({field})={type_name} {label}")
    else:
        FAILED += 1
        type_name = "|".join(t.__name__ for t in types)
        print(f"  FAIL type({field})={type(value).__name__} expected {type_name} {label}")


def test_health():
    print("\n[health]")
    resp = requests.get(f"{API_BASE}/health", timeout=10)
    assert_status(resp, 200)
    data = resp.json()
    assert_field(data, "status")
    assert_field(data, "service")
    assert data["status"] == "ok"


def test_dashboard():
    print("\n[dashboard]")
    resp = requests.get(f"{API_BASE}/api/dashboard", timeout=10)
    assert_status(resp, 200)
    data = resp.json()
    assert_field(data, "summary")
    assert_field(data, "latest_metrics")
    assert_field(data, "recent_alarms")
    assert_field(data, "yield_trend")
    assert_field(data, "bin_distribution")
    s = data["summary"]
    assert_type(s, "device_count", int)
    assert_type(s, "active_alarm_count", int)
    assert_type(s, "average_yield", (int, float))
    if data["latest_metrics"]:
        m = data["latest_metrics"][0]
        assert_field(m, "device_code")
        assert_field(m, "metric_name")
        assert_field(m, "metric_value")


def test_devices():
    print("\n[devices]")
    resp = requests.get(f"{API_BASE}/api/devices", timeout=10)
    assert_status(resp, 200)
    devices = resp.json()
    assert isinstance(devices, list), "devices should be list"
    if devices:
        d = devices[0]
        assert_field(d, "device_code")
        assert_field(d, "device_name")
        assert_field(d, "status")

        # 设备详情
        dc = d["device_code"]
        resp2 = requests.get(f"{API_BASE}/api/devices/{dc}", timeout=10)
        assert_status(resp2, 200)
        detail = resp2.json()
        assert_field(detail, "device")
        assert_field(detail, "latest_metrics")
        assert_field(detail, "alarms")

        # 设备遥测
        resp3 = requests.get(
            f"{API_BASE}/api/devices/{dc}/telemetry",
            params={"hours": 1, "limit": 10},
            timeout=10,
        )
        assert_status(resp3, 200)
        tele = resp3.json()
        assert_field(tele, "device_code")
        assert_field(tele, "points")
        assert_field(tele, "metrics")
        assert isinstance(tele["points"], list)


def test_alarms():
    print("\n[alarms]")
    resp = requests.get(f"{API_BASE}/api/alarms", params={"limit": 10}, timeout=10)
    assert_status(resp, 200)
    alarms = resp.json()
    assert isinstance(alarms, list)
    if alarms:
        a = alarms[0]
        assert_field(a, "alarm_code")
        assert_field(a, "severity")
        assert_field(a, "status")

        # 告警详情
        ac = a["alarm_code"]
        resp2 = requests.get(f"{API_BASE}/api/alarms/{ac}", timeout=10)
        assert_status(resp2, 200)
        detail = resp2.json()
        assert_field(detail, "alarm")
        assert_field(detail, "events")
        assert isinstance(detail["events"], list)

        # 告警确认（仅对 active 告警）
        if a["status"] == "active":
            resp3 = requests.patch(
                f"{API_BASE}/api/alarms/{ac}/acknowledge",
                json={"operator": "test-script", "note": "自动化测试确认"},
                timeout=10,
            )
            assert_status(resp3, 200)
            ack = resp3.json()
            assert ack["alarm"]["status"] == "acknowledged"

            # 告警关闭
            resp4 = requests.patch(
                f"{API_BASE}/api/alarms/{ac}/clear",
                json={"operator": "test-script", "note": "自动化测试关闭"},
                timeout=10,
            )
            assert_status(resp4, 200)
            cleared = resp4.json()
            assert cleared["alarm"]["status"] == "cleared"


def test_analytics():
    print("\n[analytics]")
    resp = requests.get(f"{API_BASE}/api/analytics/yield", timeout=10)
    assert_status(resp, 200)
    data = resp.json()
    assert_field(data, "lots")
    assert_field(data, "wafers")
    assert_field(data, "bins")

    resp2 = requests.get(f"{API_BASE}/api/analytics/spc", timeout=10)
    assert_status(resp2, 200)
    spc = resp2.json()
    assert isinstance(spc, list)
    if spc:
        s = spc[0]
        assert_field(s, "sample_time")
        assert_field(s, "value")
        assert_field(s, "center_line")
        assert_field(s, "upper_control_limit")
        assert_field(s, "lower_control_limit")


def test_system():
    print("\n[system]")
    resp = requests.get(f"{API_BASE}/api/system/overview", timeout=10)
    assert_status(resp, 200)
    data = resp.json()
    assert_field(data, "services")
    assert_field(data, "summary")
    assert_field(data, "recent_device_ingestion")
    assert_field(data, "metric_ingestion")
    assert_field(data, "table_counts")

    services = {s["name"]: s for s in data["services"]}
    assert "platform-api" in services
    assert "postgres" in services
    assert "stream-worker" in services

    # 验证 worker 健康字段
    worker = data.get("worker")
    if worker:
        assert_field(worker, "worker_id")
        assert_field(worker, "telemetry_processed")
        assert_field(worker, "lag_seconds")


def test_edge():
    print("\n[edge]")
    resp = requests.get(f"{API_BASE}/api/edge/gateways", timeout=10)
    assert_status(resp, 200)
    gateways = resp.json()
    assert isinstance(gateways, list)

    if gateways:
        g = gateways[0]
        assert_field(g, "gateway_id")
        assert_field(g, "telemetry_point_count")

        # 命令列表
        gid = g["gateway_id"]
        resp2 = requests.get(
            f"{API_BASE}/api/edge/gateways/{gid}/commands", timeout=10
        )
        assert_status(resp2, 200)
        commands = resp2.json()
        assert isinstance(commands, list)
        if commands:
            c = commands[0]
            assert_field(c, "command_id")
            assert_field(c, "status")
            assert "executed_at" in c or "executed_at" not in c  # field exists

        # 下发命令
        resp3 = requests.post(
            f"{API_BASE}/api/edge/gateways/{gid}/commands",
            json={
                "command_type": "set_interval",
                "parameters": {"interval_seconds": 5},
                "operator": "test-script",
            },
            timeout=10,
        )
        assert_status(resp3, 200)
        cmd = resp3.json()
        assert_field(cmd, "command_id")
        assert cmd["status"] == "published"
        assert_field(cmd, "executed_at")


def main():
    global PASSED, FAILED

    print(f"ForgePulse API 测试 — 目标: {API_BASE}")
    print("=" * 60)

    tests = [
        test_health,
        test_dashboard,
        test_devices,
        test_alarms,
        test_analytics,
        test_system,
        test_edge,
    ]

    for test_fn in tests:
        try:
            test_fn()
        except requests.exceptions.ConnectionError:
            FAILED += 1
            print(f"  FAIL 无法连接到 API ({API_BASE})，请确保服务已启动")
            break
        except Exception as exc:
            FAILED += 1
            print(f"  FAIL {test_fn.__name__}: {exc}")
            traceback.print_exc()

    print("\n" + "=" * 60)
    total = PASSED + FAILED
    print(f"结果: {PASSED}/{total} 通过, {FAILED} 失败")
    if FAILED == 0:
        print("全部测试通过！")
    else:
        print(f"{FAILED} 个测试失败")
    return FAILED


if __name__ == "__main__":
    sys.exit(main())
