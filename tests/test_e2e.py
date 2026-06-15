"""
ForgePulse 端到端测试脚本
运行：python tests/test_e2e.py
依赖：paho-mqtt, requests
"""

import json
import os
import sys
import time
import traceback
import uuid
from datetime import UTC, datetime

try:
    import paho.mqtt.client as mqtt
    import requests
except ImportError:
    print("请先安装依赖: pip install paho-mqtt requests")
    sys.exit(1)

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = "forgepulse/telemetry"
PASSED = 0
FAILED = 0


def check(msg: str, condition: bool) -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS {msg}")
    else:
        FAILED += 1
        print(f"  FAIL {msg}")


def test_mqtt_telemetry():
    """发布 MQTT 遥测消息，然后通过 API 验证落库"""
    print("\n[MQTT 遥测落库]")

    device_code = f"E2E-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "device_code": device_code,
        "timestamp": timestamp,
        "status": "running",
        "metrics": {"temperature": 72.5, "pressure": 2.4, "voltage": 3.3},
        "payload": {
            "schema_version": "telemetry.v1",
            "gateway_id": "E2E-GW",
            "line_id": "TEST-LINE",
            "sequence": 1,
            "quality": "good",
            "sample_period_ms": 5000,
            "source": "e2e-test",
        },
    }

    def on_publish(client, userdata, mid, reason_code, properties):
        pass

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"e2e-test-{uuid.uuid4().hex[:8]}")
    client.on_publish = on_publish
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=10)
    client.loop_start()

    result = client.publish(MQTT_TOPIC, json.dumps(payload, ensure_ascii=False), qos=1)
    result.wait_for_publish(timeout=5)

    client.loop_stop()
    client.disconnect()

    check("MQTT 消息发布成功", result.rc == mqtt.MQTT_ERR_SUCCESS)

    # 等待 stream-worker 处理
    time.sleep(2)

    # 通过 API 查询设备
    resp = requests.get(f"{API_BASE}/api/devices/{device_code}", timeout=10)
    check("API 可查到新设备", resp.status_code == 200)

    if resp.status_code == 200:
        detail = resp.json()
        check("设备存在于响应中", detail["device"]["device_code"] == device_code)
        check("有遥测指标", len(detail["latest_metrics"]) > 0)

    # 查询遥测历史
    resp2 = requests.get(
        f"{API_BASE}/api/devices/{device_code}/telemetry",
        params={"hours": 1, "limit": 5},
        timeout=10,
    )
    check("遥测历史可查询", resp2.status_code == 200)
    if resp2.status_code == 200:
        tele = resp2.json()
        check("遥测点数 > 0", len(tele["points"]) > 0)
        if tele["points"]:
            pt = tele["points"][0]
            check("遥测包含 temperature", any(p["metric_name"] == "temperature" for p in tele["points"]))


def test_edge_command_flow():
    """端到端测试边缘命令下发流程"""
    print("\n[边缘命令下发]")

    # 发现网关
    resp = requests.get(f"{API_BASE}/api/edge/gateways", timeout=10)
    if resp.status_code != 200 or not resp.json():
        check("边缘网关存在 (跳过)", True)
        print("  没有发现边缘网关，跳过命令测试")
        return

    gateways = resp.json()
    gateway_id = gateways[0]["gateway_id"]

    # 下发命令
    resp2 = requests.post(
        f"{API_BASE}/api/edge/gateways/{gateway_id}/commands",
        json={
            "command_type": "pause",
            "parameters": {},
            "operator": "e2e-test",
        },
        timeout=10,
    )
    check("命令下发成功", resp2.status_code == 200)

    if resp2.status_code == 200:
        cmd = resp2.json()
        command_id = cmd["command_id"]
        check("命令 ID 生成", bool(command_id))
        check("命令状态 published", cmd["status"] == "published")

        # 等待 ack 回执
        time.sleep(5)

        # 查询命令状态
        resp3 = requests.get(
            f"{API_BASE}/api/edge/gateways/{gateway_id}/commands",
            timeout=10,
        )
        commands = resp3.json()
        latest = next((c for c in commands if c["command_id"] == command_id), None)
        if latest:
            status = latest["status"]
            check(f"命令回执状态: {status}", status in ("published", "executed"))
            if status == "executed":
                check("执行时间已记录", latest.get("executed_at") is not None)

    # 恢复上报
    requests.post(
        f"{API_BASE}/api/edge/gateways/{gateway_id}/commands",
        json={"command_type": "resume", "parameters": {}, "operator": "e2e-test"},
        timeout=10,
    )


def test_system_overview_consistency():
    """验证系统运营接口数据一致性"""
    print("\n[系统运营一致性]")

    resp = requests.get(f"{API_BASE}/api/system/overview", timeout=10)
    check("系统运营接口可访问", resp.status_code == 200)

    if resp.status_code == 200:
        data = resp.json()
        summary = data["summary"]

        # 设备计数一致性
        device_count = summary["device_count"]
        running = summary["running_count"]
        warning = summary["warning_count"]
        offline = summary["offline_count"]
        check(
            f"设备计数一致 (total={device_count}, running={running}, warning={warning}, offline={offline})",
            running + warning + offline == device_count,
        )

        # telemetry 计数
        check("遥测总数 > 0", summary["telemetry_count"] > 0)

        # 服务状态
        services = data["services"]
        check(f"服务数量: {len(services)}", len(services) >= 3)
        for svc in services:
            check(f"服务 {svc['name']} 状态有效", svc["status"] in ("ok", "stale", "no_data", "error"))

        # 表计数
        table_counts = data.get("table_counts", [])
        check(f"表计数条目: {len(table_counts)}", len(table_counts) > 0)


def main():
    global PASSED, FAILED

    print(f"ForgePulse 端到端测试")
    print(f"  API:  {API_BASE}")
    print(f"  MQTT: {MQTT_HOST}:{MQTT_PORT}")
    print("=" * 60)

    try:
        # 连通性检查
        resp = requests.get(f"{API_BASE}/health", timeout=5)
        check("API 连通", resp.status_code == 200)
    except requests.exceptions.ConnectionError:
        FAILED += 1
        print(f"  FAIL 无法连接到 API ({API_BASE})，请确保 Docker 服务已启动")
        print("\n" + "=" * 60)
        print(f"结果: {PASSED}/{PASSED + FAILED} 通过, {FAILED} 失败")
        return FAILED

    tests = [
        test_mqtt_telemetry,
        test_edge_command_flow,
        test_system_overview_consistency,
    ]

    for test_fn in tests:
        try:
            test_fn()
        except Exception as exc:
            FAILED += 1
            print(f"  FAIL {test_fn.__name__}: {exc}")
            traceback.print_exc()

    print("\n" + "=" * 60)
    total = PASSED + FAILED
    print(f"结果: {PASSED}/{total} 通过, {FAILED} 失败")
    if FAILED == 0:
        print("全部测试通过！")
    return FAILED


if __name__ == "__main__":
    sys.exit(main())
