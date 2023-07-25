FROM debian:bullseye

COPY requirements.txt /tmp/

RUN apt update

# Install pi-topOS apt source
RUN apt install -y git
RUN git clone https://github.com/pi-top/pi-topOS-Apt-Source.git \
  && cp pi-topOS-Apt-Source/keys/* /usr/share/keyrings/ \
  && cp pi-topOS-Apt-Source/sources/pi-top-os.list /etc/apt/sources.list.d/ \
  && rm -r pi-topOS-Apt-Source \
  && apt update

# dlib takes a lot of time to install & build using pip,
# it's faster to install the deb package
RUN DEBIAN_FRONTEND=noninteractive apt install -y \
  cmake \
  python3 \
  python3-dlib \
  python3-pip \
  python3-opencv

RUN pip3 install -r /tmp/requirements.txt
