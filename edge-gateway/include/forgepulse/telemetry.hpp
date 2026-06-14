#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace forgepulse {

struct DeviceProfile {
    std::string code;
    std::string status;
    double temperature_base;
    double pressure_base;
    double voltage_base;
    double yield_base;
};

std::vector<DeviceProfile> default_device_profiles();

std::string build_telemetry_payload(
    const DeviceProfile& device,
    int tick,
    std::uint64_t sequence,
    const std::string& gateway_id,
    const std::string& line_id,
    int sample_period_ms,
    bool inject_fault,
    const std::string& control_mode,
    const std::string& last_command_id,
    const std::string& last_command_type
);

}  // namespace forgepulse
