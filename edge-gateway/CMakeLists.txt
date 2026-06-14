cmake_minimum_required(VERSION 3.20)

project(forgepulse_edge_gateway VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(
    forgepulse-edge-gateway
    src/config.cpp
    src/command_listener.cpp
    src/main.cpp
    src/mqtt_publisher.cpp
    src/telemetry.cpp
)

target_include_directories(forgepulse-edge-gateway PRIVATE include)
