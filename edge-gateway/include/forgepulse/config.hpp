#pragma once

#include <chrono>
#include <string>

namespace forgepulse {

struct GatewayConfig {
    std::string gateway_id;
    std::string line_id;
    std::string mqtt_host;
    std::string mqtt_port;
    std::string mqtt_topic;
    std::string command_topic;
    std::string ack_topic;
    std::chrono::seconds publish_interval;
    int publish_retry_count;
    int spool_flush_limit;
    std::string spool_dir;
};

GatewayConfig load_config_from_environment();

}  // namespace forgepulse
