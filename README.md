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
