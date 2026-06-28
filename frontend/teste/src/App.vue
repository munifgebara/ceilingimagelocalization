<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";
import { capturarFoto, iniciarCamera, pararCamera } from "@compartilhado/camera";
import { obterPosicao } from "@compartilhado/gps";
import { api } from "@compartilhado/api";

const video = ref(null);
const svgHost = ref(null);
const status = ref("");

const locais = ref([]);
const localId = ref("");
const plantas = ref([]);
const plantaId = ref("");
const resultado = ref(null);
let stream = null;

onMounted(async () => {
  try {
    locais.value = await api.listarLocais();
    status.value = "Escolha o local, ligue a camera e localize.";
  } catch (e) {
    status.value = "API indisponivel: " + e.message;
  }
});

async function aoTrocarLocal() {
  plantas.value = await api.listarPlantas(localId.value);
  plantaId.value = "";
}

async function aoTrocarPlanta() {
  const p = await api.obterPlanta(plantaId.value);
  if (svgHost.value) svgHost.value.innerHTML = p.svg;
}

async function ligar() {
  try {
    stream = await iniciarCamera(video.value);
    status.value = "Camera ligada. Aponte para o teto e localize.";
  } catch (e) {
    status.value = "Erro na camera: " + e.message;
  }
}

function desenharPonto(x, y) {
  const svg = svgHost.value?.querySelector("svg");
  if (!svg || x == null) return;
  const ns = "http://www.w3.org/2000/svg";
  svg.querySelectorAll(".marcador-teto").forEach((n) => n.remove());
  const c = document.createElementNS(ns, "circle");
  c.setAttribute("cx", x);
  c.setAttribute("cy", y);
  c.setAttribute("r", Math.max(svg.viewBox.baseVal.width || 200, 200) * 0.02);
  c.setAttribute("fill", "rgba(220,38,38,.8)");
  c.setAttribute("stroke", "#fff");
  c.setAttribute("stroke-width", "2");
  c.classList.add("marcador-teto");
  svg.appendChild(c);
}

async function localizar() {
  let pos = null;
  try {
    pos = await obterPosicao();
  } catch {
    status.value = "Sem GPS — localizando só pela imagem.";
  }
  const blob = await capturarFoto(video.value);
  const form = new FormData();
  form.append("imagem", blob, "q.jpg");
  if (localId.value) form.append("local_id", localId.value);
  if (pos) {
    form.append("latitude", pos.latitude);
    form.append("longitude", pos.longitude);
    form.append("gps_precisao", pos.precisao);
  }
  try {
    resultado.value = await api.localizar(form);
    desenharPonto(resultado.value.x, resultado.value.y);
    status.value = `Posicao estimada (confianca ${(resultado.value.confianca * 100).toFixed(0)}%).`;
  } catch (e) {
    status.value = "Erro ao localizar: " + e.message;
  }
}

onBeforeUnmount(() => pararCamera(stream));
</script>

<template>
  <main class="tela">
    <h1>Teste — onde estou?</h1>
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
      <button @click="ligar">Ligar camera</button>
      <button @click="localizar">Localizar</button>
    </div>

    <div ref="svgHost" class="svg-host"></div>

    <div v-if="resultado" class="resultado">
      <p>
        x={{ resultado.x?.toFixed(1) }}, y={{ resultado.y?.toFixed(1) }} —
        confianca {{ (resultado.confianca * 100).toFixed(0) }}%
      </p>
      <p class="cand">{{ resultado.candidatos.length }} candidato(s) avaliado(s)</p>
    </div>
  </main>
</template>

<style>
body { margin: 0; font-family: system-ui, sans-serif; background: #111827; color: #e5e7eb; }
.tela { max-width: 520px; margin: 0 auto; padding: 16px; }
.selecao { display: flex; gap: 8px; margin-bottom: 10px; }
select { flex: 1; padding: 10px; border-radius: 8px; border: 0; }
.video { width: 100%; border-radius: 8px; background: #000; }
.acoes { display: flex; gap: 8px; margin: 12px 0; }
button { flex: 1; padding: 12px; border: 0; border-radius: 8px; background: #16a34a; color: #fff; font-size: 1rem; }
.status { min-height: 1.2em; color: #9ca3af; }
.svg-host { background: #fff; border-radius: 8px; padding: 4px; }
.svg-host svg { max-width: 100%; height: auto; }
.resultado { margin-top: 8px; font-variant-numeric: tabular-nums; }
.cand { color: #9ca3af; }
</style>
