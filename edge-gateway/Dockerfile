FROM gcc:13 AS build

WORKDIR /app
RUN apt-get update && apt-get install -y cmake && rm -rf /var/lib/apt/lists/*
COPY . .
RUN cmake -S . -B build && cmake --build build --config Release

FROM debian:bookworm-slim
WORKDIR /app
COPY --from=build /app/build/forgepulse-edge-gateway /app/forgepulse-edge-gateway
CMD ["/app/forgepulse-edge-gateway"]
