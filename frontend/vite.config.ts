import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The Python backend runs on :8000 (see Makefile `make dev`).
// A dev proxy forwards the API paths so the browser stays same-origin
// and no backend CORS middleware is required.
const BACKEND = "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/health": BACKEND,
      "/providers": BACKEND,
      "/agent/run": BACKEND,
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
