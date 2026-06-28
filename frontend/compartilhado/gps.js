// Acesso ao GPS do dispositivo (Web API Geolocation).

/** Obtem a posicao atual (uma vez). Retorna { latitude, longitude, precisao }. */
export function obterPosicao({ timeout = 10000 } = {}) {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Geolocalizacao nao suportada neste dispositivo."));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) =>
        resolve({
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
          precisao: pos.coords.accuracy,
        }),
      (erro) => reject(erro),
      { enableHighAccuracy: true, timeout, maximumAge: 0 },
    );
  });
}
