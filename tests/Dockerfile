FROM ubuntu:20.04

COPY requirements.txt /tmp/

env DISPLAY=":0"

RUN apt update

RUN DEBIAN_FRONTEND=noninteractive apt install -y \
    python3 \
    python3-pip \
    cmake \
    python3-opencv \
    xvfb

RUN pip3 install -r /tmp/requirements.txt

CMD bash -c "Xvfb -ac :0 -screen 0 1280x1024x24 > /dev/null 2>&1 &"
