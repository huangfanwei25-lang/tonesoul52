# ToneSoul VS Code Skeleton

This is a minimal Phase 5 skeleton for `ToneSoul v1.2`.

Current scope:

- start local `tonesoul.mcp_server`
- stop the local MCP process
- show `session-start --slim` output inside VS Code
- expose a small status bar indicator

This skeleton is intentionally narrow.

It is **not** yet:

- a full MCP client integration
- a sidebar or webview UI
- a packaged marketplace extension
- proof that VS Code is the primary ToneSoul entry surface

## Commands

- `ToneSoul: Start MCP Server`
- `ToneSoul: Stop MCP Server`
- `ToneSoul: Show Slim Entry`

## Configuration

- `tonesoul.pythonPath`
- `tonesoul.agentId`

## Boundary

The extension is a shell around the already-verified v1.2 path:

`session-start --slim -> MCP tools -> deeper shells only when needed`
