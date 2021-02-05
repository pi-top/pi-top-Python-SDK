const commandProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const commandHost = window.location.host;
const commandUri = `${commandProtocol}//${commandHost}/command`;

const socket = new WebSocket(commandUri);
const socketReady = new Promise(resolve => socket.onopen = resolve);

const forward = (speed) => socketReady.then(() =>
  socket.send(JSON.stringify({ type: 'FORWARD', data: { speed } }))
);

const stop = () => socketReady.then(() =>
  socket.send(JSON.stringify({ type: 'STOP' }))
);

const leftMotor = (speed) => socketReady.then(() =>
  socket.send(JSON.stringify({ type: 'LEFT_MOTOR', data: { speed } }))
);

const rightMotor = (speed) => socketReady.then(() =>
  socket.send(JSON.stringify({ type: 'RIGHT_MOTOR', data: { speed } }))
);

const text = () => {
  const input = document.getElementById('text-command');
  console.log(input ? input.value : null);
  if (input) {
    socket.send(input.value);
  }
};

window.command = {
  forward,
  stop,
  leftMotor,
  rightMotor,
  text,
}
