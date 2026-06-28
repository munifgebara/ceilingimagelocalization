// Cliente HTTP minimo para a API do projeto.

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function json(resposta) {
  if (!resposta.ok) throw new Error(`Erro ${resposta.status}: ${await resposta.text()}`);
  return resposta.json();
}

export const api = {
  base: BASE,

  saude: () => fetch(`${BASE}/saude`).then(json),

  listarLocais: () => fetch(`${BASE}/locais`).then(json),

  criarLocal: (dados) =>
    fetch(`${BASE}/locais`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    }).then(json),

  // Envia uma foto de mapeamento (multipart).
  enviarFotoMapeamento: (form) =>
    fetch(`${BASE}/fotos`, { method: "POST", body: form }).then(json),

  // Envia uma foto de consulta e recebe a posicao estimada.
  localizar: (form) =>
    fetch(`${BASE}/localizar`, { method: "POST", body: form }).then(json),
};
