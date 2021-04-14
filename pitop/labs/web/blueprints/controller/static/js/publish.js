const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
const host = window.location.host;
const publishUri = `${protocol}//${host}/publish`;

window.socket = new WebSocket(publishUri);
const socketReady = new Promise((resolve) => (socket.onopen = resolve));

window.publish = async function publish(message) {
  await socketReady;
  socket.send(JSON.stringify(message));
};
