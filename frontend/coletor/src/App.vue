<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";
import { capturarFoto, iniciarCamera, pararCamera } from "@compartilhado/camera";
import { obterPosicao } from "@compartilhado/gps";
import { pontoNoSvg } from "@compartilhado/planta";
import { api } from "@compartilhado/api";

const video = ref(null);
const svgHost = ref(null);
const status = ref("");

const locais = ref([]);
const localId = ref("");
const plantas = ref([]);
const plantaId = ref("");
const svgPlanta = ref("");
const marca = ref(null); // { x, y }

const fotoBlob = ref(null);
const previewUrl = ref(null);
const posicao = ref(null);
let stream = null;

onMounted(async () => {
  try {
    locais.value = await api.listarLocais();
    status.value = "Escolha o local e a planta.";
  } catch (e) {
    status.value = "API indisponivel: " + e.message;
  }
});

async function aoTrocarLocal() {
  plantas.value = await api.listarPlantas(localId.value);
  plantaId.value = "";
  svgPlanta.value = "";
  marca.value = null;
}

async function aoTrocarPlanta() {
  marca.value = null;
  const p = await api.obterPlanta(plantaId.value);
  svgPlanta.value = p.svg;
}

function marcarNaPlanta(ev) {
  const svg = svgHost.value?.querySelector("svg");
  if (!svg) return;
  marca.value = pontoNoSvg(svg, ev);
}

async function ligarCamera() {
  try {
    stream = await iniciarCamera(video.value);
    status.value = "Camera ligada. Aponte para o teto.";
  } catch (e) {
    status.value = "Erro na camera: " + e.message;
  }
}

async function tirarFoto() {
  fotoBlob.value = await capturarFoto(video.value);
  previewUrl.value = URL.createObjectURL(fotoBlob.value);
  try {
    posicao.value = await obterPosicao();
    status.value = "Foto + GPS ok. Toque na planta para marcar e envie.";
  } catch (e) {
    posicao.value = null;
    status.value = "Foto ok, sem GPS: " + e.message;
  }
}

async function enviar() {
  if (!fotoBlob.value) return (status.value = "Tire uma foto primeiro.");
  if (!marca.value) return (status.value = "Toque na planta para marcar a posicao.");
  try {
    const form = new FormData();
    form.append("imagem", fotoBlob.value, "teto.jpg");
    form.append("local_id", localId.value);
    if (plantaId.value) form.append("planta_id", plantaId.value);
    if (posicao.value) {
      form.append("latitude", posicao.value.latitude);
      form.append("longitude", posicao.value.longitude);
      form.append("gps_precisao", posicao.value.precisao);
    }
    form.append("plan_x", marca.value.x);
    form.append("plan_y", marca.value.y);
    await api.enviarFotoMapeamento(form);
    status.value = "Foto de mapeamento enviada! Pode tirar a proxima.";
    fotoBlob.value = null;
    previewUrl.value = null;
    marca.value = null;
  } catch (e) {
    status.value = "Erro ao enviar: " + e.message;
  }
}

onBeforeUnmount(() => pararCamera(stream));
</script>

<template>
  <main class="tela">
    <h1>Coletor — fotos do teto</h1>
    <p class="status">{{ status }}</p>

    <div class="selecao">
      <select v-model="localId" @change="aoTrocarLocal">
        <option value="" disabled>Local…</option>
        <option v-for="l in locais" :key="l.id" :value="l.id">{{ l.nome }}</option>
      </select>
      <select v-model="plantaId" @change="aoTrocarPlanta" :disabled="!plantas.length">
        <option value="" disabled>Planta…</option>
        <option v-for="p in plantas" :key="p.id" :value="p.id">{{ p.nome }}</option>
      </select>
    </div>

    <video ref="video" autoplay playsinline muted class="video"></video>
    <div class="acoes">
      <button @click="ligarCamera">Ligar camera</button>
      <button @click="tirarFoto">Tirar foto</button>
      <button @click="enviar" :disabled="!fotoBlob || !marca">Enviar</button>
    </div>

    <img v-if="previewUrl" :src="previewUrl" class="preview" alt="previa" />
    <p v-if="posicao" class="gps">
      GPS: {{ posicao.latitude.toFixed(6) }}, {{ posicao.longitude.toFixed(6) }}
      (±{{ Math.round(posicao.precisao) }} m)
    </p>

    <div v-if="svgPlanta" class="planta">
      <p class="dica">Toque/clique na planta para marcar onde tirou a foto:</p>
      <div ref="svgHost" class="svg-host" @click="marcarNaPlanta" v-html="svgPlanta"></div>
      <p v-if="marca" class="marca">
        Posicao marcada: x={{ marca.x.toFixed(1) }}, y={{ marca.y.toFixed(1) }}
      </p>
    </div>
  </main>
</template>

<style>
body { margin: 0; font-family: system-ui, sans-serif; background: #111827; color: #e5e7eb; }
.tela { max-width: 520px; margin: 0 auto; padding: 16px; }
.selecao { display: flex; gap: 8px; margin-bottom: 10px; }
select { flex: 1; padding: 10px; border-radius: 8px; border: 0; }
.video, .preview { width: 100%; border-radius: 8px; background: #000; }
.acoes { display: flex; gap: 8px; margin: 12px 0; }
button { flex: 1; padding: 12px; border: 0; border-radius: 8px; background: #2563eb; color: #fff; font-size: 1rem; }
button:disabled { background: #374151; }
.status { min-height: 1.2em; color: #9ca3af; }
.gps { font-variant-numeric: tabular-nums; }
.dica { color: #9ca3af; }
.svg-host { background: #fff; border-radius: 8px; padding: 4px; }
.svg-host svg { max-width: 100%; height: auto; cursor: crosshair; }
.marca { color: #34d399; }
</style>
