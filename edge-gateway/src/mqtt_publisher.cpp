#include "forgepulse/mqtt_publisher.hpp"

#include <cstdlib>
#include <fstream>
#include <sstream>
#include <utility>

namespace forgepulse {

MqttPublisher::MqttPublisher(std::string host, std::string port, std::string topic)
    : host_(std::move(host)), port_(std::move(port)), topic_(std::move(topic)) {}

PublishResult MqttPublisher::publish(const std::string& payload) const {
    const std::string file_path = "/tmp/forgepulse-telemetry.json";
    {
        std::ofstream file(file_path);
        file << payload;
    }

    std::ostringstream command;
    command << "mosquitto_pub"
            << " -h " << host_
            << " -p " << port_
            << " -t " << topic_
            << " -f " << file_path;

    const int exit_code = std::system(command.str().c_str());
    return PublishResult{exit_code == 0, exit_code};
}

}  // namespace forgepulse
