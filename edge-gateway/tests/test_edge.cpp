#include <cstdint>
#include <iostream>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>

#include "forgepulse/telemetry.hpp"
#include "forgepulse/command_listener.hpp"

// ---------------------------------------------------------------------------
// Minimal test framework
// ---------------------------------------------------------------------------
static int tests_passed = 0;
static int tests_failed = 0;

#define TEST_CASE(name)                                                        \
    static void test_##name();                                                 \
    struct registrar_##name {                                                  \
        registrar_##name() {                                                   \
            std::cout << "  " << #name << "... ";                              \
            try {                                                              \
                test_##name();                                                 \
                std::cout << "PASS\n";                                         \
                ++tests_passed;                                                \
            } catch (const std::exception& e) {                                \
                std::cout << "FAIL: " << e.what() << "\n";                     \
                ++tests_failed;                                                \
            } catch (...) {                                                    \
                std::cout << "FAIL (unknown)\n";                               \
                ++tests_failed;                                                \
            }                                                                  \
        }                                                                      \
    } reg_##name;                                                              \
    static void test_##name()

#define CHECK(expr)                                                            \
    do {                                                                       \
        if (!(expr))                                                           \
            throw std::runtime_error("CHECK failed: " #expr);                  \
    } while (0)

#define CHECK_CONTAINS(str, sub)                                               \
    CHECK((str).find(sub) != std::string::npos)

// ---------------------------------------------------------------------------
// Replicated helpers from anonymous namespaces
// ---------------------------------------------------------------------------

static std::string shell_quote(const std::string& value) {
    std::string quoted = "'";
    for (const char ch : value) {
        if (ch == '\'') {
            quoted += "'\\''";
        } else {
            quoted += ch;
        }
    }
    quoted += "'";
    return quoted;
}

static std::string cp_string(const std::string& payload, const std::string& field) {
    const std::regex pattern("\"" + field + "\"\\s*:\\s*\"([^\"]+)\"");
    std::smatch match;
    if (std::regex_search(payload, match, pattern)) {
        return match[1].str();
    }
    return "";
}

static int cp_int(const std::string& payload, const std::string& field, int fallback) {
    const std::regex pattern("\"" + field + "\"\\s*:\\s*([0-9]+)");
    std::smatch match;
    if (std::regex_search(payload, match, pattern)) {
        return std::stoi(match[1].str());
    }
    return fallback;
}

struct CmdResult {
    bool ok;
    std::string error;
};

static CmdResult apply_cmd(const std::string& payload, forgepulse::GatewayRuntime& rt) {
    const std::string cmd_id = cp_string(payload, "command_id");
    const std::string cmd_type = cp_string(payload, "command_type");
    if (cmd_type.empty()) {
        return {false, "empty command_type"};
    }

    CmdResult result{true, ""};

    if (cmd_type == "pause") {
        rt.paused.store(true);
        {
            std::lock_guard<std::mutex> lock(rt.command_mutex);
            rt.control_mode = "paused";
        }
    } else if (cmd_type == "resume") {
        rt.paused.store(false);
        {
            std::lock_guard<std::mutex> lock(rt.command_mutex);
            rt.control_mode = "running";
        }
    } else if (cmd_type == "set_interval") {
        const int interval = cp_int(payload, "interval_seconds",
                                    rt.publish_interval_seconds.load());
        if (interval >= 1 && interval <= 60) {
            rt.publish_interval_seconds.store(interval);
        } else {
            result.ok = false;
            result.error = "interval_seconds out of range [1,60]";
        }
    } else if (cmd_type == "inject_fault") {
        const int cycles = cp_int(payload, "fault_cycles", 6);
        rt.injected_fault_cycles.store(cycles > 0 ? cycles : 6);
    } else {
        result.ok = false;
        result.error = "unknown command_type";
    }

    rt.last_command_id = cmd_id;
    rt.last_command_type = cmd_type;
    rt.last_ack_status = result.ok ? "executed" : "failed";
    return result;
}

// ===========================================================================
// Tests: shell_quote
// ===========================================================================

TEST_CASE(shell_quote_empty) {
    CHECK(shell_quote("") == "''");
}

TEST_CASE(shell_quote_simple) {
    CHECK(shell_quote("hello") == "'hello'");
}

TEST_CASE(shell_quote_with_spaces) {
    CHECK(shell_quote("hello world") == "'hello world'");
}

TEST_CASE(shell_quote_with_single_quote) {
    CHECK(shell_quote("it's") == "'it'\\''s'");
}

TEST_CASE(shell_quote_preserves_special_chars) {
    CHECK(shell_quote("a!b@c#d$") == "'a!b@c#d$'");
}

// ===========================================================================
// Tests: default_device_profiles
// ===========================================================================

TEST_CASE(default_device_profiles_count) {
    auto profiles = forgepulse::default_device_profiles();
    CHECK(profiles.size() == 4);
}

TEST_CASE(default_device_profiles_codes) {
    auto profiles = forgepulse::default_device_profiles();
    CHECK(profiles[0].code == "ETCH-01");
    CHECK(profiles[1].code == "CVD-02");
    CHECK(profiles[2].code == "PHOTO-03");
    CHECK(profiles[3].code == "TEST-04");
}

TEST_CASE(default_device_profiles_have_statuses) {
    auto profiles = forgepulse::default_device_profiles();
    CHECK(profiles[0].status == "running");
    CHECK(profiles[2].status == "warning");
}

// ===========================================================================
// Tests: DeviceProfile struct
// ===========================================================================

TEST_CASE(device_profile_fields_assignable) {
    forgepulse::DeviceProfile dev;
    dev.code = "UNIT-01";
    dev.status = "idle";
    dev.temperature_base = 25.5;
    dev.pressure_base = 1.0;
    dev.voltage_base = 5.0;
    dev.yield_base = 99.9;
    CHECK(dev.code == "UNIT-01");
    CHECK(dev.status == "idle");
    CHECK(dev.temperature_base == 25.5);
    CHECK(dev.pressure_base == 1.0);
    CHECK(dev.voltage_base == 5.0);
    CHECK(dev.yield_base == 99.9);
}

// ===========================================================================
// Tests: build_telemetry_payload — field presence
// ===========================================================================

TEST_CASE(payload_contains_top_level_fields) {
    forgepulse::DeviceProfile dev{"ETCH-01", "running", 50.0, 2.0, 3.3, 95.0};
    std::string json = forgepulse::build_telemetry_payload(
        dev, 0, 1, "GW-01", "LINE-A", 500, false, "running", "", "");
    CHECK(json.find("device_code") != std::string::npos);
    CHECK(json.find("ETCH-01") != std::string::npos);
    CHECK(json.find("timestamp") != std::string::npos);
    CHECK(json.find("running") != std::string::npos);
}

TEST_CASE(payload_contains_metrics_section) {
    forgepulse::DeviceProfile dev{"ETCH-01", "running", 50.0, 2.0, 3.3, 95.0};
    std::string json = forgepulse::build_telemetry_payload(
        dev, 0, 1, "GW-01", "LINE-A", 500, false, "running", "", "");
    CHECK_CONTAINS(json, "\"metrics\":{");
    CHECK_CONTAINS(json, "\"temperature\":");
    CHECK_CONTAINS(json, "\"pressure\":");
    CHECK_CONTAINS(json, "\"voltage\":");
    CHECK_CONTAINS(json, "\"yield_rate\":");
}

TEST_CASE(payload_contains_payload_section) {
    forgepulse::DeviceProfile dev{"ETCH-01", "running", 50.0, 2.0, 3.3, 95.0};
    std::string json = forgepulse::build_telemetry_payload(
        dev, 0, 1, "GW-01", "LINE-A", 500, false, "running", "", "");
    CHECK_CONTAINS(json, "\"schema_version\":\"telemetry.v1\"");
    CHECK_CONTAINS(json, "\"gateway_id\":\"GW-01\"");
    CHECK_CONTAINS(json, "\"line_id\":\"LINE-A\"");
    CHECK_CONTAINS(json, "\"sequence\":1");
    CHECK_CONTAINS(json, "\"quality\":\"");
    CHECK_CONTAINS(json, "\"status_reason\":\"");
    CHECK_CONTAINS(json, "\"sample_period_ms\":500");
    CHECK_CONTAINS(json, "\"control_mode\":\"running\"");
    CHECK_CONTAINS(json, "\"lot_code\":\"LOT-RT-240613\"");
    CHECK_CONTAINS(json, "\"source\":\"edge-gateway\"");
}

TEST_CASE(payload_contains_wafer_id) {
    forgepulse::DeviceProfile dev{"ETCH-01", "running", 50.0, 2.0, 3.3, 95.0};
    std::string json = forgepulse::build_telemetry_payload(
        dev, 0, 1, "GW-01", "LINE-A", 500, false, "running", "", "");
    CHECK_CONTAINS(json, "\"wafer_id\":\"W");
}

TEST_CASE(payload_includes_last_command_when_present) {
    forgepulse::DeviceProfile dev{"ETCH-01", "running", 50.0, 2.0, 3.3, 95.0};
    std::string json = forgepulse::build_telemetry_payload(
        dev, 0, 1, "GW-01", "LINE-A", 500, false, "running", "cmd-123", "pause");
    CHECK_CONTAINS(json, "\"last_command_id\":\"cmd-123\"");
    CHECK_CONTAINS(json, "\"last_command_type\":\"pause\"");
}

TEST_CASE(payload_omits_last_command_when_empty) {
    forgepulse::DeviceProfile dev{"ETCH-01", "running", 50.0, 2.0, 3.3, 95.0};
    std::string json = forgepulse::build_telemetry_payload(
        dev, 0, 1, "GW-01", "LINE-A", 500, false, "running", "", "");
    CHECK(json.find("last_command_id") == std::string::npos);
}

TEST_CASE(payload_reflects_gateway_and_line) {
    forgepulse::DeviceProfile dev{"ETCH-01", "running", 50.0, 2.0, 3.3, 95.0};
    std::string json = forgepulse::build_telemetry_payload(
        dev, 0, 42, "EDGE-GW-02", "FAB-B", 1000, false, "running", "", "");
    CHECK_CONTAINS(json, "\"gateway_id\":\"EDGE-GW-02\"");
    CHECK_CONTAINS(json, "\"line_id\":\"FAB-B\"");
    CHECK_CONTAINS(json, "\"sequence\":42");
    CHECK_CONTAINS(json, "\"sample_period_ms\":1000");
}

// ===========================================================================
// Tests: quality marking via build_telemetry_payload
// ===========================================================================

TEST_CASE(quality_good_with_normal_values) {
    forgepulse::DeviceProfile dev{"NORMAL-01", "running", 50.0, 2.0, 3.3, 95.0};
    std::string json = forgepulse::build_telemetry_payload(
        dev, 0, 1, "GW-01", "LINE-A", 500, false, "running", "", "");
    CHECK_CONTAINS(json, "\"quality\":\"good\"");
    CHECK_CONTAINS(json, "\"status_reason\":\"normal\"");
}

TEST_CASE(quality_degraded_with_high_temperature) {
    forgepulse::DeviceProfile dev{"HOT-01", "running", 100.0, 2.0, 3.3, 95.0};
    std::string json = forgepulse::build_telemetry_payload(
        dev, 0, 1, "GW-01", "LINE-A", 500, false, "running", "", "");
    CHECK_CONTAINS(json, "\"quality\":\"degraded\"");
    CHECK_CONTAINS(json, "\"status_reason\":\"threshold_watch\"");
}

TEST_CASE(quality_degraded_with_high_pressure) {
    forgepulse::DeviceProfile dev{"PRESS-01", "running", 50.0, 3.0, 3.3, 95.0};
    std::string json = forgepulse::build_telemetry_payload(
        dev, 0, 1, "GW-01", "LINE-A", 500, false, "running", "", "");
    CHECK_CONTAINS(json, "\"quality\":\"degraded\"");
    CHECK_CONTAINS(json, "\"status_reason\":\"threshold_watch\"");
}

TEST_CASE(quality_degraded_with_low_voltage) {
    forgepulse::DeviceProfile dev{"LOWV-01", "running", 50.0, 2.0, 3.0, 95.0};
    std::string json = forgepulse::build_telemetry_payload(
        dev, 0, 1, "GW-01", "LINE-A", 500, false, "running", "", "");
    CHECK_CONTAINS(json, "\"quality\":\"degraded\"");
    CHECK_CONTAINS(json, "\"status_reason\":\"threshold_watch\"");
}

TEST_CASE(quality_degraded_with_fault_injection_on_etch) {
    forgepulse::DeviceProfile dev = forgepulse::default_device_profiles()[0];
    std::string json = forgepulse::build_telemetry_payload(
        dev, 0, 1, "GW-01", "LINE-A", 500, true, "running", "", "");
    CHECK_CONTAINS(json, "\"quality\":\"degraded\"");
}

TEST_CASE(quality_good_with_fault_injection_on_non_etch) {
    forgepulse::DeviceProfile dev{"TEST-04", "running", 61.5, 1.95, 3.22, 95.4};
    std::string json = forgepulse::build_telemetry_payload(
        dev, 0, 1, "GW-01", "LINE-A", 500, true, "running", "", "");
    CHECK_CONTAINS(json, "\"quality\":\"good\"");
}

// ===========================================================================
// Tests: command parsing (cp_string / cp_int)
// ===========================================================================

TEST_CASE(cp_string_extracts_value) {
    std::string payload = R"({"command_id":"abc-123","command_type":"pause"})";
    CHECK(cp_string(payload, "command_id") == "abc-123");
    CHECK(cp_string(payload, "command_type") == "pause");
}

TEST_CASE(cp_string_missing_field_returns_empty) {
    std::string payload = R"({"command_id":"abc-123"})";
    CHECK(cp_string(payload, "command_type") == "");
}

TEST_CASE(cp_string_handles_whitespace) {
    std::string payload = R"({"command_id" : "abc-123"})";
    CHECK(cp_string(payload, "command_id") == "abc-123");
}

TEST_CASE(cp_int_extracts_value) {
    std::string payload = R"({"interval_seconds":10})";
    CHECK(cp_int(payload, "interval_seconds", 5) == 10);
}

TEST_CASE(cp_int_missing_field_returns_fallback) {
    std::string payload = R"({"other":99})";
    CHECK(cp_int(payload, "interval_seconds", 5) == 5);
}

TEST_CASE(cp_int_handles_whitespace) {
    std::string payload = R"({"interval_seconds" : 42})";
    CHECK(cp_int(payload, "interval_seconds", 5) == 42);
}

// ===========================================================================
// Tests: command application (apply_cmd)
// ===========================================================================

TEST_CASE(cmd_pause_sets_paused) {
    forgepulse::GatewayRuntime rt;
    rt.paused.store(false);
    rt.control_mode = "running";
    auto result = apply_cmd(
        R"({"command_id":"c1","command_type":"pause"})", rt);
    CHECK(result.ok);
    CHECK(rt.paused.load() == true);
    CHECK(rt.control_mode == "paused");
}

TEST_CASE(cmd_resume_clears_paused) {
    forgepulse::GatewayRuntime rt;
    rt.paused.store(true);
    rt.control_mode = "paused";
    auto result = apply_cmd(
        R"({"command_id":"c2","command_type":"resume"})", rt);
    CHECK(result.ok);
    CHECK(rt.paused.load() == false);
    CHECK(rt.control_mode == "running");
}

TEST_CASE(cmd_set_interval_valid) {
    forgepulse::GatewayRuntime rt;
    rt.publish_interval_seconds.store(5);
    auto result = apply_cmd(
        R"({"command_id":"c3","command_type":"set_interval","interval_seconds":15})", rt);
    CHECK(result.ok);
    CHECK(rt.publish_interval_seconds.load() == 15);
}

TEST_CASE(cmd_set_interval_boundary_lower) {
    forgepulse::GatewayRuntime rt;
    rt.publish_interval_seconds.store(5);
    auto result = apply_cmd(
        R"({"command_id":"c4","command_type":"set_interval","interval_seconds":1})", rt);
    CHECK(result.ok);
    CHECK(rt.publish_interval_seconds.load() == 1);
}

TEST_CASE(cmd_set_interval_boundary_upper) {
    forgepulse::GatewayRuntime rt;
    rt.publish_interval_seconds.store(5);
    auto result = apply_cmd(
        R"({"command_id":"c5","command_type":"set_interval","interval_seconds":60})", rt);
    CHECK(result.ok);
    CHECK(rt.publish_interval_seconds.load() == 60);
}

TEST_CASE(cmd_set_interval_below_range) {
    forgepulse::GatewayRuntime rt;
    rt.publish_interval_seconds.store(5);
    auto result = apply_cmd(
        R"({"command_id":"c6","command_type":"set_interval","interval_seconds":0})", rt);
    CHECK(!result.ok);
    CHECK(result.error == "interval_seconds out of range [1,60]");
    CHECK(rt.publish_interval_seconds.load() == 5);
}

TEST_CASE(cmd_set_interval_above_range) {
    forgepulse::GatewayRuntime rt;
    rt.publish_interval_seconds.store(5);
    auto result = apply_cmd(
        R"({"command_id":"c7","command_type":"set_interval","interval_seconds":61})", rt);
    CHECK(!result.ok);
    CHECK(result.error == "interval_seconds out of range [1,60]");
    CHECK(rt.publish_interval_seconds.load() == 5);
}

TEST_CASE(cmd_inject_fault_with_cycles) {
    forgepulse::GatewayRuntime rt;
    rt.injected_fault_cycles.store(0);
    auto result = apply_cmd(
        R"({"command_id":"c8","command_type":"inject_fault","fault_cycles":10})", rt);
    CHECK(result.ok);
    CHECK(rt.injected_fault_cycles.load() == 10);
}

TEST_CASE(cmd_inject_fault_defaults_to_six) {
    forgepulse::GatewayRuntime rt;
    rt.injected_fault_cycles.store(0);
    auto result = apply_cmd(
        R"({"command_id":"c9","command_type":"inject_fault"})", rt);
    CHECK(result.ok);
    CHECK(rt.injected_fault_cycles.load() == 6);
}

TEST_CASE(cmd_inject_fault_zero_uses_default) {
    forgepulse::GatewayRuntime rt;
    rt.injected_fault_cycles.store(0);
    auto result = apply_cmd(
        R"({"command_id":"c10","command_type":"inject_fault","fault_cycles":0})", rt);
    CHECK(result.ok);
    CHECK(rt.injected_fault_cycles.load() == 6);
}

TEST_CASE(cmd_unknown_type_returns_error) {
    forgepulse::GatewayRuntime rt;
    auto result = apply_cmd(
        R"({"command_id":"c11","command_type":"reboot"})", rt);
    CHECK(!result.ok);
    CHECK(result.error == "unknown command_type");
}

TEST_CASE(cmd_records_last_command_on_success) {
    forgepulse::GatewayRuntime rt;
    apply_cmd(R"({"command_id":"c12","command_type":"pause"})", rt);
    CHECK(rt.last_command_id == "c12");
    CHECK(rt.last_command_type == "pause");
    CHECK(rt.last_ack_status == "executed");
}

TEST_CASE(cmd_records_ack_failed_on_error) {
    forgepulse::GatewayRuntime rt;
    apply_cmd(R"({"command_id":"c13","command_type":"set_interval","interval_seconds":0})", rt);
    CHECK(rt.last_ack_status == "failed");
}

TEST_CASE(cmd_empty_command_type_returns_error) {
    forgepulse::GatewayRuntime rt;
    auto result = apply_cmd(R"({"command_id":"c14"})", rt);
    CHECK(!result.ok);
    CHECK(result.error == "empty command_type");
}

// ===========================================================================
// main
// ===========================================================================

int main() {
    std::cout << "Running edge-gateway unit tests...\n" << std::endl;

    std::cout << "\nResults: " << tests_passed << " passed, "
              << tests_failed << " failed" << std::endl;

    return tests_failed > 0 ? 1 : 0;
}
