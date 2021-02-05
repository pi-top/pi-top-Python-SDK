const commandProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const commandHost = window.location.host;
const commandUri = `${commandProtocol}//${commandHost}/command`;

const socket = new WebSocket(commandUri);
const socketReady = new Promise(resolve => socket.onopen = resolve);

const motor_stop = () => socketReady.then(() =>
  socket.send(JSON.stringify({ type: 'motor_stop' }))
);

const motor_move = (data) => socketReady.then(() =>
  socket.send(JSON.stringify({ type: 'motor_move', data: { data } }))
);

window.command = {
  motor_stop,
  motor_move,
}
