#include "forgepulse/mqtt_publisher.hpp"

#include <algorithm>
#include <cstdlib>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <utility>
#include <vector>

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

std::string monotonic_suffix() {
    const auto now = std::chrono::system_clock::now().time_since_epoch();
    return std::to_string(std::chrono::duration_cast<std::chrono::microseconds>(now).count());
}

}  // namespace

MqttPublisher::MqttPublisher(
    std::string host,
    std::string port,
    std::string topic,
    int retry_count,
    std::string spool_dir
)
    : host_(std::move(host)),
      port_(std::move(port)),
      topic_(std::move(topic)),
      retry_count_(retry_count > 0 ? retry_count : 0),
      spool_dir_(std::move(spool_dir)) {}

PublishResult MqttPublisher::publish_file(const std::string& file_path) const {
    std::ostringstream command;
    command << "mosquitto_pub"
            << " -h " << shell_quote(host_)
            << " -p " << shell_quote(port_)
            << " -t " << shell_quote(topic_)
            << " -f " << shell_quote(file_path);

    const int exit_code = std::system(command.str().c_str());
    return PublishResult{exit_code == 0, exit_code};
}

void MqttPublisher::spool_payload(const std::string& payload) const {
    std::filesystem::create_directories(spool_dir_);
    const std::string file_path = spool_dir_ + "/telemetry-" + monotonic_suffix() + ".json";
    std::ofstream file(file_path);
    file << payload;
}

PublishResult MqttPublisher::publish(const std::string& payload) const {
    const std::string file_path = "/tmp/forgepulse-telemetry-" + monotonic_suffix() + ".json";
    {
        std::ofstream file(file_path);
        file << payload;
    }

    PublishResult result{false, -1};
    for (int attempt = 0; attempt <= retry_count_; ++attempt) {
        result = publish_file(file_path);
        if (result.ok) {
            std::filesystem::remove(file_path);
            return result;
        }
    }

    spool_payload(payload);
    std::filesystem::remove(file_path);
    return result;
}

int MqttPublisher::flush_spool(int limit) const {
    if (limit <= 0 || !std::filesystem::exists(spool_dir_)) {
        return 0;
    }

    std::vector<std::filesystem::directory_entry> entries;
    for (const auto& entry : std::filesystem::directory_iterator(spool_dir_)) {
        if (entry.is_regular_file() && entry.path().extension() == ".json") {
            entries.push_back(entry);
        }
    }

    std::sort(entries.begin(), entries.end(), [](const auto& left, const auto& right) {
        return left.path().filename().string() < right.path().filename().string();
    });

    int flushed = 0;
    for (const auto& entry : entries) {
        if (flushed >= limit) {
            break;
        }

        const PublishResult result = publish_file(entry.path().string());
        if (!result.ok) {
            break;
        }

        std::filesystem::remove(entry.path());
        ++flushed;
    }

    return flushed;
}

}  // namespace forgepulse
