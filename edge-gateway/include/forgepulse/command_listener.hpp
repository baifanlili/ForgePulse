#pragma once

#include <atomic>
#include <mutex>
#include <string>

#include "forgepulse/config.hpp"

namespace forgepulse {

struct GatewayRuntime {
    std::atomic<bool> paused{false};
    std::atomic<int> publish_interval_seconds{5};
    std::atomic<int> injected_fault_cycles{0};
    std::mutex command_mutex;
    std::string last_command_id;
    std::string last_command_type;
    std::string last_ack_status;
    std::string control_mode{"running"};
};

void start_command_listener(const GatewayConfig& config, GatewayRuntime& runtime);

}  // namespace forgepulse
