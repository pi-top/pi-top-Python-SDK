This project provides a web client and server for remote controlling a pi-top robot.

### Usage
#### On pi-topOS
All the dependencies for this project should be pre-installed on pi-topOS, so
running it is just a matter of cloning the repo and starting it with
```
python3 run.py
```
Then opening the UI in a browser with the pi-top's IP address as host and port 8070 eg
```
http://localhost:8070/
```

#### Development
We are using Python 3.7 and managing dependencies with
[pipenv](https://github.com/pypa/pipenv)
```
pipenv shell
pipenv sync
python3 run.py
```

Open the webpage in you browser, the server runs on port 8070.
```
http://localhost:8070/
```

### Details
The server accepts 'commands' over a websocket on `/command`.
E.g. using [websocat](https://github.com/vi/websocat):
```
websocat ws://localhost:8070/command
```
- Send `forward` command, speed 50%:
```
{ "type": "FORWARD", "data": { "speed": 50 } }
```
- Send `STOP` command with `sourceScript`:
```
{ "type": "STOP" }
```


### Notes
see also https://github.com/pi-top/further-link
