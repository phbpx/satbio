"""Séries do cubo Sentinel-2 do Brazil Data Cube (S2-16D-2) em pontos.

Cada item do cubo é uma composição de 16 dias ("Least CC First"): cada pixel
vem da observação menos nublada do período, e a banda PROVENANCE diz de que
dia do ano ela veio. Para não usar informação posterior às gravações, só
entram composições que terminam até o corte (véspera da primeira gravação do
sítio × campanha; PRD, seção 6.3).

B8A e B11 têm resolução nativa de 20 m e são distribuídas reamostradas para
10 m; o pixel de 10 m não tem detalhe próprio nessas bandas. O NDVI do cubo
é calculado com B8A, não B08 — (B8A − B04) / (B8A + B04), conferido nos
dados —, então também carrega a resolução de 20 m no NIR.
"""

from __future__ import annotations

import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Callable

import numpy as np
import pystac
import rasterio
from pystac_client import Client
from rasterio.warp import transform
from rasterio.windows import Window

CATALOGO = "https://data.inpe.br/bdc/stac/v1"
COLECAO = "S2-16D-2"
# Cenas Sentinel-2 L2A individuais, de onde vêm os pixels do cubo (PRD 6.3, decisão D).
COLECAO_ORIGEM = "S2_L2A-1"
USER_AGENT = "satbio/0.1 (+https://github.com/phbpx/satbio)"

BANDAS_ESPECTRAIS = ["B02", "B04", "B08", "B8A", "B11"]
INDICES = ["NDVI", "EVI"]
BANDAS_QUALIDADE = ["SCL", "CLEAROB", "TOTALOB", "PROVENANCE"]
BANDAS_LIDAS = BANDAS_ESPECTRAIS + INDICES + BANDAS_QUALIDADE

# Classes da Scene Classification Layer (Sentinel-2 L2A).
SCL_NOMES = {
    0: "sem dado", 1: "saturado ou defeituoso", 2: "área escura", 3: "sombra de nuvem",
    4: "vegetação", 5: "solo exposto", 6: "água", 7: "não classificado",
    8: "nuvem (prob. média)", 9: "nuvem (prob. alta)", 10: "cirrus", 11: "neve ou gelo",
}
SCL_VALIDOS = frozenset({4, 5, 6})
# Teste de névoa: o SCL classifica névoa fina como solo exposto. Vegetação limpa
# nestes dados tem B02 <= 0,075 em 95% dos pixels; 0,10 é limiar físico usual.
# Fixado em 2026-10-03, depois de ver os dois casos do piloto (docs/piloto/semana-3.md).
B02_MAX = 0.10
RAIO_JANELA_PX = 1  # janela 3×3 em volta do pixel do ponto

GDAL_ENV = {
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "GDAL_HTTP_MAX_RETRY": "4",
    "GDAL_HTTP_RETRY_DELAY": "5",
    "GDAL_HTTP_USERAGENT": USER_AGENT,
}


@dataclass(frozen=True)
class Posicao:
    """Onde o ponto cai num raster do cubo.

    `x`, `y` são o ponto no CRS do cubo; `x_centro`, `y_centro` o centro do
    pixel que o contém; `res` o tamanho do pixel. Com eles se calcula o centro
    de cada pixel da janela, usado para conferir a cena de origem.
    """
    x: float
    y: float
    linha: int
    coluna: int
    dist_borda_px: int
    crs: str = ""
    x_centro: float = 0.0
    y_centro: float = 0.0
    res: float = 10.0

    def centros_da_janela(self, raio_px: int = RAIO_JANELA_PX) -> list[list[tuple[float, float]]]:
        """Centros (x, y), no CRS do cubo, dos pixels da janela, linha a linha."""
        return [[(self.x_centro + j * self.res, self.y_centro - i * self.res) for j in range(-raio_px, raio_px + 1)]
                for i in range(-raio_px, raio_px + 1)]


Leitor = Callable[[str, float, float], np.ndarray]
Localizador = Callable[[str, float, float], Posicao]
# (datas por pixel, posição, lon, lat, B04 do cubo por pixel) -> conferência com as cenas de origem
Verificador = Callable[[np.ndarray, Posicao, float, float, np.ndarray], "ResultadoOrigem"]


