const commandProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
const commandHost = window.location.host;
const commandUri = `${commandProtocol}//${commandHost}/command`;

const socket = new WebSocket(commandUri);
const socketReady = new Promise((resolve) => (socket.onopen = resolve));

window.publish = async function publish(message) {
  await socketReady;
  socket.send(JSON.stringify(message));
};
