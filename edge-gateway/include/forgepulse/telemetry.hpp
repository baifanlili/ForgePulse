#pragma once

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

std::string build_telemetry_payload(const DeviceProfile& device, int tick);

}  // namespace forgepulse