def janela(inicio_campanha: datetime, dias: int = 365) -> tuple[date, date]:
    """Devolve (início, corte) da série de imagens de um sítio × campanha.

    O corte é a véspera da primeira gravação: absorve o fuso desconhecido do
    relógio dos gravadores. O início fica `dias` antes do corte; como só
    entram composições inteiras, a série cobre um pouco menos que `dias`.
    """
    corte = inicio_campanha.date() - timedelta(days=1)
    return corte - timedelta(days=dias), corte


def antes_do_corte(fim_composicao: datetime, corte: date) -> bool:
    """A composição só entra se o período inteiro terminar até o corte.

    O `end_datetime` do BDC marca o fim do período de 16 dias; tratá-lo como
    inclusivo é o lado conservador.
    """
    return fim_composicao.date() <= corte


def periodo(item: pystac.Item) -> tuple[datetime, datetime]:
    props = item.properties
    return (datetime.fromisoformat(props["start_datetime"].replace("Z", "+00:00")),
            datetime.fromisoformat(props["end_datetime"].replace("Z", "+00:00")))


def filtrar_janela(itens: list[pystac.Item], inicio: date, corte: date) -> list[pystac.Item]:
    """Mantém só composições inteiramente dentro de [início, corte], em ordem de data."""
    dentro = [it for it in itens if periodo(it)[0].date() >= inicio and antes_do_corte(periodo(it)[1], corte)]
    return sorted(dentro, key=lambda it: periodo(it)[0])


def buscar_itens(lon: float, lat: float, inicio: date, corte: date, catalogo: str = CATALOGO) -> list[pystac.Item]:
    """Itens do S2-16D-2 sobre o ponto, inteiramente dentro de [início, corte].

    Perto da borda entre tiles pode haver mais de um item por período; use
    `um_item_por_periodo` antes de extrair.
    """
    cliente = Client.open(catalogo, headers={"User-Agent": USER_AGENT})
    busca = cliente.search(collections=[COLECAO], intersects={"type": "Point", "coordinates": [lon, lat]},
                           datetime=f"{inicio.isoformat()}/{corte.isoformat()}")
    return filtrar_janela(list(busca.items()), inicio, corte)


def localizar(href: str, lon: float, lat: float) -> Posicao:
    """Posição do ponto no raster. Levanta ValueError se o ponto estiver fora dele."""
    with rasterio.Env(**GDAL_ENV), rasterio.open(href) as ds:
        xs, ys = transform("EPSG:4326", ds.crs, [lon], [lat])
        linha, coluna = ds.index(xs[0], ys[0])
        if not (0 <= linha < ds.height and 0 <= coluna < ds.width):
            raise ValueError(f"ponto ({lon}, {lat}) fora do raster {href}")
        dist = min(linha, coluna, ds.height - 1 - linha, ds.width - 1 - coluna)
        xc, yc = ds.xy(linha, coluna)
        return Posicao(x=xs[0], y=ys[0], linha=linha, coluna=coluna, dist_borda_px=dist,
                       crs=ds.crs.to_string(), x_centro=xc, y_centro=yc, res=ds.res[0])


def um_item_por_periodo(itens: list[pystac.Item], lon: float, lat: float,
                        localizador: Localizador = localizar) -> list[tuple[pystac.Item, Posicao | None]]:
    """Escolhe um item por período de composição.

    Entre itens do mesmo período (tiles vizinhos), fica o que contém o ponto
    mais longe da borda. Se nenhum contiver o ponto, o período fica com o
    primeiro item e posição None, para virar linha inválida em vez de sumir.
    """
    por_periodo: dict[datetime, list[pystac.Item]] = defaultdict(list)
    for item in itens:
        por_periodo[periodo(item)[0]].append(item)

    escolhidos = []
    for inicio in sorted(por_periodo):
        candidatos = []
        for item in por_periodo[inicio]:
            try:
                candidatos.append((item, localizador(item.assets["SCL"].href, lon, lat)))
            except ValueError:
                continue
        if candidatos:
            escolhidos.append(max(candidatos, key=lambda c: c[1].dist_borda_px))
        else:
            escolhidos.append((por_periodo[inicio][0], None))
    return escolhidos


