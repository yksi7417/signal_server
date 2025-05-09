const ENV = "prod"; // Change to 'dev', 'uat', or 'prod'

const WS_ENDPOINTS = {
  dev: "ws://localhost:8080/ws",
  uat: "wss://oracle-free-instance-20230330-1941.tail356fe.ts.net/ws",
  prod: "wss://signal-server-eo-7uq.fly.dev/ws",
};

window.APP_CONFIG = {
  env: ENV,
  wsUrl: WS_ENDPOINTS[ENV],
};
