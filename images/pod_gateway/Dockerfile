

FROM ghcr.io/k8s-at-home/pod-gateway:v1.6.1

RUN apk update && apk add iputils openssh-client busybox-extras net-snmp-tools iproute2

COPY ./client_init.sh /bin
