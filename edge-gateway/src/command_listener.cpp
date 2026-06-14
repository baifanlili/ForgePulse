#include "forgepulse/command_listener.hpp"

#include <cstdio>
#include <iostream>
#include <regex>
#include <sstream>
#include <thread>

namespace forgepulse {
namespace {

std::string shell_quote(const std::string& value) {
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

std::string capture_string(const std::string& payload, const std::string& field) {
    const std::regex pattern("\"" + field + "\"\\s*:\\s*\"([^\"]+)\"");
    std::smatch match;
    if (std::regex_search(payload, match, pattern)) {
        return match[1].str();
    }
    return "";
}

int capture_int(const std::string& payload, const std::string& field, int fallback) {
    const std::regex pattern("\"" + field + "\"\\s*:\\s*([0-9]+)");
    std::smatch match;
    if (std::regex_search(payload, match, pattern)) {
        return std::stoi(match[1].str());
    }
    return fallback;
}

void remember_command(GatewayRuntime& runtime, const std::string& command_id, const std::string& command_type) {
    std::lock_guard<std::mutex> lock(runtime.command_mutex);
    runtime.last_command_id = command_id;
    runtime.last_command_type = command_type;
}

void apply_command(GatewayRuntime& runtime, const std::string& payload) {
    const std::string command_id = capture_string(payload, "command_id");
    const std::string command_type = capture_string(payload, "command_type");
    if (command_type.empty()) {
        std::cout << "ignored malformed edge command " << payload << std::endl;
        return;
    }

    if (command_type == "pause") {
        runtime.paused.store(true);
        {
            std::lock_guard<std::mutex> lock(runtime.command_mutex);
            runtime.control_mode = "paused";
        }
    } else if (command_type == "resume") {
        runtime.paused.store(false);
        {
            std::lock_guard<std::mutex> lock(runtime.command_mutex);
            runtime.control_mode = "running";
        }
    } else if (command_type == "set_interval") {
        const int interval_seconds = capture_int(payload, "interval_seconds", runtime.publish_interval_seconds.load());
        if (interval_seconds >= 1 && interval_seconds <= 60) {
            runtime.publish_interval_seconds.store(interval_seconds);
        }
    } else if (command_type == "inject_fault") {
        const int cycles = capture_int(payload, "fault_cycles", 6);
        runtime.injected_fault_cycles.store(cycles > 0 ? cycles : 6);
    }

    remember_command(runtime, command_id, command_type);
    std::cout << "applied edge command " << command_type << " id=" << command_id << std::endl;
}

void listen_forever(const GatewayConfig& config, GatewayRuntime& runtime) {
    while (true) {
        std::ostringstream command;
        command << "mosquitto_sub"
                << " -h " << shell_quote(config.mqtt_host)
                << " -p " << shell_quote(config.mqtt_port)
                << " -t " << shell_quote(config.command_topic)
                << " -q 1";

        FILE* pipe = popen(command.str().c_str(), "r");
        if (pipe == nullptr) {
            std::cout << "edge command listener failed to start" << std::endl;
            std::this_thread::sleep_for(std::chrono::seconds(3));
            continue;
        }

        char buffer[4096];
        while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
            apply_command(runtime, std::string(buffer));
        }

        const int exit_code = pclose(pipe);
        std::cout << "edge command listener exited code=" << exit_code << ", retrying" << std::endl;
        std::this_thread::sleep_for(std::chrono::seconds(3));
    }
}

}  // namespace

void start_command_listener(const GatewayConfig& config, GatewayRuntime& runtime) {
    std::thread([config, &runtime]() { listen_forever(config, runtime); }).detach();
}

}  // namespace forgepulse
