#!/usr/bin/env bash

if [[ ! -d /run/fapolicyd ]]; then mkdir /run/fapolicyd; fi
if [[ ! -p /run/fapolicyd/fapolicyd.fifo ]]; then mkfifo /run/fapolicyd/fapolicyd.fifo; fi

chown "$SUDO_UID" /run/fapolicyd/fapolicyd.fifo

while i=$(cat /run/fapolicyd/fapolicyd.fifo); do echo "$i"; done
