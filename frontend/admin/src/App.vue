<script setup>
import { onMounted, ref } from "vue";
import { api } from "@compartilhado/api";

const saude = ref("verificando...");
const nome = ref("");
const descricao = ref("");
const mensagem = ref("");

onMounted(async () => {
  try {
    const s = await api.saude();
    saude.value = `API ${s.versao} — banco: ${s.banco}`;
  } catch (e) {
    saude.value = "API indisponivel: " + e.message;
  }
});

async function criar() {
  // No M1 isto chama POST /locais e depois o upload da planta.
  mensagem.value = "Cadastro de local sera habilitado no marco M1 (endpoint /locais).";
}
</script>

<template>
  <main class="tela">
    <h1>Admin — locais e plantas</h1>
    <p class="status">{{ saude }}</p>

    <section class="cartao">
      <h2>Novo local</h2>
      <label>Nome <input v-model="nome" placeholder="Ex.: Shopping Centro" /></label>
      <label>Descricao <textarea v-model="descricao"></textarea></label>
      <button @click="criar">Cadastrar local</button>
      <p class="msg">{{ mensagem }}</p>
    </section>
  </main>
</template>

<style>
body { margin: 0; font-family: system-ui, sans-serif; background: #f3f4f6; color: #111827; }
.tela { max-width: 640px; margin: 0 auto; padding: 24px; }
.cartao { background: #fff; padding: 16px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
label { display: block; margin: 10px 0; }
input, textarea { width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 8px; }
button { margin-top: 8px; padding: 10px 16px; border: 0; border-radius: 8px; background: #2563eb; color: #fff; }
.status { color: #6b7280; }
.msg { color: #b45309; }
</style>
