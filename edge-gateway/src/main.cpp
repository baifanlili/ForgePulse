#include <chrono>
#include <iostream>
#include <thread>

int main() {
    std::cout << "ForgePulse edge gateway placeholder started." << std::endl;
    std::cout << "Next step: publish semiconductor telemetry to MQTT." << std::endl;

    while (true) {
        std::cout << "heartbeat: SIM-TEST-001" << std::endl;
        std::this_thread::sleep_for(std::chrono::seconds(5));
    }

    return 0;
}
