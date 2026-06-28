import { fileURLToPath, URL } from "node:url";
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";

// App Teste (PWA): envia foto + GPS e mostra a posicao estimada na planta.
export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "Teto — Teste",
        short_name: "Teste",
        description: "Testa a localizacao por foto do teto",
        theme_color: "#1f2937",
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
  server: { host: true, port: 5175 },
});
