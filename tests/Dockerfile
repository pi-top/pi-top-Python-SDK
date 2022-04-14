FROM ubuntu:20.04

COPY requirements.txt /tmp/

RUN apt update

RUN DEBIAN_FRONTEND=noninteractive apt install -y \
    python3 \
    python3-pip \
    cmake \
    python3-opencv

RUN pip3 install -r /tmp/requirements.txt
