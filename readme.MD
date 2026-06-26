## Instructions

### Build MCP image
\# Inside the Dockerfile directory use  
`docker build -t mcp-server .`

### Setup and bring up all local infrastructure

```bash
# Create a shared network
podman network create myapp-net

# Run postgres on it
podman run -d \
  --name postgres \
  -p 5432:5432  \
  --network myapp-net \
  --replace \
  -e POSTGRES_PASSWORD=postgres \
  postgres:16

# Check for exposed port of container
ss -tlnp | grep 5432

# Run MCP app on the same network
podman run --name=MCP-srv -p 8000:8000 --network myapp-net --replace localhost/mcp-server:latest

```

### Postgres DB Table Setup with data
`PGPASSWORD=postgres pgcli -h localhost -p 5432 -U postgres -d postgres`

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL
);

INSERT INTO users (user_id) VALUES ('alex');
```

### MCP Server testing part

```bash
SESSION_ID=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{"roots":{"listChanged":true},"sampling":{}},"clientInfo":{"name":"curl-test","version":"1.0.0"}}}' \
  http://0.0.0.0:8000/mcp \
  -D /dev/stderr 2>&1 | grep "mcp-session-id:" | cut -d' ' -f2 | tr -d '\r')

echo "Session ID: $SESSION_ID"

curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
  http://0.0.0.0:8000/mcp

curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  http://0.0.0.0:8000/mcp | yq .data

 curl -s -X POST \
   -H "Content-Type: application/json" \
   -H "Accept: application/json, text/event-stream" \
   -H "mcp-session-id: $SESSION_ID" \
   -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_user_data","arguments":{"user_id":"alex"}}}' \
   http://0.0.0.0:8000/mcp | yq .

```

### Development
Can use `test_mcp_srv_functs.py` to test the MCP server app using venv.