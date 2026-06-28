"""Gera o artigo cientifico do projeto em PDF (reproduzivel).

Layout em duas colunas, com formalizacao matematica, figuras/esquemas (arquitetura,
fluxo em duas fases, pipeline, modelo de dados) e grafico de erro da avaliacao.

Uso:
    pip install reportlab
    python docs/artigo/gerar_artigo.py

Saida: docs/artigo/Localizacao-Indoor-Teto.pdf
Os dados do grafico vem de docs/artigo/dados_avaliacao.json (gerado por
backend/avaliacao/avaliar.py --saida-json).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing, Group, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    FrameBreak,
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

AQUI = Path(__file__).parent

# ----------------------------------------------------------------------------- cores
AZUL = colors.HexColor("#1F2937")
AZUL_CLARO = colors.HexColor("#2563EB")
VERDE = colors.HexColor("#16A34A")
VERDE_CLARO = colors.HexColor("#DCFCE7")
CINZA = colors.HexColor("#6B7280")
CINZA_CLARO = colors.HexColor("#E5E7EB")

# ----------------------------------------------------------------------------- fontes
_DEJAVU = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DejaVuSans", f"{_DEJAVU}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", f"{_DEJAVU}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFontFamily(
    "DejaVuSans", normal="DejaVuSans", bold="DejaVuSans-Bold",
    italic="DejaVuSans", boldItalic="DejaVuSans-Bold",
)
FONTE = "DejaVuSans"
FONTE_B = "DejaVuSans-Bold"

# ----------------------------------------------------------------------------- estilos
TITULO = ParagraphStyle("T", fontName=FONTE_B, fontSize=17, leading=21,
                        alignment=TA_CENTER, textColor=AZUL, spaceAfter=5)
SUBTITULO = ParagraphStyle("S", fontName=FONTE, fontSize=10.5, leading=13,
                           alignment=TA_CENTER, textColor=CINZA, spaceAfter=2)
AUTOR = ParagraphStyle("A", fontName=FONTE, fontSize=9.5, leading=12,
                       alignment=TA_CENTER, spaceAfter=10)
H1 = ParagraphStyle("H1", fontName=FONTE_B, fontSize=11.5, leading=14,
                    textColor=AZUL, spaceBefore=9, spaceAfter=4)
H2 = ParagraphStyle("H2", fontName=FONTE_B, fontSize=10, leading=12.5,
                    textColor=AZUL_CLARO, spaceBefore=6, spaceAfter=3)
CORPO = ParagraphStyle("C", fontName=FONTE, fontSize=9, leading=12.5,
                       alignment=TA_JUSTIFY, spaceAfter=5)
RESUMO = ParagraphStyle("R", fontName=FONTE, fontSize=9, leading=12.5,
                        alignment=TA_JUSTIFY, leftIndent=0.8 * cm, rightIndent=0.8 * cm,
                        spaceAfter=4)
EQ = ParagraphStyle("EQ", fontName=FONTE, fontSize=9.5, leading=15,
                    alignment=TA_CENTER, spaceBefore=3, spaceAfter=5, textColor=AZUL)
LEG = ParagraphStyle("LEG", fontName=FONTE, fontSize=8, leading=10,
                     alignment=TA_CENTER, textColor=CINZA, spaceAfter=8, spaceBefore=2)
REF = ParagraphStyle("REF", fontName=FONTE, fontSize=8, leading=10.5,
                     alignment=TA_JUSTIFY, leftIndent=0.4 * cm, firstLineIndent=-0.4 * cm,
                     spaceAfter=2)
ITEM = ParagraphStyle("I", fontName=FONTE, fontSize=9, leading=12.5, alignment=TA_JUSTIFY)

CW = 238  # largura util das figuras (cabe na coluna)


def par(t):
    return Paragraph(t, CORPO)


def lista(itens):
    return ListFlowable(
        [ListItem(Paragraph(t, ITEM), leftIndent=8) for t in itens],
        bulletType="bullet", start="•", leftIndent=12, spaceAfter=5,
    )


def figura(drawing, legenda):
    return KeepTogether([drawing, Paragraph(legenda, LEG)])


# ----------------------------------------------------------------------------- desenhos
def _seta(d, x, y0, y1):
    d.add(Line(x, y0, x, y1, strokeColor=CINZA, strokeWidth=1))
    s = 4 if y1 < y0 else -4
    d.add(Polygon([x - 3, y1 + s, x + 3, y1 + s, x, y1], fillColor=CINZA, strokeColor=CINZA))


def _cadeia(d, cx, top, passos, bw=210, bh=22, gap=12, fill=AZUL_CLARO, fcor=colors.white, fs=7.5):
    y = top
    for i, s in enumerate(passos):
        d.add(Rect(cx - bw / 2, y - bh, bw, bh, rx=5, ry=5, fillColor=fill, strokeColor=AZUL))
        d.add(String(cx, y - bh / 2 - 3, s, textAnchor="middle", fontName=FONTE, fontSize=fs,
                     fillColor=fcor))
        if i < len(passos) - 1:
            _seta(d, cx, y - bh, y - bh - gap)
        y -= bh + gap
    return y


def fig_arquitetura():
    W, H = CW, 175
    d = Drawing(W, H)
    apps = ["App Admin", "App Coletor", "App Teste"]
    bw, bh = 72, 24
    gap = (W - 3 * bw) / 4
    for i, a in enumerate(apps):
        x = gap + i * (bw + gap)
        d.add(Rect(x, H - bh, bw, bh, rx=5, ry=5, fillColor=VERDE_CLARO, strokeColor=VERDE))
        d.add(String(x + bw / 2, H - bh / 2 - 3, a, textAnchor="middle", fontName=FONTE,
                     fontSize=7.5))
        d.add(Line(x + bw / 2, H - bh, W / 2, H - bh - 16, strokeColor=CINZA, strokeWidth=0.8))
    api_y = H - bh - 16 - 30
    d.add(Rect(W / 2 - 75, api_y, 150, 28, rx=6, ry=6, fillColor=AZUL_CLARO, strokeColor=AZUL))
    d.add(String(W / 2, api_y + 14 - 3, "API FastAPI (Python)", textAnchor="middle",
                 fontName=FONTE_B, fontSize=8.5, fillColor=colors.white))
    d.add(String(W / 2, api_y + 4, "embeddings · filtro · match · interpolação",
                 textAnchor="middle", fontName=FONTE, fontSize=6, fillColor=colors.white))
    _seta(d, W / 2, api_y, api_y - 16)
    db_y = api_y - 16 - 28
    d.add(Rect(W / 2 - 90, db_y, 180, 26, rx=6, ry=6, fillColor=AZUL, strokeColor=AZUL))
    d.add(String(W / 2, db_y + 13 - 3, "PostgreSQL + pgvector + earthdistance",
                 textAnchor="middle", fontName=FONTE, fontSize=7, fillColor=colors.white))
    # storage
    d.add(Rect(W / 2 - 55, db_y - 34, 110, 22, rx=5, ry=5, fillColor=colors.white,
               strokeColor=CINZA, strokeDashArray=[2, 2]))
    d.add(String(W / 2, db_y - 34 + 11 - 3, "volume: imagens", textAnchor="middle",
                 fontName=FONTE, fontSize=6.5, fillColor=CINZA))
    _seta(d, W / 2 - 30, db_y, db_y - 12)
    return d


def fig_fases():
    W, H = CW, 168
    d = Drawing(W, H)
    d.add(String(W * 0.27, H - 8, "Mapeamento", textAnchor="middle", fontName=FONTE_B,
                 fontSize=8.5, fillColor=AZUL))
    d.add(String(W * 0.75, H - 8, "Consulta", textAnchor="middle", fontName=FONTE_B,
                 fontSize=8.5, fillColor=VERDE))
    _cadeia(d, W * 0.27, H - 14, ["Foto + GPS", "Marca x,y", "Embedding", "Grava no banco"],
            bw=104, bh=20, gap=10, fill=AZUL_CLARO, fs=7)
    _cadeia(d, W * 0.75, H - 14, ["Foto + GPS", "Embedding", "/localizar", "x,y + confiança"],
            bw=104, bh=20, gap=10, fill=VERDE, fs=7)
    return d


def fig_pipeline():
    W, H = CW, 205
    d = Drawing(W, H)
    passos = [
        "Foto do teto + GPS",
        "1. Filtro por raio de GPS (earthdistance)",
        "2. Top-N por similaridade (pgvector)",
        "3. Verificação geométrica (ORB + RANSAC)",
        "4. Interpolação ponderada de (x, y)",
        "Resposta: x, y, confiança, candidatos",
    ]
    cores = [AZUL, AZUL_CLARO, AZUL_CLARO, AZUL_CLARO, AZUL_CLARO, VERDE]
    y = H
    bw, bh, gap = 216, 24, 9
    for i, s in enumerate(passos):
        d.add(Rect(W / 2 - bw / 2, y - bh, bw, bh, rx=5, ry=5, fillColor=cores[i],
                   strokeColor=AZUL))
        d.add(String(W / 2, y - bh / 2 - 3, s, textAnchor="middle", fontName=FONTE,
                     fontSize=7.3, fillColor=colors.white))
        if i < len(passos) - 1:
            _seta(d, W / 2, y - bh, y - bh - gap)
        y -= bh + gap
    return d


def fig_modelo():
    W, H = CW, 222
    d = Drawing(W, H)

    def entidade(x, y, w, titulo, campos):
        h = 15 + len(campos) * 10 + 3
        d.add(Rect(x, y - h, w, h, fillColor=colors.white, strokeColor=AZUL))
        d.add(Rect(x, y - 15, w, 15, fillColor=AZUL, strokeColor=AZUL))
        d.add(String(x + w / 2, y - 11, titulo, textAnchor="middle", fontName=FONTE_B,
                     fontSize=8, fillColor=colors.white))
        for i, c in enumerate(campos):
            d.add(String(x + 6, y - 26 - i * 10, c, fontName=FONTE, fontSize=6.5,
                         fillColor=AZUL))
        return h

    cx = W / 2
    h1 = entidade(cx - 55, H, 110, "local", ["id", "nome", "descrição"])
    y2 = H - h1 - 22
    h2 = entidade(cx - 55, y2, 110, "planta", ["id, local_id", "svg, escala", "largura, altura"])
    y3 = y2 - h2 - 22
    entidade(cx - 75, y3, 150, "foto",
             ["id, local_id, planta_id", "latitude, longitude, gps_precisao",
              "plan_x, plan_y", "embedding vector(512)", "tipo"])
    _seta(d, cx, H - h1, H - h1 - 22)
    d.add(String(cx + 6, H - h1 - 13, "1..N", fontName=FONTE, fontSize=6, fillColor=CINZA))
    _seta(d, cx, y2 - h2, y3)
    d.add(String(cx + 6, y2 - h2 - 11, "1..N", fontName=FONTE, fontSize=6, fillColor=CINZA))
    return d


def fig_grafico_erro():
    caminho = AQUI / "dados_avaliacao.json"
    if not caminho.exists():
        return None
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    erros = dados["erros_m"]
    vmax = max(0.5, math.ceil(max(erros) * 1.25 * 4) / 4)

    W, H = CW, 165
    d = Drawing(W, H)
    bc = VerticalBarChart()
    bc.x, bc.y, bc.width, bc.height = 30, 24, 200, 120
    bc.data = [erros]
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = vmax
    bc.valueAxis.valueStep = vmax / 4
    bc.valueAxis.labels.fontName = FONTE
    bc.valueAxis.labels.fontSize = 6
    bc.categoryAxis.labels.fontName = FONTE
    bc.categoryAxis.labels.fontSize = 5
    bc.categoryAxis.categoryNames = [str(i + 1) if (i % 5 == 0) else "" for i in range(len(erros))]
    bc.bars[0].fillColor = AZUL_CLARO
    bc.barWidth = 4
    d.add(bc)
    # eixo y rotulo
    g = Group(String(0, 0, "erro (m)", fontName=FONTE, fontSize=6.5, fillColor=AZUL))
    g.translate(10, 60)
    g.rotate(90)
    d.add(g)
    d.add(String(130, 6, "posição mapeada", textAnchor="middle", fontName=FONTE, fontSize=6.5,
                 fillColor=AZUL))
    # mediana
    med = dados["mediana_m"]
    ymed = bc.y + (med / vmax) * bc.height
    d.add(Line(bc.x, ymed, bc.x + bc.width, ymed, strokeColor=VERDE, strokeWidth=0.8,
               strokeDashArray=[3, 2]))
    d.add(String(bc.x + bc.width, ymed + 2, f"mediana {med:.2f} m", textAnchor="end",
                 fontName=FONTE, fontSize=6, fillColor=VERDE))
    return d


# ----------------------------------------------------------------------------- documento
def _rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONTE, 7.5)
    canvas.setFillColor(CINZA)
    canvas.drawString(1.6 * cm, 1.0 * cm, "Localização Indoor Baseada em Imagens do Teto")
    canvas.drawRightString(A4[0] - 1.6 * cm, 1.0 * cm, f"Página {doc.page}")
    canvas.restoreState()


def construir() -> Path:
    saida = AQUI / "Localizacao-Indoor-Teto.pdf"
    PW, PH = A4
    M = 1.6 * cm
    GUT = 0.7 * cm
    FOOT = 1.4 * cm
    usable = PW - 2 * M
    colw = (usable - GUT) / 2
    header_h = 8.6 * cm

    header = Frame(M, PH - M - header_h, usable, header_h, id="cab",
                   leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    l1 = Frame(M, FOOT, colw, PH - M - header_h - 0.3 * cm - FOOT, id="l1",
               leftPadding=0, rightPadding=0)
    r1 = Frame(M + colw + GUT, FOOT, colw, PH - M - header_h - 0.3 * cm - FOOT, id="r1",
               leftPadding=0, rightPadding=0)
    lc = Frame(M, FOOT, colw, PH - M - FOOT, id="lc", leftPadding=0, rightPadding=0)
    rc = Frame(M + colw + GUT, FOOT, colw, PH - M - FOOT, id="rc", leftPadding=0, rightPadding=0)

    doc = BaseDocTemplate(
        str(saida), pagesize=A4, title="Localizacao Indoor Baseada em Imagens do Teto",
        author="Munif Gebara",
    )
    doc.addPageTemplates([
        PageTemplate(id="primeira", frames=[header, l1, r1], onPage=_rodape),
        PageTemplate(id="resto", frames=[lc, rc], onPage=_rodape),
    ])

    e = []
    # ------------------------------------------------------------------ cabecalho
    e.append(Paragraph("Localização Indoor Baseada em Imagens do Teto", TITULO))
    e.append(Paragraph("Estimativa de posição em ambientes fechados por reconhecimento visual "
                       "do teto auxiliado por GPS aproximado", SUBTITULO))
    e.append(Spacer(1, 3))
    e.append(Paragraph("Munif Gebara · Projeto de pesquisa · Junho de 2026", AUTOR))
    e.append(HRFlowable(width="100%", color=CINZA_CLARO))
    e.append(Spacer(1, 4))
    e.append(Paragraph("Resumo", H2))
    e.append(Paragraph(
        "A localização de pessoas e ativos em ambientes fechados é um problema relevante e ainda "
        "mal resolvido: o GPS degrada-se sob coberturas e lajes, e soluções por Wi-Fi ou Bluetooth "
        "exigem infraestrutura dedicada e recalibração frequente. Este trabalho propõe e implementa "
        "um sistema que estima a posição do usuário sobre a planta baixa a partir de uma fotografia "
        "do teto combinada com uma leitura de GPS de baixa precisão. A hipótese central é que o teto "
        "é uma referência visual estável — pouca oclusão por pessoas, baixa variação temporal e "
        "iluminação relativamente constante — adequada ao reconhecimento visual de lugar. O sistema "
        "combina um filtro geográfico grosseiro, busca por similaridade de embeddings de imagem e "
        "verificação geométrica opcional, seguidos de interpolação ponderada da posição. "
        "Apresentamos a formalização do método, a arquitetura, a implementação (API em "
        "Python/FastAPI, PostgreSQL com pgvector e earthdistance, e três aplicativos web "
        "progressivos) e uma avaliação em cenário sintético, na qual o sistema obteve erro mediano "
        "de aproximadamente 0,6 m e 100% de acertos dentro de 2 m. Discutimos limitações e "
        "delineamos a avaliação prática com dados reais como principal trabalho futuro.", RESUMO))
    e.append(Paragraph("<b>Palavras-chave:</b> localização indoor; reconhecimento visual de lugar; "
                       "embeddings de imagem; pgvector; PostgreSQL; FastAPI.", RESUMO))
    e.append(NextPageTemplate("resto"))
    e.append(FrameBreak())

    # ------------------------------------------------------------------ 1 Introducao
    e.append(Paragraph("1. Introdução", H1))
    e.append(par(
        "Sistemas de navegação por satélite (GNSS) revolucionaram a localização em ambientes "
        "abertos, mas sua precisão cai drasticamente em ambientes internos, onde o sinal é atenuado "
        "e sofre múltiplos caminhos. Em shopping centers, aeroportos e hospitais, isso inviabiliza "
        "orientação ao usuário, logística e análise de fluxo. Abordagens por rádio (Wi-Fi "
        "<i>fingerprinting</i>, balizas Bluetooth, UWB) alcançam boa precisão, mas dependem de "
        "infraestrutura instalada e recalibração periódica, elevando custo e manutenção."))
    e.append(par(
        "A visão computacional é uma alternativa atraente: o ambiente já é rico em informação "
        "visual e o smartphone do usuário dispõe de câmera e GPS. O reconhecimento visual de lugar "
        "(<i>Visual Place Recognition</i>, VPR) identifica onde uma imagem foi capturada comparando-a "
        "com uma base de referência. Fotos ao nível dos olhos, porém, sofrem com oclusão por "
        "pessoas, mudanças de vitrines e variações de iluminação."))
    e.append(par(
        "Este trabalho explora usar o <b>teto</b> como referência. Tetos são visualmente estáveis, "
        "raramente ocluídos por pessoas e têm iluminação mais uniforme, tornando-os âncoras visuais "
        "confiáveis. A Figura 1 mostra a arquitetura geral do sistema."))
    e.append(figura(fig_arquitetura(),
                    "Figura 1. Arquitetura: três PWAs consomem a API, que persiste dados e "
                    "embeddings no PostgreSQL e as imagens em volume."))

    # ------------------------------------------------------------------ 2 Hipotese
    e.append(Paragraph("2. Hipótese e objetivos", H1))
    e.append(par(
        "<b>Hipótese.</b> Dada uma planta baixa e uma base de fotografias do teto rotuladas com a "
        "posição em que foram tiradas, é possível estimar a posição de uma nova fotografia do teto "
        "sobre a planta, usando o GPS apenas como filtro grosseiro e a imagem como discriminador "
        "fino. A Figura 2 resume as duas fases de operação."))
    e.append(figura(fig_fases(),
                    "Figura 2. As duas fases: mapeamento (coleta rotulada) e consulta (estimativa "
                    "da posição)."))
    e.append(par("<b>Objetivos:</b>"))
    e.append(lista([
        "Implementar uma API que receba foto do teto + GPS e devolva (x, y) na planta com confiança.",
        "Construir o fluxo de mapeamento e de consulta em aplicativos web.",
        "Definir e medir uma métrica de erro em metros, validando o método.",
        "Estabelecer base extensível para modelos de visão mais fortes.",
    ]))

    # ------------------------------------------------------------------ 3 Trabalhos relacionados
    e.append(Paragraph("3. Trabalhos relacionados", H1))
    e.append(par(
        "<b>Descritores visuais.</b> O reconhecimento de lugar evoluiu de descritores locais "
        "clássicos — SIFT [1] e ORB [2], casados e filtrados por RANSAC [3] — para descritores "
        "globais aprendidos, como NetVLAD [4], e, recentemente, para características "
        "auto-supervisionadas de propósito geral como DINOv2 [5]. Para verificação geométrica, "
        "SuperPoint [6] e LightGlue [7] superam pipelines clássicos. O descritor de imagem reduzida "
        "(<i>tiny image</i>) [8] é uma linha de base simples e eficiente para recuperação."))
    e.append(par(
        "<b>Localização indoor.</b> Soluções por rádio (Wi-Fi <i>fingerprinting</i>, BLE, UWB) são "
        "precisas, mas dependem de infraestrutura e calibração. Abordagens visuais dispensam "
        "hardware adicional; o uso específico do teto, menos sujeito a oclusão e mudanças, é "
        "comparativamente pouco explorado e é o foco deste trabalho."))
    e.append(par(
        "<b>Sistemas.</b> A extensão pgvector [9] habilita busca aproximada por vizinhos em "
        "PostgreSQL, e a extensão earthdistance permite consultas geográficas por raio sem a "
        "complexidade do PostGIS. Combinamos essas peças num pipeline híbrido específico para o teto."))

    # ------------------------------------------------------------------ 4 Metodo
    e.append(Paragraph("4. Arquitetura e método", H1))
    e.append(Paragraph("4.1 Pipeline de localização", H2))
    e.append(par(
        "A consulta percorre quatro etapas encadeadas (Figura 3): filtro geográfico, busca por "
        "similaridade, verificação geométrica opcional e interpolação da posição."))
    e.append(figura(fig_pipeline(),
                    "Figura 3. Pipeline de localização: do par foto+GPS à posição estimada."))

    e.append(Paragraph("4.2 Modelo de dados", H2))
    e.append(par(
        "Três entidades (Figura 4): <b>local</b> (o ambiente), <b>planta</b> (SVG com escala em "
        "metros por unidade) e <b>foto</b> (imagem do teto com GPS, posição na planta, embedding e "
        "tipo). Um índice GiST sobre <font face='Courier'>ll_to_earth(lat, lon)</font> sustenta o "
        "filtro por raio e um índice HNSW sobre o embedding sustenta a busca por similaridade."))
    e.append(figura(fig_modelo(),
                    "Figura 4. Modelo de dados e cardinalidades."))

    e.append(Paragraph("4.3 Formalização", H2))
    e.append(par(
        "Seja I uma imagem do teto. O embedding e ∈ ℝ⁵¹² é obtido convertendo I para tons de cinza, "
        "redimensionando para 32×16, achatando no vetor v e normalizando:"))
    e.append(Paragraph("e = (v − μ) / ‖v − μ‖<sub>2</sub>,   v ∈ ℝ<super>512</super>", EQ))
    e.append(par(
        "onde μ é a média de v (invariância a brilho). Como os embeddings são normalizados, a "
        "distância de cosseno e a similaridade entre a consulta q e uma referência i são:"))
    e.append(Paragraph("d(e<sub>q</sub>, e<sub>i</sub>) = 1 − e<sub>q</sub> · e<sub>i</sub>,    "
                       "s<sub>i</sub> = 1 − d(e<sub>q</sub>, e<sub>i</sub>)", EQ))
    e.append(par(
        "O conjunto de candidatos C é restrito por proximidade geográfica, com raio r dependente da "
        "imprecisão do GPS:"))
    e.append(Paragraph("C = { i : tipo<sub>i</sub> = mapeamento  ∧  dist<sub>geo</sub>"
                       "(g<sub>q</sub>, g<sub>i</sub>) ≤ r }", EQ))
    e.append(par(
        "Cada candidato recebe um peso que cresce com a similaridade e, quando há verificação "
        "geométrica, com o número de <i>inliers</i>:"))
    e.append(Paragraph("w<sub>i</sub> = max(s<sub>i</sub>, 0)<super>2</super> · (1 + inliers<sub>i</sub>)",
                       EQ))
    e.append(par("A posição é a média ponderada das posições dos candidatos:"))
    e.append(Paragraph("(x̂, ŷ) = ( ∑<sub>i</sub> w<sub>i</sub> x<sub>i</sub> / ∑<sub>i</sub> "
                       "w<sub>i</sub> ,  ∑<sub>i</sub> w<sub>i</sub> y<sub>i</sub> / "
                       "∑<sub>i</sub> w<sub>i</sub> )", EQ))
    e.append(par("e o erro de localização, em metros, usa a escala da planta:"))
    e.append(Paragraph("ε = ‖(x̂, ŷ) − (x, y)‖<sub>2</sub> · escala", EQ))

    e.append(Paragraph("4.4 Representação e filtro geográfico", H2))
    e.append(par(
        "O backend padrão é o descritor <i>tiny-image</i> acima, que mantém o serviço leve (sem "
        "dependências pesadas) e valida o pipeline de ponta a ponta; a arquitetura permite trocá-lo "
        "por um backend forte (p. ex., DINOv2) sem alterar o restante. Como o PostgreSQL disponível "
        "não inclui PostGIS, o filtro por raio usa <font face='Courier'>cube</font>/"
        "<font face='Courier'>earthdistance</font>: <font face='Courier'>ll_to_earth</font> projeta "
        "a coordenada em um ponto 3D e <font face='Courier'>earth_box</font>/"
        "<font face='Courier'>earth_distance</font> realizam a busca por proximidade com índice GiST."))

    # ------------------------------------------------------------------ 5 Implementacao
    e.append(Paragraph("5. Implementação", H1))
    e.append(par(
        "A API usa <b>FastAPI</b> (Python), persistência em <b>PostgreSQL 17</b> (pgvector) com as "
        "extensões <i>vector</i>, <i>cube</i> e <i>earthdistance</i>, e migrações com Alembic; as "
        "imagens ficam em volume persistente. O front-end são três PWAs em <b>Vue 3 + Vite</b> "
        "(admin, coletor e teste) que compartilham módulos de câmera, GPS e cliente HTTP. A "
        "implantação é em <b>Kubernetes (k3s)</b> com Ingress Traefik; a integração contínua "
        "(GitHub Actions) executa estilo e testes a cada alteração, e o desenvolvimento seguiu o "
        "fluxo <i>issue</i> → ramo → <i>Pull Request</i> → integração."))

    # ------------------------------------------------------------------ 6 Avaliacao
    e.append(Paragraph("6. Avaliação experimental", H1))
    e.append(par(
        "Realizamos uma avaliação controlada e reproduzível para validar o pipeline e o método de "
        "medição antes da coleta de dados reais. Cria-se um local com planta de 1000×1000 unidades e "
        "escala de 0,05 m/unidade (ambiente de ~50 m). Mapeiam-se 25 posições em grade, cada uma com "
        "um padrão visual distinto. Para cada posição, gera-se uma consulta a partir da mesma imagem "
        "perturbada com ruído gaussiano (σ = 18) e variação de brilho (+20), simulando recaptura. O "
        "erro é a distância à posição verdadeira, convertida em metros pela escala (Tabela 1, "
        "Figura 5)."))

    dados = [
        ["Métrica", "Unid.", "Metros"],
        ["Erro mediano", "11,90", "0,595"],
        ["Erro médio", "10,76", "0,538"],
        ["Erro máximo", "18,93", "0,947"],
        ["Acerto (≤ 2 m)", "—", "100%"],
    ]
    tab = Table(dados, colWidths=[CW * 0.5, CW * 0.22, CW * 0.28])
    tab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), FONTE_B),
        ("FONTNAME", (0, 1), (-1, -1), FONTE),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, CINZA_CLARO),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    e.append(tab)
    e.append(Paragraph("Tabela 1. Resultados da avaliação sintética (n = 25, tiny-image).", LEG))
    grafico = fig_grafico_erro()
    if grafico is not None:
        e.append(figura(grafico,
                        "Figura 5. Erro de localização por posição mapeada; todas abaixo do "
                        "limiar de 2 m."))
    e.append(par(
        "O sistema localizou corretamente todas as consultas dentro de 2 m, com erro mediano de "
        "cerca de 0,6 m. O resíduo decorre da interpolação ponderada, que mistura o candidato "
        "correto com vizinhos de baixa semelhança. O objetivo é verificar a corretude do pipeline e "
        "da medição; os números não devem ser extrapolados para condições reais."))

    # ------------------------------------------------------------------ 7 Discussao
    e.append(Paragraph("7. Discussão e limitações", H1))
    e.append(lista([
        "<b>Backend de embedding.</b> O tiny-image é sensível a rotação, escala e iluminação; "
        "padrões de teto repetitivos podem confundi-lo.",
        "<b>Avaliação sintética.</b> Valida o método, não a precisão em campo; não captura variação "
        "de pose da câmera nem mudanças reais do ambiente.",
        "<b>GPS indoor.</b> O filtro pressupõe GPS minimamente informativo; sem sinal, o raio "
        "precisa ser ampliado.",
        "<b>Georreferência.</b> GPS e coordenadas da planta são, por ora, independentes; a conversão "
        "entre eles fica para fase posterior.",
    ]))

    # ------------------------------------------------------------------ 8 Trabalhos futuros
    e.append(Paragraph("8. Trabalhos futuros", H1))
    e.append(lista([
        "<b>Avaliação prática com dados reais</b> em um ambiente real, com posição de referência "
        "conhecida, medindo erro em metros sob variação de horário e de aparelho.",
        "<b>Embeddings fortes</b> (DINOv2, NetVLAD) comparados em precisão, latência e custo.",
        "<b>Verificação geométrica moderna</b> (SuperPoint + LightGlue) versus ORB/RANSAC.",
        "<b>Calibração</b> de raio, top-N e limiares por local.",
        "<b>Georreferência da planta</b> com pontos de controle (fase 2).",
        "<b>Operação</b>: exposição externa segura, monitoramento e reindexação incremental.",
    ]))

    # ------------------------------------------------------------------ 9 Conclusao
    e.append(Paragraph("9. Conclusão", H1))
    e.append(par(
        "Apresentamos um sistema completo e funcional de localização indoor baseado em imagens do "
        "teto, do modelo de dados à API, aos aplicativos e à implantação em Kubernetes. A avaliação "
        "confirmou a corretude do pipeline e do método de medição, com erro mediano sub-métrico em "
        "cenário controlado, sustentando a hipótese de que o teto é uma referência visual "
        "conveniente e motivando a avaliação prática com dados reais."))

    # ------------------------------------------------------------------ Referencias
    e.append(Paragraph("Referências", H1))
    refs = [
        "[1] Lowe, D. G. Distinctive image features from scale-invariant keypoints. IJCV, 2004.",
        "[2] Rublee, E. et al. ORB: An efficient alternative to SIFT or SURF. ICCV, 2011.",
        "[3] Fischler, M. A.; Bolles, R. C. Random sample consensus. Communications of the ACM, 1981.",
        "[4] Arandjelović, R. et al. NetVLAD: CNN architecture for weakly supervised place "
        "recognition. CVPR, 2016.",
        "[5] Oquab, M. et al. DINOv2: Learning robust visual features without supervision. "
        "arXiv:2304.07193, 2023.",
        "[6] DeTone, D.; Malisiewicz, T.; Rabinovich, A. SuperPoint: Self-supervised interest point "
        "detection and description. CVPR Workshops, 2018.",
        "[7] Lindenberger, P.; Sarlin, P.-E.; Pollefeys, M. LightGlue: Local feature matching at "
        "light speed. ICCV, 2023.",
        "[8] Torralba, A.; Fergus, R.; Freeman, W. T. 80 million tiny images. IEEE TPAMI, 2008.",
        "[9] pgvector: vector similarity search for PostgreSQL. github.com/pgvector/pgvector.",
    ]
    for r in refs:
        e.append(Paragraph(r, REF))

    doc.build(e)
    return saida


if __name__ == "__main__":
    print(f"Artigo gerado: {construir()}")
