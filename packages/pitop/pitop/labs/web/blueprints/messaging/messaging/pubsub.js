const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
const host = window.location.host;
const pubsubUri = `${protocol}//${host}/messaging`;

window.socket = new WebSocket(pubsubUri);
const socketReady = new Promise((resolve) => (socket.onopen = resolve));

window.publish = async function publish(message) {
  await socketReady;
  socket.send(JSON.stringify(message));
};

window.subscribe = function subscribe(messageHandler) {
  socket.onmessage = function onMessage(message) {
    messageHandler(JSON.parse(message.data));
  };
}
