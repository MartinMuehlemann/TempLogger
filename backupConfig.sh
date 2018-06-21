#!/bin/sh

DESTINATION_DIR=./system/

mkdir -p $DESTINATION_DIR
cp --parents /etc/network/interfaces $DESTINATION_DIR
cp --parents /etc/dhcpcd.conf $DESTINATION_DIR
cp --parents /etc/dnsmasq.conf $DESTINATION_DIR
cp --parents /boot/config.txt $DESTINATION_DIR # 1-Wire
