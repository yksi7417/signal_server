# signal_server

## Step by Step 

### Serve HTML via port 8000 

```python -m http.server -b localhost 8000```

### Launch Signal WebSocket Server 

```python signal_server.py```

### Launch Test Client to verify peer connections

```python client.py```

### Tail scale setups 

As opc, sudo to enable app to run tailscale proxy, then run the proxy command 

```
[opc@instance-20230330-1941 ~]$ sudo tailscale up --operator=app


(base) [app@instance-20230330-1941 signal_server]$ tailscale serve --https=443 http://localhost:8080
Available within your tailnet:

https://oracle-free-instance-20230330-1941.tail356fe.ts.net/
|-- proxy http://localhost:8080

```