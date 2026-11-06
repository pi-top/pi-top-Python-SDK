FROM python:3.11-bookworm

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends cmake libgl1 \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt --extra-index-url=https://packagecloud.io/pi-top/pypi/pypi/simple

# Simulation tests use pygame without a display
ENV SDL_VIDEODRIVER=dummy
