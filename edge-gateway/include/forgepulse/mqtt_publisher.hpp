#pragma once

#include <string>

namespace forgepulse {

struct PublishResult {
    bool ok;
    int exit_code;
};

class MqttPublisher {
public:
    MqttPublisher(std::string host, std::string port, std::string topic);

    PublishResult publish(const std::string& payload) const;

private:
    std::string host_;
    std::string port_;
    std::string topic_;
};

}  // namespace forgepulse
