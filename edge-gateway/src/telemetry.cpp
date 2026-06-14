#include "forgepulse/telemetry.hpp"

#include <chrono>
#include <cmath>
#include <iomanip>
#include <sstream>

namespace forgepulse {
namespace {

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

}  // namespace

std::vector<DeviceProfile> default_device_profiles() {
    return {
        {"ETCH-01", "running", 73.2, 2.42, 3.31, 94.6},
        {"CVD-02", "running", 68.4, 2.64, 3.27, 95.1},
        {"PHOTO-03", "warning", 66.8, 2.18, 3.35, 93.8},
        {"TEST-04", "running", 61.5, 1.95, 3.22, 95.4},
    };
}

std::string build_telemetry_payload(const DeviceProfile& device, int tick) {
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

}  // namespace forgepulse
