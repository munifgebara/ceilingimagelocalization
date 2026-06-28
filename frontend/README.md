# Frontend — apps web (Vue 3 + Vite, PWA)

Três aplicações PWA (instaláveis, acessam câmera e GPS pelo navegador) que
compartilham código em [`compartilhado/`](compartilhado).

| App | Pasta | Porta dev | O que faz |
|-----|-------|-----------|-----------|
| Admin | [`admin/`](admin) | 5174 | Cadastra locais e faz upload da planta (SVG) |
| Coletor | [`coletor/`](coletor) | 5173 | Tira foto do teto + GPS e marca a posição na planta |
| Teste | [`teste/`](teste) | 5175 | Envia foto + GPS e mostra a posição estimada |

## Código compartilhado

Em [`compartilhado/`](compartilhado), importado nos apps via alias `@compartilhado`:

- `camera.js` — acesso à câmera (`getUserMedia`), captura de foto.
- `gps.js` — posição via `navigator.geolocation`.
- `api.js` — cliente HTTP da API (base em `VITE_API_URL`).
- `planta.js` — conversão de clique → coordenada da planta SVG.

## Rodar um app

```bash
cd frontend/coletor      # ou admin, teste
npm install
npm run dev              # abre em http://localhost:5173
```

> Câmera e GPS no navegador exigem **HTTPS** (ou `localhost`). Em produção isso é
> resolvido pelo Cloudflare Tunnel; em rede local, use `localhost` ou um proxy
> HTTPS.

Configure a URL da API com a variável `VITE_API_URL` (padrão
`http://localhost:8000`).

## Estado atual

Os apps já têm a estrutura, a UI base e a integração com câmera/GPS/API. As
chamadas de escrita (cadastro, envio de fotos, localização) são habilitadas
conforme os marcos do backend (M1, M2, M3).