def meta_banda(item: pystac.Item, banda: str) -> dict:
    """nodata e escala da banda, lidos do próprio item (extensão eo:bands do BDC).

    Falha em vez de presumir: sem nodata, um zero de preenchimento viraria
    valor válido; sem escala, reflectâncias sairiam em número digital.
    """
    eo = item.assets[banda].extra_fields.get("eo:bands", [{}])[0]
    if eo.get("nodata") is None:
        raise ValueError(f"{item.id}/{banda}: metadado sem nodata")
    if banda not in BANDAS_QUALIDADE and eo.get("scale") is None:
        raise ValueError(f"{item.id}/{banda}: metadado sem escala")
    return {"nodata": eo["nodata"], "escala": eo.get("scale") or 1.0}


def ler_janela(href: str, lon: float, lat: float, raio_px: int = RAIO_JANELA_PX) -> np.ndarray:
    """Valores brutos da janela (2·raio+1)² centrada no pixel do ponto.

    Lê só os blocos necessários do COG. Fora do raster, a janela é preenchida
    com o nodata da banda, para que esses pixels saiam inválidos.
    """
    with rasterio.Env(**GDAL_ENV), rasterio.open(href) as ds:
        xs, ys = transform("EPSG:4326", ds.crs, [lon], [lat])
        linha, coluna = ds.index(xs[0], ys[0])
        if not (0 <= linha < ds.height and 0 <= coluna < ds.width):
            raise ValueError(f"ponto ({lon}, {lat}) fora do raster {href}")
        lado = 2 * raio_px + 1
        janela_px = Window(coluna - raio_px, linha - raio_px, lado, lado)
        return ds.read(1, window=janela_px, boundless=True, fill_value=ds.nodata)


def ler_pixel(href: str, lon: float, lat: float) -> float | int:
    """Valor bruto do pixel que contém o ponto."""
    return ler_janela(href, lon, lat, raio_px=0)[0, 0].item()


def data_da_observacao(inicio_composicao: date, dia_do_ano: int) -> date:
    """Converte o dia do ano da PROVENANCE em data, considerando a virada do ano."""
    data = date(inicio_composicao.year, 1, 1) + timedelta(days=dia_do_ano - 1)
    if data < inicio_composicao:
        data = date(inicio_composicao.year + 1, 1, 1) + timedelta(days=dia_do_ano - 1)
    return data


@dataclass
class ResultadoOrigem:
    """Conferência de cada pixel da janela contra as cenas de origem (arrays do tamanho da janela).

    `scl`: SCL da cena escolhida (NaN se nenhuma). `cena`: id da cena escolhida.
    `n_cenas`: cenas do dia que cobrem o ponto. `n_com_dado`: cenas com dado
    no pixel. `conflito`: as cenas com dado discordam sobre a validade do SCL.
    `dif_b04`: |B04 da cena escolhida − B04 do cubo| (reflectância), que mede
    se a cena reproduz o cubo.
    """
    scl: np.ndarray
    cena: np.ndarray
    n_cenas: np.ndarray
    n_com_dado: np.ndarray
    conflito: np.ndarray
    dif_b04: np.ndarray

    @classmethod
    def vazio(cls, forma: tuple[int, int]) -> "ResultadoOrigem":
        return cls(scl=np.full(forma, np.nan), cena=np.full(forma, None, dtype=object),
                   n_cenas=np.zeros(forma, dtype=int), n_com_dado=np.zeros(forma, dtype=int),
                   conflito=np.zeros(forma, dtype=bool), dif_b04=np.full(forma, np.nan))


# A cena de origem "reproduz o cubo" se a B04 diferir até isto (reflectância).
TOLERANCIA_B04 = 0.01


def offset_reflectancia(cena_id: str) -> float:
    """Offset somado às reflectâncias L2A a partir da baseline 04.00 (BOA_ADD_OFFSET = -1000).

    O metadado do S2_L2A-1 não declara o offset; ele foi conferido nos dados:
    descontado, B04 das cenas N0301 e N0400 reproduz o cubo (docs/piloto/semana-3.md).
    """
    m = re.search(r"_N(\d{4})_", cena_id)
    return 1000.0 if m and int(m.group(1)) >= 400 else 0.0


