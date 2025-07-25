# Simple Synapse (Toy ESB)

This repository contains a **minimal, educational** re-implementation of key ideas behind [Apache Synapse](https://synapse.apache.org/):

* Pluggable transports (HTTP only, for now)
* A mediation core that executes a **sequence of mediators** (Log, Filter, Send)
* XML configuration, hot-reloadable at runtime

> ⚠️  This is *NOT* production-ready—just a few hundred lines to illustrate the architecture.

---

## Quick start

1.  Install dependencies

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  Run the ESB on port 8080:

    ```bash
    python -m simple_synapse.app
    ```

3.  Send a test request:

    ```bash
    curl -H 'X-Forward: true' http://localhost:8080/hello
    ```

   You should see the request proxied to `https://httpbin.org/anything` and the response bubbled back.

---

## Configuration

* All sequences live under `simple_synapse/config/*.xml`.
* Modify `main.xml`, save, and the server will pick up changes on the next request (the loader re-reads disk each time for simplicity).

```xml
<sequence name="main">
    <log level="INFO" message="Received"/>
    <filter expr="'true' == ctx.headers.get('X-Forward')">
        <send url="https://httpbin.org/anything"/>
    </filter>
</sequence>
```

### Supported mediators

| Tag     | Attributes            | Purpose                                  |
| ------- | --------------------- | ---------------------------------------- |
| `<log>` | `level`, `message`    | Logs a message at the specified level.   |
| `<filter>` | `expr`            | Python expression; children run if truthy |
| `<send>` | `url`               | Forwards the message to the given URL     |

Happy hacking! ✨

---

# MCP Services Demo (Two AI Agents)

This repository also ships with a **pair of tiny [Model Context Protocol](https://github.com/modelcontextprotocol) servers** that talk to each other over HTTP.  They are purposely minimal, just enough to show how two MCP-compatible agents can co-operate.

## Directory layout

```
mcp_services/
├── service_b.py       # Service B – answers questions
├── service_a.py       # Service A – asks B, then replies to caller
├── demo_connect.py    # CLI script that triggers the conversation
└── __init__.py
```

## What each service does

1. **Service B** (`mcp_services/service_b.py`)
   • Endpoint: `POST /mcp`  
   • Request JSON: `{ "question": "..." }`  
   • Response JSON: `{ "answer": "..." }` (stubbed, but you can swap in an LLM)

2. **Service A** (`mcp_services/service_a.py`)
   • Endpoint: `POST /mcp`  
   • Looks up `SERVICE_B_URL` (default `http://localhost:9002/mcp`) and forwards the user’s question to Service B.  
   • Returns the **conversation transcript**:

```jsonc
{
  "conversation": [
    { "role": "user", "content": "How are you?" },
    { "role": "assistant", "content": "Service B here; I’m great!" }
  ]
}
```

## Quick start (two terminals + one script)

1.  **Service B** – port 9002

    ```bash
    uvicorn mcp_services.service_b:app --port 9002 --reload
    ```

2.  **Service A** – port 9001 (tell it where B lives)

    ```bash
    SERVICE_B_URL=http://localhost:9002/mcp \
    uvicorn mcp_services.service_a:app --port 9001 --reload
    ```

3.  **Run the demo**

    ```bash
    python -m mcp_services.demo_connect
    ```

    Expected output:

    ```text
    Conversation:
    User: How are you, Service B?
    Assistant: Service B here; thanks for asking: ‘How are you, Service B?’. I’m great!
    ```

## API reference

### Service B

| Method | Path | Body (JSON)                 | Returns (JSON)            |
| ------ | ---- | --------------------------- | ------------------------- |
| POST   | /mcp | `{ "question": "..." }`    | `{ "answer": "..." }`    |

### Service A

| Method | Path | Body (JSON)                 | Returns (JSON)                                |
| ------ | ---- | --------------------------- | --------------------------------------------- |
| POST   | /mcp | `{ "question": "..." }`    | `{ "conversation": [ {role, content}, … ] }` |

Environment variable: **`SERVICE_B_URL`** – override to point Service A at a different B instance.

## Extending the demo

* Replace the canned reply in `service_b.py` with a call to your favourite LLM.
* Add more endpoints or tools that conform to the MCP spec.
* Chain additional services by having Service B consult yet another MCP server.

Have fun exploring agent-to-agent communication! ✨
