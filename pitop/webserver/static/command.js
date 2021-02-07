const commandProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const commandHost = window.location.host;
const commandUri = `${commandProtocol}//${commandHost}/command`;

const socket = new WebSocket(commandUri);
const socketReady = new Promise(resolve => socket.onopen = resolve);

const cmd_vel = (data) => socketReady.then(() =>
  socket.send(JSON.stringify({ type: 'cmd_vel', data: { data } }))
);

const servo_move = (data) => socketReady.then(() =>
  socket.send(JSON.stringify({ type: 'servo_move', data: { data } }))
);

const servo_stop = () => socketReady.then(() =>
  socket.send(JSON.stringify({ type: 'servo_stop' }))
);

window.command = {
  cmd_vel,
  servo_move,
  servo_stop,
}
