"""Figuras dos relatórios do piloto (semanas 2 e 3).

Uso:
    uv run python scripts/figuras_piloto.py

Lê as tabelas de data/processed/ (geradas pelos scripts das semanas 2 e 3)
e grava PNGs em docs/piloto/img/. O mapa consulta o catálogo STAC do INPE
para desenhar o contorno dos tiles.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon  # noqa: E402
from pystac_client import Client  # noqa: E402

from satbio import stac  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
WABAD = RAIZ / "data" / "processed" / "wabad"
STAC = RAIZ / "data" / "processed" / "stac"
SAIDA = RAIZ / "docs" / "piloto" / "img"

# Paleta de referência (validada: CVD e contraste; cores abaixo de 3:1 levam rótulo direto).
SUPERFICIE = "#fcfcfb"
TEXTO = "#0b0b0b"
TEXTO_2 = "#52514e"
MUDO = "#a8a7a2"
GRADE = "#e7e6e2"
AZUL, LARANJA, AQUA, AMARELO = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
AZUL_CLARO = "#cde2fb"

SITIOS = ["RBA", "RFP", "RGU", "RME"]
# Posição dos rótulos dos tiles no mapa (lon, lat, alinhamento), escolhida para não cobrir os sítios.
ROTULO_TILE = {"041012": (-36.12, -5.4, "left"), "041013": (-36.08, -7.1, "left"), "042013": (-34.32, -6.88, "right")}

plt.rcParams.update({
    "figure.facecolor": SUPERFICIE, "axes.facecolor": SUPERFICIE, "savefig.facecolor": SUPERFICIE,
    "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "text.color": TEXTO, "axes.labelcolor": TEXTO_2, "xtick.color": TEXTO_2, "ytick.color": TEXTO_2,
    "axes.edgecolor": MUDO, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRADE, "grid.linewidth": 0.8, "axes.axisbelow": True,
})


def _salvar(fig, nome: str) -> None:
    fig.savefig(SAIDA / nome, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  {nome}")


def _status(linha) -> str:
    if linha["valido"]:
        return "válida"
    scl = linha["SCL_origem"]
    if scl in (8, 9, 10):
        return "nuvem"
    if scl == 3:
        return "sombra de nuvem"
    if scl in stac.SCL_VALIDOS and isinstance(linha["motivo_invalido"], str) and "névoa" in linha["motivo_invalido"]:
        return "névoa (B02)"
    return "outro"


def figura_serie(serie: pd.DataFrame, campanhas: pd.DataFrame) -> None:
    """NDVI por composição, com o corte e o período das gravações."""
    fig, eixos = plt.subplots(len(SITIOS), 1, figsize=(9, 9), sharex=True, sharey=True)
    for ax, sitio in zip(eixos, SITIOS):
        s = serie[serie["sitio"] == sitio].sort_values("data_observacao")
        camp = campanhas[campanhas["sitio"] == sitio].iloc[0]
        ax.axvspan(camp["inicio_relogio"], camp["fim_relogio"], color=AZUL_CLARO, lw=0)
        corte = pd.Timestamp(s["corte"].iloc[0])
        ax.axvline(corte, color=TEXTO_2, lw=1.2, ls=(0, (4, 3)))
        validas = s[s["valido"]]
        invalidas = s[~s["valido"] & s["NDVI"].notna()]
        ax.plot(validas["data_observacao"], validas["NDVI"], color=AZUL, lw=2, marker="o", ms=5,
                markeredgecolor=SUPERFICIE, markeredgewidth=1.5, label="composição válida")
        ax.scatter(invalidas["data_observacao"], invalidas["NDVI"], s=36, facecolors="none",
                   edgecolors=MUDO, linewidths=1.5, label="inválida (nuvem, sombra ou névoa)", zorder=3)
        ax.set_title(f"{sitio} · {int(s['valido'].sum())} de {len(s)} composições válidas", fontsize=10)
        ax.set_ylim(0, 1)
        ax.set_ylabel("NDVI")
        ax.text(corte, 0.06, "corte ", color=TEXTO_2, fontsize=8, ha="right")
        ax.text(camp["inicio_relogio"] + (camp["fim_relogio"] - camp["inicio_relogio"]) / 2, 0.06,
                "gravações", color=TEXTO_2, fontsize=8, ha="center")
    alcas, rotulos = eixos[0].get_legend_handles_labels()
    fig.legend(alcas, rotulos, loc="upper left", bbox_to_anchor=(0.01, 0.935), ncol=2, frameon=False, fontsize=9)
    eixos[-1].xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
    eixos[-1].xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
    fig.suptitle("Série Sentinel-2 (S2-16D-2) no pixel de cada sítio, até a véspera das gravações",
                 x=0.01, ha="left", fontsize=12, fontweight="bold", y=1.0)
    fig.text(0.01, 0.955, "Data de cada ponto = dia de origem do pixel (PROVENANCE). Corte = véspera da 1ª gravação; "
             "nada depois dele entra na série.", color=TEXTO_2, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.905))
    _salvar(fig, "semana3-serie-ndvi.png")


def figura_qualidade(serie: pd.DataFrame) -> None:
    """Composições por sítio, separadas pelo motivo de invalidez."""
    serie = serie.assign(status=serie.apply(_status, axis=1))
    categorias = [("válida", AZUL), ("nuvem", LARANJA), ("sombra de nuvem", AQUA), ("névoa (B02)", AMARELO),
                  ("outro", MUDO)]
    contagem = serie.groupby(["sitio", "status"]).size().unstack(fill_value=0).reindex(SITIOS)
    fig, ax = plt.subplots(figsize=(9, 3.4))
    esquerda = pd.Series(0, index=contagem.index)
    for nome, cor in categorias:
        if nome not in contagem:
            continue
        valores = contagem[nome]
        barras = ax.barh(contagem.index, valores, left=esquerda, color=cor, edgecolor=SUPERFICIE, linewidth=2,
                         height=0.6, label=nome)
        for barra, v in zip(barras, valores):
            if v >= 1:
                ax.text(barra.get_x() + barra.get_width() / 2, barra.get_y() + barra.get_height() / 2, str(v),
                        ha="center", va="center", fontsize=9, color="white" if nome == "válida" else TEXTO)
        esquerda += valores
    ax.invert_yaxis()
    ax.set_xlabel("composições de 16 dias na janela de 12 meses")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.02), ncol=5, frameon=False, fontsize=9)
    ax.set_title("Quanto da série sobra depois da máscara de qualidade", pad=28)
    _salvar(fig, "semana3-qualidade.png")


def figura_mapa(serie: pd.DataFrame, pontos: pd.DataFrame) -> None:
    """Sítios sobre o contorno dos tiles do cubo usados."""
    cliente = Client.open(stac.CATALOGO, headers={"User-Agent": stac.USER_AGENT})
    colecao = cliente.get_collection(stac.COLECAO)
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    for tile, item_id in serie.drop_duplicates("tile")[["tile", "item_id"]].itertuples(index=False):
        geom = colecao.get_item(item_id).geometry
        anel = geom["coordinates"][0] if geom["type"] == "Polygon" else geom["coordinates"][0][0]
        ax.add_patch(Polygon(anel, closed=True, facecolor="none", edgecolor=MUDO, lw=1.5))
        x, y, ha = ROTULO_TILE.get(f"{int(tile):06d}", (anel[0][0], anel[0][1], "left"))
        ax.text(x, y, f"tile {int(tile):06d}", color=TEXTO_2, fontsize=9, ha=ha, va="center")
    p = pontos.set_index("sitio").loc[SITIOS]
    ax.scatter(p["longitude"], p["latitude"], s=60, color=AZUL, edgecolor=SUPERFICIE, linewidth=2, zorder=3)
    for sitio, linha in p.iterrows():
        ax.annotate(f"{sitio}  {linha['area_estudo']}", (linha["longitude"], linha["latitude"]),
                    xytext=(8, 0), textcoords="offset points", va="center", fontsize=9)
    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")
    ax.set_aspect("equal")
    ax.set_title("Sítios do WABAD usados no piloto e tiles do S2-16D-2")
    ax.text(0, -0.13, "Coordenada = centro do sítio declarado no Metadata.csv do WABAD. Litoral não desenhado.",
            transform=ax.transAxes, color=TEXTO_2, fontsize=8)
    _salvar(fig, "semana3-mapa-sitios.png")


def figura_esforco(gravacoes: pd.DataFrame, deteccoes: pd.DataFrame) -> None:
    """Quando cada minuto anotado foi gravado, por sítio."""
    g = gravacoes.assign(hora=gravacoes["inicio_relogio"].dt.hour + gravacoes["inicio_relogio"].dt.minute / 60)
    fig, eixos = plt.subplots(1, len(SITIOS), figsize=(10, 3.8), sharey=True, sharex=True)
    for ax, sitio in zip(eixos, SITIOS):
        s = g[g["sitio"] == sitio]
        d = deteccoes[deteccoes["sitio"] == sitio]
        ax.scatter(s["inicio_relogio"], s["hora"], s=28, color=AZUL, edgecolor=SUPERFICIE, linewidth=1)
        ax.set_title(sitio, fontsize=10, pad=18)
        ax.text(0, 1.02, f"{len(s)} min · {d['especie'].nunique()} espécies · {len(d)} anotações",
                transform=ax.transAxes, fontsize=8, color=TEXTO_2)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
        ax.tick_params(axis="x", labelsize=8, rotation=45)
    eixos[0].set_ylim(0, 24)
    eixos[0].set_yticks(range(0, 25, 6))
    eixos[0].set_ylabel("hora do relógio do gravador")
    fig.suptitle("Minutos anotados do WABAD por sítio: quando foram gravados", x=0.01, ha="left",
                 fontsize=12, fontweight="bold")
    fig.text(0.01, 0.905, "Cada ponto é um minuto anotado por especialista. O fuso do relógio não é declarado pela fonte.",
             color=TEXTO_2, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    _salvar(fig, "semana2-esforco-acustico.png")


def figura_fluxo() -> None:
    """Diagrama do fluxo de dados do piloto."""
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.2)
    ax.axis("off")

    def caixa(x, y, titulo, texto, cor=AZUL, largura=2.6, altura=1.05):
        ax.add_patch(FancyBboxPatch((x, y), largura, altura, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=SUPERFICIE, edgecolor=cor, linewidth=1.8))
        ax.text(x + 0.12, y + altura - 0.18, titulo, fontsize=9.5, fontweight="bold", va="top")
        ax.text(x + 0.12, y + altura - 0.45, texto, fontsize=8, color=TEXTO_2, va="top", linespacing=1.4)

    def seta(x0, y0, x1, y1, rotulo=""):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=12, color=TEXTO_2, lw=1.3))
        if rotulo:
            ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 0.08, rotulo, fontsize=7.5, color=TEXTO_2, ha="center")

    caixa(0.1, 2.9, "WABAD (Zenodo)", "áudios, Metadata.csv,\nanotações de especialistas")
    caixa(3.6, 2.9, "Semana 2 · tabelas", "pontos, campanhas, gravações,\ndetecções, QC, manifesto (md5)")
    caixa(7.1, 2.9, "Corte temporal", "véspera da 1ª gravação\nde cada sítio × campanha", cor=LARANJA)
    caixa(0.1, 0.6, "Catálogo STAC do INPE", "S2-16D-2 (cubo de 16 dias)\nS2_L2A-1 (cenas de origem)")
    caixa(3.6, 0.6, "Semana 3 · série", "pixel + janela 3×3 por\ncomposição, 12 meses")
    caixa(7.1, 0.6, "Validade do pixel", "SCL da cena de origem\n+ B02 ≤ 0,10 (decisão D)", cor=LARANJA)
    seta(2.75, 3.42, 3.55, 3.42)
    seta(6.25, 3.42, 7.05, 3.42)
    seta(8.4, 2.85, 5.6, 1.7, "janela de imagens")
    seta(2.75, 1.12, 3.55, 1.12)
    seta(6.25, 1.12, 7.05, 1.12)
    ax.text(0.1, 0.15, "Próximo: tabela analítica por propriedade × campanha (docs/desenho-analitico.md). "
            "Em laranja, regras que protegem contra vazamento e nuvem.", fontsize=8, color=TEXTO_2)
    ax.set_title("Fluxo de dados do piloto", loc="left")
    _salvar(fig, "fluxo-piloto.png")


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    serie = pd.read_csv(STAC / "serie_s2.csv", parse_dates=["data_observacao", "corte"])
    campanhas = pd.read_csv(WABAD / "campanhas.csv", parse_dates=["inicio_relogio", "fim_relogio"])
    pontos = pd.read_csv(WABAD / "pontos.csv")
    gravacoes = pd.read_csv(WABAD / "gravacoes.csv", parse_dates=["inicio_relogio"])
    deteccoes = pd.read_csv(WABAD / "deteccoes.csv")
    print("figuras em docs/piloto/img/:")
    figura_serie(serie, campanhas)
    figura_qualidade(serie)
    figura_mapa(serie, pontos)
    figura_esforco(gravacoes, deteccoes)
    figura_fluxo()


if __name__ == "__main__":
    main()
