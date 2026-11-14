import { defineConfig } from "vitest/config";

export default defineConfig({
  test: { environment: "node", include: ["tests/**/*.test.{ts,tsx}"], maxWorkers: 1 },
  esbuild: { jsx: "automatic" },
});
