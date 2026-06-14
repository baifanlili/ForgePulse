#pragma once

#include <string>

namespace forgepulse {

struct PublishResult {
    bool ok;
    int exit_code;
};

class MqttPublisher {
public:
    MqttPublisher(std::string host, std::string port, std::string topic, int retry_count, std::string spool_dir);

    PublishResult publish(const std::string& payload) const;
    int flush_spool(int limit) const;

private:
    PublishResult publish_file(const std::string& file_path) const;
    void spool_payload(const std::string& payload) const;

    std::string host_;
    std::string port_;
    std::string topic_;
    int retry_count_;
    std::string spool_dir_;
};

}  // namespace forgepulse
