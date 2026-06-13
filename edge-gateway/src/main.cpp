#include <chrono>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

namespace {

struct DeviceProfile {
    std::string code;
    std::string status;
    double temperature_base;
    double pressure_base;
    double voltage_base;
    double yield_base;
};

std::string env_or_default(const char* name, const std::string& fallback) {
    const char* value = std::getenv(name);
    if (value == nullptr || std::string(value).empty()) {
        return fallback;
    }
    return value;
}

std::string iso_timestamp() {
    const auto now = std::chrono::system_clock::now();
    const auto time = std::chrono::system_clock::to_time_t(now);
    std::tm tm{};
#if defined(_WIN32)
    gmtime_s(&tm, &time);
#else
    gmtime_r(&time, &tm);
#endif
    std::ostringstream out;
    out << std::put_time(&tm, "%Y-%m-%dT%H:%M:%SZ");
    return out.str();
}

std::string json_number(double value) {
    std::ostringstream out;
    out << std::fixed << std::setprecision(2) << value;
    return out.str();
}

std::string build_payload(const DeviceProfile& device, int tick) {
    const double wave = std::sin((tick % 60) / 6.0);
    const double drift = std::cos((tick % 45) / 5.0);
    const double temperature = device.temperature_base + wave * 2.4 + (device.code == "ETCH-01" ? 1.8 : 0.0);
    const double pressure = device.pressure_base + drift * 0.22;
    const double voltage = device.voltage_base + wave * 0.05;
    const double yield_rate = device.yield_base + drift * 0.35;

    std::ostringstream json;
    json << "{"
         << "\"device_code\":\"" << device.code << "\","
         << "\"timestamp\":\"" << iso_timestamp() << "\","
         << "\"status\":\"" << device.status << "\","
         << "\"metrics\":{"
         << "\"temperature\":" << json_number(temperature) << ","
         << "\"pressure\":" << json_number(pressure) << ","
         << "\"voltage\":" << json_number(voltage) << ","
         << "\"yield_rate\":" << json_number(yield_rate)
         << "},"
         << "\"payload\":{"
         << "\"lot_code\":\"LOT-RT-240613\","
         << "\"wafer_id\":\"W" << std::setw(2) << std::setfill('0') << ((tick % 6) + 1) << "\","
         << "\"source\":\"edge-gateway\""
         << "}"
         << "}";
    return json.str();
}

bool publish_message(const std::string& host, const std::string& port, const std::string& topic, const std::string& payload) {
    const std::string file_path = "/tmp/forgepulse-telemetry.json";
    {
        std::ofstream file(file_path);
        file << payload;
    }

    std::ostringstream command;
    command << "mosquitto_pub"
            << " -h " << host
            << " -p " << port
            << " -t " << topic
            << " -f " << file_path;

    return std::system(command.str().c_str()) == 0;
}

}  // namespace

int main() {
    const std::string mqtt_host = env_or_default("MQTT_HOST", "mqtt");
    const std::string mqtt_port = env_or_default("MQTT_PORT", "1883");
    const std::string topic = env_or_default("MQTT_TELEMETRY_TOPIC", "forgepulse/telemetry");

    const std::vector<DeviceProfile> devices = {
        {"ETCH-01", "running", 73.2, 2.42, 3.31, 94.6},
        {"CVD-02", "running", 68.4, 2.64, 3.27, 95.1},
        {"PHOTO-03", "warning", 66.8, 2.18, 3.35, 93.8},
        {"TEST-04", "running", 61.5, 1.95, 3.22, 95.4},
    };

    std::cout << "ForgePulse edge gateway started." << std::endl;
    std::cout << "Publishing telemetry to mqtt://" << mqtt_host << ":" << mqtt_port << "/" << topic << std::endl;

    int tick = 0;
    while (true) {
        for (const auto& device : devices) {
            const std::string payload = build_payload(device, tick);
            const bool ok = publish_message(mqtt_host, mqtt_port, topic, payload);
            std::cout << (ok ? "published " : "publish failed ") << device.code << " " << payload << std::endl;
        }

        ++tick;
        std::this_thread::sleep_for(std::chrono::seconds(5));
    }

    return 0;
}
