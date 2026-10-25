#!/usr/bin/env bash
set -e

echo "=== [Render Build] Compiling C Native Backend Core for Linux ==="
mkdir -p bin reports
gcc -std=c99 -shared -fPIC -Wall -Wextra -Iinclude \
    src/c_backend.c \
    src/ip_calc.c \
    src/vlsm_engine.c \
    src/flsm_engine.c \
    src/supernet_engine.c \
    src/host_inventory.c \
    src/reachability.c \
    src/cisco_export.c \
    -o bin/netlab_core.so

echo "=== [Render Build] Installing Python Dependencies ==="
pip install -r requirements.txt

echo "=== [Render Build] Build Finished Successfully ==="
