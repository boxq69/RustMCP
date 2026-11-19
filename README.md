# RustMCP

MCP server that lets an AI agent (Claude, Cursor, Codex) manage a
Rust game server over WebRCON.

## Tools

| Tool | What it does |
|---|---|
| `server_info` | `serverinfo`: hostname, players, fps, map |
| `list_players` | `playerlist` as JSON |
| `console_tail` | last N console lines |
| `chat_tail` | last N chat messages |
| `find_command` | search console commands and variables (`find <query>`) |
| `say` | message to global chat |
| `reload_plugin` | `o.reload` / `c.reload`, returns compile errors (Oxide or Carbon is detected automatically) |
| `rcon` | any command; off unless `ALLOW_RAW_COMMANDS=true` |

Even with `ALLOW_RAW_COMMANDS=true`, commands like `quit`, `restart`,
`ownerid`, `kickall`, `harmony.load` and changes to `rcon.*` are blocked.

## Requirements

- [uv](https://docs.astral.sh/uv/): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- A Rust server with `rcon.web 1` (the default)

## Setup

Replace the IP, port and password with your server's RCON settings.

**Claude Code**

```bash
claude mcp add RustMCP -e RCON_HOST=127.0.0.1 -e RCON_PORT=28016 -e RCON_PASSWORD=your-rcon-password -- uvx RustMCP
```

**Codex**

```bash
codex mcp add RustMCP --env RCON_HOST=127.0.0.1 --env RCON_PORT=28016 --env RCON_PASSWORD=your-rcon-password -- uvx RustMCP
```

**Cursor, Claude Desktop and other clients**

Add this to the client's MCP config file:

```json
{
  "mcpServers": {
    "RustMCP": {
      "command": "uvx",
      "args": ["RustMCP"],
      "env": {
        "RCON_HOST": "127.0.0.1",
        "RCON_PORT": "28016",
        "RCON_PASSWORD": "your-rcon-password"
      }
    }
  }
}
```

## Configuration

| Variable | Required | Description |
|---|---|---|
| `RCON_HOST` | yes | Server IP or hostname |
| `RCON_PORT` | yes | RCON port (`rcon.port`) |
| `RCON_PASSWORD` | yes | RCON password (`rcon.password`) |
| `ALLOW_RAW_COMMANDS` | no | `true` enables the `rcon` tool. Default `false` |

## Good to know

- Rust refuses a new RCON connection from the same IP within 1 second
  (`rcon.connectioncooldown`), so commands run one after another with a short pause.
- 5 wrong passwords get your IP banned from RCON for 5 minutes
  (`rcon.maxpasswordfailures`). RustMCP never retries a rejected login.
- Chat, console and player names are written by players. The agent is told to
  treat them as data, but keep `ALLOW_RAW_COMMANDS=false` unless you need it.

## License

MIT
