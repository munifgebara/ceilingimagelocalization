import { fileURLToPath, URL } from "node:url";
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";

// App Coletor (PWA): tira foto do teto, captura GPS e marca a posicao na planta.
export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "Teto — Coletor",
        short_name: "Coletor",
        description: "Coleta fotos do teto para mapeamento",
        theme_color: "#1f2937",
        background_color: "#111827",
        display: "standalone",
        icons: [{ src: "/icon.svg", sizes: "any", type: "image/svg+xml" }],
      },
    }),
  ],
  resolve: {
    alias: {
      "@compartilhado": fileURLToPath(new URL("../compartilhado", import.meta.url)),
    },
  },
  server: { host: true, port: 5173 },
});
