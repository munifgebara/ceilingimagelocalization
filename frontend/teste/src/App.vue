<script setup>
import { onBeforeUnmount, ref } from "vue";
import { capturarFoto, iniciarCamera, pararCamera } from "@compartilhado/camera";
import { obterPosicao } from "@compartilhado/gps";
import { api } from "@compartilhado/api";

const video = ref(null);
const status = ref("");
const resultado = ref(null);
let stream = null;

async function ligar() {
  try {
    stream = await iniciarCamera(video.value);
    status.value = "Camera ligada. Aponte para o teto e localize.";
  } catch (e) {
    status.value = "Erro na camera: " + e.message;
  }
}

async function localizar() {
  const blob = await capturarFoto(video.value);
  let pos;
  try {
    pos = await obterPosicao();
  } catch (e) {
    status.value = "Sem GPS: " + e.message;
    return;
  }
  // No M3 monta o multipart e chama POST /localizar.
  status.value =
    "Localizacao sera habilitada no marco M3 (endpoint /localizar). " +
    `Foto ${Math.round(blob.size / 1024)} KB, GPS ${pos.latitude.toFixed(5)}, ${pos.longitude.toFixed(5)}.`;
}

onBeforeUnmount(() => pararCamera(stream));
</script>

<template>
  <main class="tela">
    <h1>Teste — onde estou?</h1>
    <p class="status">{{ status }}</p>
    <video ref="video" autoplay playsinline muted class="video"></video>
    <div class="acoes">
      <button @click="ligar">Ligar camera</button>
      <button @click="localizar">Localizar</button>
    </div>
    <pre v-if="resultado">{{ resultado }}</pre>
    <p class="rodape">API: {{ api.base }}</p>
  </main>
</template>

<style>
body { margin: 0; font-family: system-ui, sans-serif; background: #111827; color: #e5e7eb; }
.tela { max-width: 480px; margin: 0 auto; padding: 16px; }
.video { width: 100%; border-radius: 8px; background: #000; }
.acoes { display: flex; gap: 8px; margin: 12px 0; }
button { flex: 1; padding: 12px; border: 0; border-radius: 8px; background: #16a34a; color: #fff; font-size: 1rem; }
.status { min-height: 1.2em; color: #9ca3af; }
.rodape { color: #6b7280; font-size: 0.8rem; }
</style>
