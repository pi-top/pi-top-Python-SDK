#!/bin/bash

pip3 install \
  --extra-index-url=https://packagecloud.io/pi-top/pypi/pypi/simple \
  -e ./packages/common \
  -e ./packages/core \
  -e ./packages/battery \
  -e ./packages/system \
  -e ./packages/pma \
  -e ./packages/keyboard \
  -e ./packages/display \
  -e ./packages/miniscreen \
  -e ./packages/simulation \
  -e ./packages/robotics \
  -e ./packages/processing \
  -e ./packages/camera \
  -e ./packages/cli \
  -e ./packages/pitop
