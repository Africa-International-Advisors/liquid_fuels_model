import path from "node:path";
import { fileURLToPath } from "node:url";
const root = path.dirname(fileURLToPath(import.meta.url));
export default {
  output: "standalone",
  poweredByHeader: false,
  // Documentation is mounted/copied explicitly at runtime, not bundled through tracing.
  outputFileTracingExcludes: {
    "/*": ["./.env*", "./README.md", "./Dockerfile", "./app/**/*", "./components/**/*", "./lib/**/*", "./next.config.mjs", "./postcss.config.mjs", "./tsconfig.json", "./next-env.d.ts", "./package-lock.json"],
  },
  turbopack: { root },
};
