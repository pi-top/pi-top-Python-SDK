# Tests

## Running the tests

To run the tests, install the dependencies declared in `requirements.txt`. Then, you can run the tests with `pytest`.

```
$ pip3 install -r tests/requirements.txt
$ pytest --verbose
```

## Using docker

Since it can take a while to download or build the dependencies, you can create a docker image with these pre-loaded. We provide a `Dockerfile` to build an image that can be used to run the tests.

Build the image by running:
```
$ cd tests
$ docker build -t sdk-test-runner .
```

Then, run the tests with:
```
$ docker run \
    --rm \
    -it \
    --volume $PWD:/sdk \
    --workdir /sdk \
    --entrypoint=pytest \
    sdk-test-runner \
    --verbose
```
