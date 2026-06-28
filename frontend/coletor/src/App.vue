<script setup>
import { onBeforeUnmount, ref } from "vue";
import { capturarFoto, iniciarCamera, pararCamera } from "@compartilhado/camera";
import { obterPosicao } from "@compartilhado/gps";
import { api } from "@compartilhado/api";

const video = ref(null);
const status = ref("");
const posicao = ref(null);
const fotoBlob = ref(null);
const previewUrl = ref(null);
let stream = null;

async function ligarCamera() {
  try {
    stream = await iniciarCamera(video.value);
    status.value = "Camera ligada. Aponte para o teto.";
  } catch (e) {
    status.value = "Erro ao abrir a camera: " + e.message;
  }
}

async function tirarFoto() {
  fotoBlob.value = await capturarFoto(video.value);
  previewUrl.value = URL.createObjectURL(fotoBlob.value);
  try {
    posicao.value = await obterPosicao();
    status.value = "Foto capturada com GPS. Marque a posicao na planta e envie.";
  } catch (e) {
    status.value = "Foto capturada, mas sem GPS: " + e.message;
  }
}

async function enviar() {
  // No M2 isto envia foto + GPS + plan_x/plan_y para POST /fotos.
  status.value = "Envio sera habilitado no marco M2 (endpoint /fotos).";
}

onBeforeUnmount(() => pararCamera(stream));
</script>

<template>
  <main class="tela">
    <h1>Coletor — fotos do teto</h1>
    <p class="status">{{ status }}</p>

    <video ref="video" autoplay playsinline muted class="video"></video>

    <div class="acoes">
      <button @click="ligarCamera">Ligar camera</button>
      <button @click="tirarFoto">Tirar foto</button>
      <button @click="enviar" :disabled="!fotoBlob">Enviar</button>
    </div>

    <img v-if="previewUrl" :src="previewUrl" class="preview" alt="previa" />

    <p v-if="posicao" class="gps">
      GPS: {{ posicao.latitude.toFixed(6) }}, {{ posicao.longitude.toFixed(6) }}
      (±{{ Math.round(posicao.precisao) }} m)
    </p>

    <p class="rodape">API: {{ api.base }}</p>
  </main>
</template>

<style>
body { margin: 0; font-family: system-ui, sans-serif; background: #111827; color: #e5e7eb; }
.tela { max-width: 480px; margin: 0 auto; padding: 16px; }
h1 { font-size: 1.2rem; }
.video, .preview { width: 100%; border-radius: 8px; background: #000; }
.acoes { display: flex; gap: 8px; margin: 12px 0; }
button { flex: 1; padding: 12px; border: 0; border-radius: 8px; background: #2563eb; color: #fff; font-size: 1rem; }
button:disabled { background: #374151; }
.status { min-height: 1.2em; color: #9ca3af; }
.gps { font-variant-numeric: tabular-nums; }
.rodape { color: #6b7280; font-size: 0.8rem; }
</style>
