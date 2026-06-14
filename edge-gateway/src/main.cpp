#include <iostream>
#include <cstdint>
#include <mutex>
#include <thread>

#include "forgepulse/command_listener.hpp"
#include "forgepulse/config.hpp"
#include "forgepulse/mqtt_publisher.hpp"
#include "forgepulse/telemetry.hpp"

int main() {
    const forgepulse::GatewayConfig config = forgepulse::load_config_from_environment();
    const forgepulse::MqttPublisher publisher(
        config.mqtt_host,
        config.mqtt_port,
        config.mqtt_topic,
        config.publish_retry_count,
        config.spool_dir
    );
    const auto devices = forgepulse::default_device_profiles();
    forgepulse::GatewayRuntime runtime;
    runtime.publish_interval_seconds.store(static_cast<int>(config.publish_interval.count()));
    forgepulse::start_command_listener(config, runtime);

    std::cout << "ForgePulse edge gateway started." << std::endl;
    std::cout << "Gateway: " << config.gateway_id << " line=" << config.line_id << std::endl;
    std::cout << "Publishing telemetry to mqtt://" << config.mqtt_host << ":" << config.mqtt_port << "/"
              << config.mqtt_topic << std::endl;
    std::cout << "Listening edge commands on " << config.command_topic << std::endl;
    std::cout << "Publish interval: " << config.publish_interval.count() << " seconds" << std::endl;
    std::cout << "Retry count: " << config.publish_retry_count << " spool=" << config.spool_dir << std::endl;

    int tick = 0;
    std::uint64_t sequence = 1;
    while (true) {
        const int flushed = publisher.flush_spool(config.spool_flush_limit);
        if (flushed > 0) {
            std::cout << "flushed spooled messages count=" << flushed << std::endl;
        }

        if (runtime.paused.load()) {
            std::cout << "telemetry paused by edge command" << std::endl;
            std::this_thread::sleep_for(std::chrono::seconds(runtime.publish_interval_seconds.load()));
            continue;
        }

        std::string last_command_id;
        std::string last_command_type;
        std::string control_mode;
        {
            std::lock_guard<std::mutex> lock(runtime.command_mutex);
            last_command_id = runtime.last_command_id;
            last_command_type = runtime.last_command_type;
            control_mode = runtime.control_mode;
        }

        const bool inject_fault = runtime.injected_fault_cycles.load() > 0;
        for (const auto& device : devices) {
            const int sample_period_ms = runtime.publish_interval_seconds.load() * 1000;
            const std::string payload = forgepulse::build_telemetry_payload(
                device,
                tick,
                sequence,
                config.gateway_id,
                config.line_id,
                sample_period_ms,
                inject_fault,
                control_mode,
                last_command_id,
                last_command_type
            );
            const forgepulse::PublishResult result = publisher.publish(payload);
            std::cout << (result.ok ? "published " : "publish failed ") << device.code << " exit="
                      << result.exit_code << " " << payload << std::endl;
            ++sequence;
        }
        if (inject_fault) {
            runtime.injected_fault_cycles.fetch_sub(1);
        }

        ++tick;
        std::this_thread::sleep_for(std::chrono::seconds(runtime.publish_interval_seconds.load()));
    }

    return 0;
}
