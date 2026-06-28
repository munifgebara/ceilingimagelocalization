// Acesso a camera do dispositivo (Web API getUserMedia).
// Independente de framework — usado pelos apps coletor e teste.

/** Inicia o stream da camera traseira e o conecta a um elemento <video>. */
export async function iniciarCamera(elementoVideo, { traseira = true } = {}) {
  const stream = await navigator.mediaDevices.getUserMedia({
    video: { facingMode: traseira ? { ideal: "environment" } : "user" },
    audio: false,
  });
  elementoVideo.srcObject = stream;
  await elementoVideo.play();
  return stream;
}

/** Captura o quadro atual do video e retorna um Blob (JPEG). */
export async function capturarFoto(elementoVideo, { qualidade = 0.92 } = {}) {
  const canvas = document.createElement("canvas");
  canvas.width = elementoVideo.videoWidth;
  canvas.height = elementoVideo.videoHeight;
  canvas.getContext("2d").drawImage(elementoVideo, 0, 0);
  return new Promise((resolve) =>
    canvas.toBlob((blob) => resolve(blob), "image/jpeg", qualidade),
  );
}

/** Para todas as trilhas do stream (libera a camera). */
export function pararCamera(stream) {
  stream?.getTracks().forEach((t) => t.stop());
}
