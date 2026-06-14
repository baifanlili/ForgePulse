#pragma once

#include <chrono>
#include <string>

namespace forgepulse {

struct GatewayConfig {
    std::string mqtt_host;
    std::string mqtt_port;
    std::string mqtt_topic;
    std::chrono::seconds publish_interval;
};

GatewayConfig load_config_from_environment();

}  // namespace forgepulse
