// Utilitarios para lidar com a planta baixa em SVG (marcar/ler coordenadas).

/**
 * Converte um clique do mouse/toque em coordenadas internas do SVG (plan_x, plan_y),
 * respeitando o viewBox da planta.
 */
export function pontoNoSvg(elementoSvg, evento) {
  const ponto = elementoSvg.createSVGPoint();
  const origem = evento.touches ? evento.touches[0] : evento;
  ponto.x = origem.clientX;
  ponto.y = origem.clientY;
  const transformado = ponto.matrixTransform(elementoSvg.getScreenCTM().inverse());
  return { x: transformado.x, y: transformado.y };
}
