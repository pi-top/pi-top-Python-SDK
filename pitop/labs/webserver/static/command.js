const commandProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const commandHost = window.location.host;
const commandUri = `${commandProtocol}//${commandHost}/command`;

const socket = new WebSocket(commandUri);
const socketReady = new Promise(resolve => socket.onopen = resolve);

const cmd_vel = (data) => socketReady.then(() =>
  socket.send(JSON.stringify({ type: 'cmd_vel', data: { data } }))
);

const pan_tilt = (data) => socketReady.then(() =>
  socket.send(JSON.stringify({ type: 'pan_tilt', data: { data } }))
);

window.command = {
  cmd_vel,
  pan_tilt,
}
