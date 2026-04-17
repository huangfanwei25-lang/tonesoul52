"use strict";

const cp = require("child_process");
const path = require("path");
const vscode = require("vscode");

let mcpProcess = null;

function getConfig() {
  return vscode.workspace.getConfiguration("tonesoul");
}

function getRepoRoot() {
  const folder = vscode.workspace.workspaceFolders?.[0];
  return folder?.uri.fsPath || process.cwd();
}

function createOutputChannel() {
  return vscode.window.createOutputChannel("ToneSoul");
}

function updateStatusBar(statusBar, running) {
  statusBar.text = running ? "$(radio-tower) ToneSoul MCP" : "$(circle-large-outline) ToneSoul MCP";
  statusBar.tooltip = running ? "ToneSoul MCP server is running" : "ToneSoul MCP server is idle";
}

function startMcpServer(output, statusBar) {
  if (mcpProcess) {
    vscode.window.showInformationMessage("ToneSoul MCP server is already running.");
    return;
  }

  const pythonPath = getConfig().get("pythonPath", "python");
  const repoRoot = getRepoRoot();
  const args = ["-m", "tonesoul.mcp_server", "--toolset", "gateway"];
  output.appendLine(`[ToneSoul] starting MCP server: ${pythonPath} ${args.join(" ")}`);

  const child = cp.spawn(pythonPath, args, {
    cwd: repoRoot,
    stdio: ["pipe", "pipe", "pipe"],
  });

  child.stdout.on("data", (chunk) => output.append(chunk.toString("utf8")));
  child.stderr.on("data", (chunk) => output.append(chunk.toString("utf8")));
  child.on("exit", (code, signal) => {
    output.appendLine(`[ToneSoul] MCP server exited code=${code ?? "null"} signal=${signal ?? "null"}`);
    mcpProcess = null;
    updateStatusBar(statusBar, false);
  });
  child.on("error", (error) => {
    output.appendLine(`[ToneSoul] MCP server failed: ${error.message}`);
    vscode.window.showErrorMessage(`ToneSoul MCP server failed: ${error.message}`);
    mcpProcess = null;
    updateStatusBar(statusBar, false);
  });

  mcpProcess = child;
  updateStatusBar(statusBar, true);
  output.show(true);
  vscode.window.showInformationMessage("ToneSoul MCP server started.");
}

function stopMcpServer(output, statusBar) {
  if (!mcpProcess) {
    vscode.window.showInformationMessage("ToneSoul MCP server is not running.");
    return;
  }
  output.appendLine("[ToneSoul] stopping MCP server");
  mcpProcess.kill();
  mcpProcess = null;
  updateStatusBar(statusBar, false);
}

function showSlimEntry(output) {
  const pythonPath = getConfig().get("pythonPath", "python");
  const agentId = getConfig().get("agentId", "vscode-shell");
  const repoRoot = getRepoRoot();
  const scriptPath = path.join(repoRoot, "scripts", "start_agent_session.py");

  const completed = cp.spawnSync(
    pythonPath,
    [scriptPath, "--agent", agentId, "--slim", "--no-ack"],
    {
      cwd: repoRoot,
      encoding: "utf8",
    }
  );

  if (completed.status !== 0) {
    const errorText = (completed.stderr || completed.stdout || "unknown error").trim();
    output.appendLine(`[ToneSoul] slim entry failed: ${errorText}`);
    vscode.window.showErrorMessage(`ToneSoul slim entry failed: ${errorText}`);
    return;
  }

  let payload;
  try {
    payload = JSON.parse(completed.stdout);
  } catch (error) {
    output.appendLine(`[ToneSoul] failed to parse slim entry: ${error.message}`);
    vscode.window.showErrorMessage(`ToneSoul slim entry parse failed: ${error.message}`);
    return;
  }

  output.appendLine(JSON.stringify(payload, null, 2));
  output.show(true);
  vscode.window.showInformationMessage(
    `ToneSoul slim entry: readiness=${payload.readiness} tier=${payload.claim_boundary?.current_tier || "unknown"}`
  );
}

function activate(context) {
  const output = createOutputChannel();
  const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 20);
  statusBar.command = "tonesoul.startMcpServer";
  updateStatusBar(statusBar, false);
  statusBar.show();

  context.subscriptions.push(output, statusBar);
  context.subscriptions.push(
    vscode.commands.registerCommand("tonesoul.startMcpServer", () => startMcpServer(output, statusBar))
  );
  context.subscriptions.push(
    vscode.commands.registerCommand("tonesoul.stopMcpServer", () => stopMcpServer(output, statusBar))
  );
  context.subscriptions.push(
    vscode.commands.registerCommand("tonesoul.showSlimEntry", () => showSlimEntry(output))
  );
}

function deactivate() {
  if (mcpProcess) {
    mcpProcess.kill();
    mcpProcess = null;
  }
}

module.exports = {
  activate,
  deactivate,
};
