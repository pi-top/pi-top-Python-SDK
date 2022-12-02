# Tests

## Running the tests

To run the tests in your machine, install the dependencies declared in `requirements.txt` and the `xvfb` package, needed to start a virtual display. Then, you can run the tests with `pytest`.

```
$ sudo apt update
$ sudo apt install -y xvfb
$ pip3 install -r tests/requirements.txt
$ export DISPLAY=:0
$ Xvfb -ac :0 -screen 0 1280x1024x24 > /dev/null 2>&1 &
$ pytest --verbose
```

## Using docker

Since it can take a while to download or build the dependencies, you can create a docker image with these pre-loaded. We provide a `Dockerfile` to build an image that can be used to run the tests. We also provide images you can use to run the tests directly.

### Using pi-top test runner image

```
$ docker run \
    --rm \
    -it \
    --volume "$PWD":/sdk \
    --workdir /sdk \
    --entrypoint=pytest \
    pitop/sdk-test-runner \
    --verbose
```

### Building the image

Build the image by running:

```
$ docker build -t sdk-test-runner tests
```

Then, run the tests with:

```
$ docker run \
    --rm \
    -it \
    --volume "$PWD":/sdk \
    --workdir /sdk \
    --entrypoint=pytest \
    sdk-test-runner \
    --verbose
```
