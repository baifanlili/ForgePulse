CREATE TABLE IF NOT EXISTS devices (
    id BIGSERIAL PRIMARY KEY,
    device_code VARCHAR(64) NOT NULL UNIQUE,
    device_name VARCHAR(128) NOT NULL,
    device_type VARCHAR(64) NOT NULL,
    area VARCHAR(128),
    line VARCHAR(128),
    status VARCHAR(32) NOT NULL DEFAULT 'offline',
    last_heartbeat_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS telemetry_points (
    time TIMESTAMPTZ NOT NULL,
    device_code VARCHAR(64) NOT NULL,
    metric_name VARCHAR(64) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    tags JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS alarms (
    id BIGSERIAL PRIMARY KEY,
    alarm_code VARCHAR(64) NOT NULL UNIQUE,
    device_code VARCHAR(64) NOT NULL,
    severity VARCHAR(16) NOT NULL,
    title VARCHAR(128) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'active',
    started_at TIMESTAMPTZ NOT NULL,
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by VARCHAR(128),
    cleared_at TIMESTAMPTZ,
    cleared_by VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS alarm_events (
    id BIGSERIAL PRIMARY KEY,
    alarm_code VARCHAR(64) NOT NULL,
    event_type VARCHAR(32) NOT NULL,
    operator VARCHAR(128) NOT NULL DEFAULT 'system',
    note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lots (
    id BIGSERIAL PRIMARY KEY,
    lot_code VARCHAR(64) NOT NULL UNIQUE,
    product_code VARCHAR(64) NOT NULL,
    route_name VARCHAR(64) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    wafer_count INTEGER NOT NULL,
    total_die INTEGER NOT NULL,
    pass_die INTEGER NOT NULL,
    fail_die INTEGER NOT NULL,
    yield_rate DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS wafer_yields (
    id BIGSERIAL PRIMARY KEY,
    lot_code VARCHAR(64) NOT NULL,
    wafer_id VARCHAR(64) NOT NULL,
    total_die INTEGER NOT NULL,
    pass_die INTEGER NOT NULL,
    fail_die INTEGER NOT NULL,
    yield_rate DOUBLE PRECISION NOT NULL,
    measured_at TIMESTAMPTZ NOT NULL,
    UNIQUE (lot_code, wafer_id)
);

CREATE TABLE IF NOT EXISTS bin_counts (
    id BIGSERIAL PRIMARY KEY,
    lot_code VARCHAR(64) NOT NULL,
    bin_name VARCHAR(32) NOT NULL,
    die_count INTEGER NOT NULL,
    UNIQUE (lot_code, bin_name)
);

CREATE TABLE IF NOT EXISTS spc_points (
    id BIGSERIAL PRIMARY KEY,
    metric_name VARCHAR(64) NOT NULL,
    sample_time TIMESTAMPTZ NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    center_line DOUBLE PRECISION NOT NULL,
    upper_control_limit DOUBLE PRECISION NOT NULL,
    lower_control_limit DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS edge_commands (
    id BIGSERIAL PRIMARY KEY,
    command_id VARCHAR(64) NOT NULL UNIQUE,
    gateway_id VARCHAR(64) NOT NULL,
    command_type VARCHAR(64) NOT NULL,
    parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(32) NOT NULL DEFAULT 'published',
    operator VARCHAR(128) NOT NULL DEFAULT 'demo-operator',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    executed_at TIMESTAMPTZ,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS worker_heartbeats (
    id BIGSERIAL PRIMARY KEY,
    worker_id VARCHAR(64) NOT NULL,
    last_heartbeat_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status VARCHAR(32) NOT NULL DEFAULT 'healthy',
    telemetry_processed BIGINT NOT NULL DEFAULT 0,
    alarms_triggered BIGINT NOT NULL DEFAULT 0,
    detail TEXT,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_telemetry_points_device_time
    ON telemetry_points (device_code, time DESC);

CREATE INDEX IF NOT EXISTS idx_alarms_status_started
    ON alarms (status, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_alarm_events_alarm_created
    ON alarm_events (alarm_code, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_wafer_yields_lot
    ON wafer_yields (lot_code, wafer_id);

CREATE INDEX IF NOT EXISTS idx_edge_commands_gateway_created
    ON edge_commands (gateway_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_worker_heartbeats_worker_time
    ON worker_heartbeats (worker_id, last_heartbeat_at DESC);

ALTER TABLE alarms
    ADD COLUMN IF NOT EXISTS acknowledged_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS acknowledged_by VARCHAR(128),
    ADD COLUMN IF NOT EXISTS cleared_by VARCHAR(128);

INSERT INTO devices (device_code, device_name, device_type, area, line, status, last_heartbeat_at)
VALUES
    ('ETCH-01', '刻蚀机 01', 'Etcher', 'FAB-A', 'Line-01', 'running', NOW() - INTERVAL '18 seconds'),
    ('CVD-02', '薄膜沉积 02', 'CVD', 'FAB-A', 'Line-01', 'running', NOW() - INTERVAL '26 seconds'),
    ('PHOTO-03', '光刻机 03', 'Lithography', 'FAB-A', 'Line-02', 'warning', NOW() - INTERVAL '2 minutes'),
    ('TEST-04', '晶圆测试 04', 'Wafer Tester', 'TEST-B', 'Line-07', 'running', NOW() - INTERVAL '41 seconds'),
    ('PACK-05', '封装检测 05', 'Inspection', 'PACK-C', 'Line-03', 'offline', NOW() - INTERVAL '35 minutes')
ON CONFLICT (device_code) DO UPDATE SET
    device_name = EXCLUDED.device_name,
    device_type = EXCLUDED.device_type,
    area = EXCLUDED.area,
    line = EXCLUDED.line,
    status = EXCLUDED.status,
    last_heartbeat_at = EXCLUDED.last_heartbeat_at,
    updated_at = NOW();

INSERT INTO telemetry_points (time, device_code, metric_name, metric_value, tags)
VALUES
    (NOW() - INTERVAL '6 minutes', 'ETCH-01', 'temperature', 71.2, '{"unit":"celsius"}'),
    (NOW() - INTERVAL '5 minutes', 'ETCH-01', 'temperature', 72.0, '{"unit":"celsius"}'),
    (NOW() - INTERVAL '4 minutes', 'ETCH-01', 'temperature', 72.8, '{"unit":"celsius"}'),
    (NOW() - INTERVAL '3 minutes', 'ETCH-01', 'temperature', 73.1, '{"unit":"celsius"}'),
    (NOW() - INTERVAL '2 minutes', 'ETCH-01', 'temperature', 74.4, '{"unit":"celsius"}'),
    (NOW() - INTERVAL '1 minutes', 'ETCH-01', 'temperature', 73.7, '{"unit":"celsius"}'),
    (NOW() - INTERVAL '6 minutes', 'CVD-02', 'pressure', 2.4, '{"unit":"kpa"}'),
    (NOW() - INTERVAL '5 minutes', 'CVD-02', 'pressure', 2.5, '{"unit":"kpa"}'),
    (NOW() - INTERVAL '4 minutes', 'CVD-02', 'pressure', 2.7, '{"unit":"kpa"}'),
    (NOW() - INTERVAL '3 minutes', 'CVD-02', 'pressure', 2.8, '{"unit":"kpa"}'),
    (NOW() - INTERVAL '2 minutes', 'CVD-02', 'pressure', 2.6, '{"unit":"kpa"}'),
    (NOW() - INTERVAL '1 minutes', 'CVD-02', 'pressure', 2.5, '{"unit":"kpa"}');

INSERT INTO alarms (
    alarm_code,
    device_code,
    severity,
    title,
    description,
    status,
    started_at,
    acknowledged_at,
    acknowledged_by,
    cleared_at,
    cleared_by
)
VALUES
    ('ALM-20260613-001', 'PHOTO-03', 'warning', '心跳延迟', '设备心跳超过 120 秒未刷新，建议检查链路状态。', 'active', NOW() - INTERVAL '7 minutes', NULL, NULL, NULL, NULL),
    ('ALM-20260613-002', 'ETCH-01', 'critical', '腔体温度偏高', '刻蚀腔体温度连续 3 个采样点高于控制上限。', 'active', NOW() - INTERVAL '11 minutes', NULL, NULL, NULL, NULL),
    ('ALM-20260613-003', 'PACK-05', 'warning', '设备离线', '封装检测设备离线超过 30 分钟。', 'acknowledged', NOW() - INTERVAL '35 minutes', NOW() - INTERVAL '28 minutes', 'shift-lead', NULL, NULL),
    ('ALM-20260613-004', 'TEST-04', 'info', '良率恢复', '最近一个 Lot 良率回到目标线以上。', 'cleared', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '110 minutes', 'qa-engineer', NOW() - INTERVAL '84 minutes', 'qa-engineer')
ON CONFLICT (alarm_code) DO UPDATE SET
    device_code = EXCLUDED.device_code,
    severity = EXCLUDED.severity,
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    status = EXCLUDED.status,
    started_at = EXCLUDED.started_at,
    acknowledged_at = EXCLUDED.acknowledged_at,
    acknowledged_by = EXCLUDED.acknowledged_by,
    cleared_at = EXCLUDED.cleared_at,
    cleared_by = EXCLUDED.cleared_by;

INSERT INTO alarm_events (alarm_code, event_type, operator, note, created_at)
VALUES
    ('ALM-20260613-001', 'created', 'system', '心跳监控规则触发。', NOW() - INTERVAL '7 minutes'),
    ('ALM-20260613-002', 'created', 'system', '温度阈值规则触发。', NOW() - INTERVAL '11 minutes'),
    ('ALM-20260613-003', 'created', 'system', '设备离线规则触发。', NOW() - INTERVAL '35 minutes'),
    ('ALM-20260613-003', 'acknowledged', 'shift-lead', '现场已派人检查封装检测设备。', NOW() - INTERVAL '28 minutes'),
    ('ALM-20260613-004', 'created', 'system', '良率恢复事件生成。', NOW() - INTERVAL '2 hours'),
    ('ALM-20260613-004', 'acknowledged', 'qa-engineer', '确认恢复趋势有效。', NOW() - INTERVAL '110 minutes'),
    ('ALM-20260613-004', 'cleared', 'qa-engineer', 'Lot 复测通过，关闭告警。', NOW() - INTERVAL '84 minutes')
ON CONFLICT DO NOTHING;

INSERT INTO lots (lot_code, product_code, route_name, started_at, completed_at, wafer_count, total_die, pass_die, fail_die, yield_rate)
VALUES
    ('LOT-A240613-01', 'FP-7N-ASIC', '7nm-test-route', NOW() - INTERVAL '8 hours', NOW() - INTERVAL '6 hours', 6, 9120, 8617, 503, 94.48),
    ('LOT-A240613-02', 'FP-7N-ASIC', '7nm-test-route', NOW() - INTERVAL '6 hours', NOW() - INTERVAL '4 hours', 6, 9120, 8492, 628, 93.11),
    ('LOT-B240613-03', 'FP-PMIC-28', '28nm-pmic-route', NOW() - INTERVAL '4 hours', NOW() - INTERVAL '2 hours', 6, 7680, 7319, 361, 95.30),
    ('LOT-B240613-04', 'FP-PMIC-28', '28nm-pmic-route', NOW() - INTERVAL '2 hours', NULL, 6, 7680, 7242, 438, 94.30)
ON CONFLICT (lot_code) DO UPDATE SET
    product_code = EXCLUDED.product_code,
    route_name = EXCLUDED.route_name,
    started_at = EXCLUDED.started_at,
    completed_at = EXCLUDED.completed_at,
    wafer_count = EXCLUDED.wafer_count,
    total_die = EXCLUDED.total_die,
    pass_die = EXCLUDED.pass_die,
    fail_die = EXCLUDED.fail_die,
    yield_rate = EXCLUDED.yield_rate;

INSERT INTO wafer_yields (lot_code, wafer_id, total_die, pass_die, fail_die, yield_rate, measured_at)
VALUES
    ('LOT-A240613-01', 'W01', 1520, 1441, 79, 94.80, NOW() - INTERVAL '7 hours'),
    ('LOT-A240613-01', 'W02', 1520, 1435, 85, 94.41, NOW() - INTERVAL '7 hours'),
    ('LOT-A240613-01', 'W03', 1520, 1427, 93, 93.88, NOW() - INTERVAL '7 hours'),
    ('LOT-A240613-01', 'W04', 1520, 1458, 62, 95.92, NOW() - INTERVAL '7 hours'),
    ('LOT-A240613-01', 'W05', 1520, 1422, 98, 93.55, NOW() - INTERVAL '7 hours'),
    ('LOT-A240613-01', 'W06', 1520, 1434, 86, 94.34, NOW() - INTERVAL '7 hours'),
    ('LOT-B240613-04', 'W01', 1280, 1219, 61, 95.23, NOW() - INTERVAL '48 minutes'),
    ('LOT-B240613-04', 'W02', 1280, 1206, 74, 94.22, NOW() - INTERVAL '42 minutes'),
    ('LOT-B240613-04', 'W03', 1280, 1188, 92, 92.81, NOW() - INTERVAL '36 minutes'),
    ('LOT-B240613-04', 'W04', 1280, 1221, 59, 95.39, NOW() - INTERVAL '30 minutes'),
    ('LOT-B240613-04', 'W05', 1280, 1199, 81, 93.67, NOW() - INTERVAL '24 minutes'),
    ('LOT-B240613-04', 'W06', 1280, 1209, 71, 94.45, NOW() - INTERVAL '18 minutes')
ON CONFLICT (lot_code, wafer_id) DO UPDATE SET
    total_die = EXCLUDED.total_die,
    pass_die = EXCLUDED.pass_die,
    fail_die = EXCLUDED.fail_die,
    yield_rate = EXCLUDED.yield_rate,
    measured_at = EXCLUDED.measured_at;

INSERT INTO bin_counts (lot_code, bin_name, die_count)
VALUES
    ('LOT-B240613-04', 'Bin 1 Pass', 7242),
    ('LOT-B240613-04', 'Bin 2 Leakage', 126),
    ('LOT-B240613-04', 'Bin 3 Timing', 184),
    ('LOT-B240613-04', 'Bin 4 Open/Short', 79),
    ('LOT-B240613-04', 'Bin 5 Other', 49)
ON CONFLICT (lot_code, bin_name) DO UPDATE SET
    die_count = EXCLUDED.die_count;

INSERT INTO spc_points (metric_name, sample_time, value, center_line, upper_control_limit, lower_control_limit)
VALUES
    ('critical_dimension', NOW() - INTERVAL '8 hours', 27.8, 28.0, 29.2, 26.8),
    ('critical_dimension', NOW() - INTERVAL '7 hours', 28.1, 28.0, 29.2, 26.8),
    ('critical_dimension', NOW() - INTERVAL '6 hours', 28.4, 28.0, 29.2, 26.8),
    ('critical_dimension', NOW() - INTERVAL '5 hours', 28.0, 28.0, 29.2, 26.8),
    ('critical_dimension', NOW() - INTERVAL '4 hours', 28.6, 28.0, 29.2, 26.8),
    ('critical_dimension', NOW() - INTERVAL '3 hours', 28.9, 28.0, 29.2, 26.8),
    ('critical_dimension', NOW() - INTERVAL '2 hours', 29.4, 28.0, 29.2, 26.8),
    ('critical_dimension', NOW() - INTERVAL '1 hours', 28.7, 28.0, 29.2, 26.8);

ALTER TABLE edge_commands
    ADD COLUMN IF NOT EXISTS executed_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS error_message TEXT;