class VerificadorOrigem:
    """SCL da cena Sentinel-2 L2A de origem para cada pixel da janela.

    Para cada data de PROVENANCE presente na janela, busca as cenas daquele
    dia que cobrem o ponto e lê, no centro de cada pixel do cubo, o SCL e a
    B04 de todas elas. Quando há mais de uma cena com dado (tiles sobrepostos,
    datastrips, reprocessamentos), fica a que melhor reproduz a B04 do cubo.
    Se as candidatas discordarem sobre a validade e nenhuma reproduzir o cubo
    (diferença > TOLERANCIA_B04), o pixel é marcado em `conflito` e sai
    inválido. As buscas ficam em cache por (ponto, dia); vizinhos fora das
    cenas que cobrem o ponto ficam sem dado (lado conservador).
    """

    def __init__(self, catalogo: str = CATALOGO):
        self._cliente = Client.open(catalogo, headers={"User-Agent": USER_AGENT})
        self._cenas: dict[tuple[float, float, date], list[pystac.Item]] = {}

    def cenas_do_dia(self, lon: float, lat: float, dia: date) -> list[pystac.Item]:
        chave = (lon, lat, dia)
        if chave not in self._cenas:
            busca = self._cliente.search(collections=[COLECAO_ORIGEM],
                                         intersects={"type": "Point", "coordinates": [lon, lat]},
                                         datetime=f"{dia.isoformat()}T00:00:00Z/{dia.isoformat()}T23:59:59Z")
            self._cenas[chave] = sorted(busca.items(), key=lambda it: it.id)
        return self._cenas[chave]

    def cenas_consultadas(self) -> dict[str, dict]:
        """Metadados de todas as cenas buscadas, para o manifesto."""
        saida = {}
        for itens in self._cenas.values():
            for it in itens:
                m = re.search(r"_N(\d{4})_", it.id)
                saida[it.id] = {"baseline": m.group(1) if m else None, "aquisicao": it.properties.get("datetime"),
                                "criado": it.properties.get("created"), "atualizado": it.properties.get("updated")}
        return dict(sorted(saida.items()))

    @staticmethod
    def _amostrar(href: str, crs_origem: str, xs: list[float], ys: list[float]) -> list[float]:
        """Valor em cada ponto; NaN fora do raster ou onde o valor é 0 ou o nodata do arquivo."""
        with rasterio.Env(**GDAL_ENV), rasterio.open(href) as ds:
            tx, ty = transform(crs_origem, ds.crs, xs, ys)
            saida = []
            for x, y in zip(tx, ty):
                linha, coluna = ds.index(x, y)
                if not (0 <= linha < ds.height and 0 <= coluna < ds.width):
                    saida.append(np.nan)
                    continue
                valor = ds.read(1, window=Window(coluna, linha, 1, 1))[0, 0].item()
                saida.append(np.nan if valor == 0 or (ds.nodata is not None and valor == ds.nodata) else float(valor))
            return saida

    def __call__(self, datas: np.ndarray, posicao: Posicao, lon: float, lat: float,
                 b04_cubo: np.ndarray) -> ResultadoOrigem:
        centros = posicao.centros_da_janela((datas.shape[0] - 1) // 2)
        res = ResultadoOrigem.vazio(datas.shape)
        for dia in {d for d in datas.ravel() if d is not None}:
            pixels = list(zip(*np.nonzero(datas == dia)))
            cenas = self.cenas_do_dia(lon, lat, dia)
            xs = [centros[i][j][0] for i, j in pixels]
            ys = [centros[i][j][1] for i, j in pixels]
            leituras = []  # por cena: (id, scl por pixel, b04 por pixel)
            for item in cenas:
                scl = self._amostrar(item.assets["SCL"].href, posicao.crs, xs, ys)
                b04 = self._amostrar(item.assets["B04"].href, posicao.crs, xs, ys)
                offset = offset_reflectancia(item.id)
                leituras.append((item.id, scl, [(v - offset) * 0.0001 for v in b04]))
            for k, (i, j) in enumerate(pixels):
                res.n_cenas[i, j] = len(cenas)
                candidatas = [(cid, scl[k], b04[k]) for cid, scl, b04 in leituras if not np.isnan(scl[k])]
                res.n_com_dado[i, j] = len(candidatas)
                if not candidatas:
                    continue
                difs = [abs(b04 - b04_cubo[i, j]) if np.isfinite(b04) and np.isfinite(b04_cubo[i, j]) else np.inf
                        for _, _, b04 in candidatas]
                melhor = int(np.argmin(difs))
                validades = {scl in SCL_VALIDOS for _, scl, _ in candidatas}
                res.conflito[i, j] = len(validades) > 1 and difs[melhor] > TOLERANCIA_B04
                cid, scl, _ = candidatas[melhor]
                res.scl[i, j] = scl
                res.cena[i, j] = cid
                res.dif_b04[i, j] = difs[melhor]
        return res


_VERIFICADOR_PADRAO: VerificadorOrigem | None = None


def _verificador_padrao() -> VerificadorOrigem:
    global _VERIFICADOR_PADRAO
    if _VERIFICADOR_PADRAO is None:
        _VERIFICADOR_PADRAO = VerificadorOrigem()
    return _VERIFICADOR_PADRAO


def _fisico(bruto: np.ndarray, meta: dict, banda: str) -> np.ndarray:
    """Converte para escala física, com NaN onde o valor é nodata."""
    arr = bruto.astype("float64")
    nodata = meta["nodata"]
    sem_dado = np.isnan(arr) if isinstance(nodata, float) and np.isnan(nodata) else arr == nodata
    if banda not in BANDAS_QUALIDADE:
        arr = arr * meta["escala"]
    return np.where(sem_dado, np.nan, arr)


def _validade(v: dict[str, np.ndarray], inicio: date, fim: date) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Testes de qualidade pixel a pixel e a data de origem de cada pixel."""
    datas = np.array([[data_da_observacao(inicio, int(d)) if np.isfinite(d) else None for d in linha]
                      for linha in v["PROVENANCE"]], dtype=object)
    no_periodo = np.vectorize(lambda d: d is not None and inicio <= d <= fim, otypes=[bool])(datas)
    testes = {
        "scl_cubo": np.isin(v["SCL"], list(SCL_VALIDOS)),
        "bandas": np.all([np.isfinite(v[b]) for b in BANDAS_ESPECTRAIS + INDICES], axis=0),
        "provenance": no_periodo,
        "nevoa": np.nan_to_num(v["B02"], nan=np.inf) <= B02_MAX,
    }
    return testes, datas


def _num(x) -> float | int | None:
    return None if x is None or not np.isfinite(x) else x.item() if hasattr(x, "item") else x


def _motivo_scl(scl, rotulo: str) -> str:
    if scl is None:
        return f"{rotulo} sem dado"
    return f"{rotulo} {scl} ({SCL_NOMES.get(scl, 'desconhecida')})"


def linha_da_composicao(item: pystac.Item, lon: float, lat: float, posicao: Posicao | None,
                        leitor: Leitor = ler_janela, verificador: Verificador | None = None,
                        paralelo: int = 8) -> dict:
    """Uma linha da série: o pixel do ponto e a janela 3×3 em volta, com qualidade.

    Reflectâncias e índices saem na escala física; nodata vira None. Regra
    principal (PRD 6.3, decisão D): o pixel é válido se o SCL da cena
    Sentinel-2 de origem for 4, 5 ou 6, se nenhuma banda estiver sem dado, se
    a PROVENANCE cair no período e se B02 <= B02_MAX. Pixels inválidos não são
    descartados: ficam com o motivo em `motivo_invalido`.

    Variantes para análise de sensibilidade, com o SCL do cubo no lugar do
    da cena de origem: `valido_scl_cubo_b02` (regra anterior) e
    `valido_somente_scl_cubo` (sem o teste de névoa). As colunas `viz_*`
    resumem os pixels da janela válidos pela regra principal.
    `posicao` None significa que o ponto não está em nenhum raster do período.
    """
    ini, fim = periodo(item)
    linha: dict = {
        "item_id": item.id,
        "item_atualizado": item.properties.get("updated"),
        "tile": ",".join(item.properties.get("bdc:tiles", [])),
        "inicio_composicao": ini.date(),
        "fim_composicao": fim.date(),
        "nuvem_item_pct": item.properties.get("eo:cloud_cover"),
        "x_cubo": posicao.x if posicao else None,
        "y_cubo": posicao.y if posicao else None,
        "pixel_linha": posicao.linha if posicao else None,
        "pixel_coluna": posicao.coluna if posicao else None,
    }
    if posicao is None:
        linha.update({b: None for b in BANDAS_LIDAS + ["NDMI", "SCL_origem", "dif_b04_origem"]})
        linha.update({"data_observacao": None, "cena_origem": None, "n_cenas_origem": 0,
                      "conflito_scl_origem": False, "cenas_origem_janela": None, "valido": False,
                      "valido_scl_cubo_b02": False, "valido_somente_scl_cubo": False,
                      "motivo_invalido": "ponto fora do raster", "viz_n_pixels": 0, "viz_n_validos": 0})
        return linha

    with ThreadPoolExecutor(max_workers=paralelo) as ex:
        brutos = dict(zip(BANDAS_LIDAS, ex.map(lambda b: leitor(item.assets[b].href, lon, lat), BANDAS_LIDAS)))
    v = {b: _fisico(np.asarray(brutos[b]), meta_banda(item, b), b) for b in BANDAS_LIDAS}
    with np.errstate(divide="ignore", invalid="ignore"):
        v["NDMI"] = (v["B8A"] - v["B11"]) / (v["B8A"] + v["B11"])

    testes, datas = _validade(v, ini.date(), fim.date())
    origem = (verificador or _verificador_padrao())(datas, posicao, lon, lat, v["B04"])
    testes["scl_origem"] = np.isin(origem.scl, list(SCL_VALIDOS)) & ~origem.conflito

    comuns = testes["bandas"] & testes["provenance"]
    valido_px = testes["scl_origem"] & testes["nevoa"] & comuns
    c = v["SCL"].shape[0] // 2

    for banda in BANDAS_LIDAS + ["NDMI"]:
        valor = _num(v[banda][c, c])
        linha[banda] = int(valor) if valor is not None and banda in BANDAS_QUALIDADE else valor
    scl_o = _num(origem.scl[c, c])
    linha["SCL_origem"] = int(scl_o) if scl_o is not None else None
    linha["cena_origem"] = origem.cena[c, c]
    linha["n_cenas_origem"] = int(origem.n_cenas[c, c])
    linha["conflito_scl_origem"] = bool(origem.conflito[c, c])
    linha["dif_b04_origem"] = _num(origem.dif_b04[c, c])
    linha["cenas_origem_janela"] = ";".join(sorted({x for x in origem.cena.ravel() if x})) or None
    linha["data_observacao"] = datas[c, c]

    motivos = []
    if datas[c, c] is not None and not testes["scl_origem"][c, c]:
        if origem.n_cenas[c, c] == 0:
            motivos.append("sem cena de origem no dia")
        elif origem.n_com_dado[c, c] == 0:
            motivos.append("cena de origem sem dado no pixel")
        elif origem.conflito[c, c]:
            motivos.append("cenas de origem em conflito e nenhuma reproduz o cubo")
        else:
            motivos.append(_motivo_scl(linha["SCL_origem"], "SCL origem"))
    if not testes["bandas"][c, c]:
        motivos.append("banda sem dado")
    if not testes["provenance"][c, c]:
        motivos.append("PROVENANCE sem dado" if datas[c, c] is None else f"PROVENANCE fora do período ({datas[c, c]})")
    if testes["bandas"][c, c] and not testes["nevoa"][c, c]:
        motivos.append(f"névoa (B02 {linha['B02']:.3f} > {B02_MAX})")
    linha["valido"] = not motivos
    linha["motivo_invalido"] = "; ".join(motivos) or None
    linha["valido_scl_cubo_b02"] = bool(testes["scl_cubo"][c, c] and testes["nevoa"][c, c] and comuns[c, c])
    linha["valido_somente_scl_cubo"] = bool(testes["scl_cubo"][c, c] and comuns[c, c])

    linha["viz_n_pixels"] = int(valido_px.size)
    linha["viz_n_validos"] = int(valido_px.sum())
    for indice in ["NDVI", "EVI", "NDMI"]:
        valores = v[indice][valido_px]
        linha[f"viz_{indice}_mediana"] = float(np.median(valores)) if valores.size else None
        linha[f"viz_{indice}_dp"] = float(np.std(valores)) if valores.size >= 2 else None
    return linha
