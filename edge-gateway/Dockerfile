FROM alpine:3.20 AS build

WORKDIR /app
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk add --no-cache cmake g++ make
COPY . .
RUN cmake -S . -B build && cmake --build build --config Release

FROM alpine:3.20
WORKDIR /app
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk add --no-cache libstdc++ mosquitto-clients
COPY --from=build /app/build/forgepulse-edge-gateway /app/forgepulse-edge-gateway
CMD ["/app/forgepulse-edge-gateway"]
