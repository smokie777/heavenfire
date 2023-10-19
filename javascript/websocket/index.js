const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 4000 });

console.log('WebSocket server live!');

wss.on('connection', ws => {
  console.log('New client connected!');

  ws.on('message', data => {
    broadcast(data.toString(), ws);
  });

  ws.on('close', () => {
    console.log('Client has disconnected!');
  });
});

const broadcast = (data, sender) => {
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN && client !== sender) {
      client.send(data);
    }
  });
};
