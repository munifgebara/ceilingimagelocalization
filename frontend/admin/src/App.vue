<script setup>
import { computed, onMounted, ref } from "vue";
import { api } from "@compartilhado/api";

const saude = ref("verificando...");
const locais = ref([]);
const selecionado = ref(null);
const plantas = ref([]);
const svgSelecionada = ref("");

// Formulario de local
const nome = ref("");
const descricao = ref("");
const mensagem = ref("");

// Formulario de planta
const arquivo = ref(null);
const nomePlanta = ref("Terreo");
const escala = ref("");
const msgPlanta = ref("");

onMounted(async () => {
  try {
    const s = await api.saude();
    saude.value = `API ${s.versao} — banco: ${s.banco}`;
  } catch (e) {
    saude.value = "API indisponivel: " + e.message;
  }
  await carregarLocais();
});

async function carregarLocais() {
  locais.value = await api.listarLocais();
}

async function criar() {
  mensagem.value = "";
  try {
    const local = await api.criarLocal({ nome: nome.value, descricao: descricao.value });
    nome.value = "";
    descricao.value = "";
    await carregarLocais();
    await selecionar(local);
  } catch (e) {
    mensagem.value = "Erro: " + e.message;
  }
}

async function selecionar(local) {
  selecionado.value = local;
  svgSelecionada.value = "";
  plantas.value = await api.listarPlantas(local.id);
}

async function verPlanta(p) {
  const completa = await api.obterPlanta(p.id);
  svgSelecionada.value = completa.svg;
}

function aoEscolherArquivo(ev) {
  arquivo.value = ev.target.files[0] || null;
}

async function enviarPlanta() {
  msgPlanta.value = "";
  if (!arquivo.value) {
    msgPlanta.value = "Escolha um arquivo SVG.";
    return;
  }
  try {
    const form = new FormData();
    form.append("arquivo", arquivo.value);
    form.append("nome", nomePlanta.value);
    if (escala.value) form.append("escala_m_por_unidade", escala.value);
    const planta = await api.enviarPlanta(selecionado.value.id, form);
    await selecionar(selecionado.value);
    await verPlanta(planta);
    msgPlanta.value = "Planta enviada!";
  } catch (e) {
    msgPlanta.value = "Erro: " + e.message;
  }
}

const temSelecao = computed(() => selecionado.value !== null);
</script>

<template>
  <main class="tela">
    <h1>Admin — locais e plantas</h1>
    <p class="status">{{ saude }}</p>

    <div class="colunas">
      <section class="cartao">
        <h2>Locais</h2>
        <ul class="lista">
          <li
            v-for="l in locais"
            :key="l.id"
            :class="{ ativo: selecionado && selecionado.id === l.id }"
            @click="selecionar(l)"
          >
            {{ l.nome }}
          </li>
          <li v-if="!locais.length" class="vazio">Nenhum local ainda.</li>
        </ul>

        <h3>Novo local</h3>
        <input v-model="nome" placeholder="Nome (ex.: Shopping Centro)" />
        <textarea v-model="descricao" placeholder="Descricao (opcional)"></textarea>
        <button @click="criar">Cadastrar local</button>
        <p class="msg">{{ mensagem }}</p>
      </section>

      <section class="cartao" v-if="temSelecao">
        <h2>{{ selecionado.nome }} — plantas</h2>
        <ul class="lista">
          <li v-for="p in plantas" :key="p.id" @click="verPlanta(p)">
            {{ p.nome }} <small>({{ p.largura }}×{{ p.altura }})</small>
          </li>
          <li v-if="!plantas.length" class="vazio">Sem plantas. Envie um SVG.</li>
        </ul>

        <h3>Enviar planta (SVG)</h3>
        <input type="file" accept=".svg,image/svg+xml" @change="aoEscolherArquivo" />
        <input v-model="nomePlanta" placeholder="Nome do pavimento" />
        <input v-model="escala" placeholder="Escala (metros por unidade, opcional)" />
        <button @click="enviarPlanta">Enviar planta</button>
        <p class="msg">{{ msgPlanta }}</p>

        <div v-if="svgSelecionada" class="preview" v-html="svgSelecionada"></div>
      </section>
    </div>
  </main>
</template>

<style>
body { margin: 0; font-family: system-ui, sans-serif; background: #f3f4f6; color: #111827; }
.tela { max-width: 1000px; margin: 0 auto; padding: 24px; }
.colunas { display: grid; grid-template-columns: 1fr 2fr; gap: 16px; align-items: start; }
.cartao { background: #fff; padding: 16px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
.lista { list-style: none; padding: 0; margin: 0 0 12px; }
.lista li { padding: 8px; border-radius: 8px; cursor: pointer; }
.lista li:hover { background: #f3f4f6; }
.lista li.ativo { background: #dbeafe; font-weight: 600; }
.vazio { color: #9ca3af; cursor: default; }
input, textarea { width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 8px; margin: 6px 0; box-sizing: border-box; }
button { padding: 10px 16px; border: 0; border-radius: 8px; background: #2563eb; color: #fff; cursor: pointer; }
.status { color: #6b7280; }
.msg { color: #b45309; min-height: 1em; }
.preview { margin-top: 12px; border: 1px solid #e5e7eb; border-radius: 8px; padding: 8px; }
.preview svg { max-width: 100%; height: auto; }
@media (max-width: 720px) { .colunas { grid-template-columns: 1fr; } }
</style>
