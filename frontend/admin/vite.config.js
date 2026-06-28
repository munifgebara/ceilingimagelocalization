import { fileURLToPath, URL } from "node:url";
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";

// App Admin (PWA): cadastra locais e faz upload da planta (SVG).
export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "Teto — Admin",
        short_name: "Admin",
        description: "Administracao de locais e plantas",
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
  server: { host: true, port: 5174 },
});
