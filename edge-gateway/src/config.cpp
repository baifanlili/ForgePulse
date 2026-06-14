#include "forgepulse/config.hpp"

#include <cstdlib>

namespace forgepulse {
namespace {

std::string env_or_default(const char* name, const std::string& fallback) {
    const char* value = std::getenv(name);
    if (value == nullptr || std::string(value).empty()) {
        return fallback;
    }
    return value;
}

int env_int_or_default(const char* name, int fallback) {
    const char* value = std::getenv(name);
    if (value == nullptr || std::string(value).empty()) {
        return fallback;
    }

    try {
        return std::stoi(value);
    } catch (...) {
        return fallback;
    }
}

}  // namespace

GatewayConfig load_config_from_environment() {
    const int interval_seconds = env_int_or_default("EDGE_PUBLISH_INTERVAL_SECONDS", 5);
    const std::string gateway_id = env_or_default("EDGE_GATEWAY_ID", "EDGE-GW-01");

    return GatewayConfig{
        gateway_id,
        env_or_default("EDGE_LINE_ID", "FAB-A-RT"),
        env_or_default("MQTT_HOST", "mqtt"),
        env_or_default("MQTT_PORT", "1883"),
        env_or_default("MQTT_TELEMETRY_TOPIC", "forgepulse/telemetry"),
        env_or_default("MQTT_COMMAND_TOPIC", "forgepulse/commands/" + gateway_id),
        std::chrono::seconds{interval_seconds > 0 ? interval_seconds : 5},
        env_int_or_default("EDGE_PUBLISH_RETRY_COUNT", 2),
        env_int_or_default("EDGE_SPOOL_FLUSH_LIMIT", 20),
        env_or_default("EDGE_SPOOL_DIR", "/tmp/forgepulse-edge-spool"),
    };
}

}  // namespace forgepulse
