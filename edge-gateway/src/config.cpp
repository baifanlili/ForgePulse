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

    return GatewayConfig{
        env_or_default("MQTT_HOST", "mqtt"),
        env_or_default("MQTT_PORT", "1883"),
        env_or_default("MQTT_TELEMETRY_TOPIC", "forgepulse/telemetry"),
        std::chrono::seconds{interval_seconds > 0 ? interval_seconds : 5},
    };
}

}  // namespace forgepulse
