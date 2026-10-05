import { cp, access } from "node:fs/promises";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const frontend = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const standalone = path.join(frontend, ".next", "standalone");
const server = path.join(standalone, "server.js");
try { await access(server); } catch { console.error("No production build found. Run npm run build first."); process.exit(1); }
// Next's standalone server expects its static assets alongside the server bundle.
await cp(path.join(frontend, ".next", "static"), path.join(standalone, ".next", "static"), { recursive: true });
const child = spawn(process.execPath, [server], {
  cwd: standalone, stdio: "inherit", windowsHide: true,
  env: { ...process.env, HOSTNAME: "127.0.0.1", PORT: process.env.PORT || "3100",
    LFM_DOCS_ROOT: process.env.LFM_DOCS_ROOT || path.resolve(frontend, ".."), NEXT_TELEMETRY_DISABLED: "1" },
});
for (const signal of ["SIGINT", "SIGTERM"]) process.on(signal, () => child.kill(signal));
child.on("error", (error) => { console.error(error.message); process.exit(1); });
child.on("exit", (code) => process.exit(code ?? 0));
