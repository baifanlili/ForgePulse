#include <iostream>
#include <thread>

#include "forgepulse/config.hpp"
#include "forgepulse/mqtt_publisher.hpp"
#include "forgepulse/telemetry.hpp"

int main() {
    const forgepulse::GatewayConfig config = forgepulse::load_config_from_environment();
    const forgepulse::MqttPublisher publisher(config.mqtt_host, config.mqtt_port, config.mqtt_topic);
    const auto devices = forgepulse::default_device_profiles();

    std::cout << "ForgePulse edge gateway started." << std::endl;
    std::cout << "Publishing telemetry to mqtt://" << config.mqtt_host << ":" << config.mqtt_port << "/"
              << config.mqtt_topic << std::endl;
    std::cout << "Publish interval: " << config.publish_interval.count() << " seconds" << std::endl;

    int tick = 0;
    while (true) {
        for (const auto& device : devices) {
            const std::string payload = forgepulse::build_telemetry_payload(device, tick);
            const forgepulse::PublishResult result = publisher.publish(payload);
            std::cout << (result.ok ? "published " : "publish failed ") << device.code << " exit="
                      << result.exit_code << " " << payload << std::endl;
        }

        ++tick;
        std::this_thread::sleep_for(config.publish_interval);
    }

    return 0;
}
