"""Nebulosidade do S2-16D-2 no sul da Bahia em 2022 (docs/literatura/nebulosidade-sul-bahia.md).

Uso:
    uv run python scripts/nebulosidade_sul_bahia.py [--permitir-sujo]

Sem coordenadas publicadas de cabrucas, usa os dois centros de paisagem de
Rocha et al. 2019 (Una e Ilhéus, UTM SAD69 24S) e uma grade de 10 pontos a
cada 2 km em volta de cada um (2 linhas × 5 colunas). Os pontos não são
necessariamente cabrucas: medem a nebulosidade regional. Para cada ponto lê
as composições de 2022 e conta o pixel central válido por duas regras: a
usada no teste original (SCL do cubo + B02 <= 0,10) e a regra principal da
decisão D (SCL da cena de origem). Grava em data/processed/nebulosidade/
(fora do git) a tabela por ponto × composição, o resumo e um manifesto.
Precisa de internet; leva cerca de 15 a 30 minutos.
"""

from __future__ import annotations

import argparse
import json
import platform
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from importlib.metadata import version
from pathlib import Path

import pandas as pd
from pystac_client import Client
from rasterio.warp import transform

from satbio import acustica, rastreio, stac

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "data" / "processed" / "nebulosidade"
ANO = 2022
# Centros de paisagem publicados por Rocha et al. 2019 (DOI 10.1002/ece3.5021), UTM SAD69 zona 24S.
CENTROS = {"Una": (484973, 8325906), "Ilhéus": (473698, 8373196)}
CRS_CENTROS = "EPSG:29194"
PASSO_M = 2000
DESLOCAMENTOS = [(dx * PASSO_M, dy * PASSO_M) for dy in (-0.5, 0.5) for dx in (-2, -1, 0, 1, 2)]
REGRAS = {"valido_scl_cubo_b02": "SCL do cubo + B02 (regra do teste original)",
          "valido": "SCL da cena de origem + B02 (decisão D)"}


def pontos() -> pd.DataFrame:
    linhas = []
    for paisagem, (x0, y0) in CENTROS.items():
        xs = [x0 + dx for dx, _ in DESLOCAMENTOS]
        ys = [y0 + dy for _, dy in DESLOCAMENTOS]
        lons, lats = transform(CRS_CENTROS, "EPSG:4326", xs, ys)
        for i, (lon, lat) in enumerate(zip(lons, lats)):
            linhas.append({"ponto": f"{paisagem}-{i:02d}", "paisagem": paisagem, "longitude": lon, "latitude": lat})
    return pd.DataFrame(linhas)


def serie_do_ponto(p: dict) -> list[dict]:
    inicio, fim = date(ANO, 1, 1), date(ANO, 12, 31)
    itens = stac.buscar_itens(p["longitude"], p["latitude"], inicio, fim)
    verificador = stac.VerificadorOrigem()
    linhas = []
    for item, posicao in stac.um_item_por_periodo(itens, p["longitude"], p["latitude"]):
        linha = stac.linha_da_composicao(item, p["longitude"], p["latitude"], posicao, verificador=verificador)
        linhas.append({"ponto": p["ponto"], "paisagem": p["paisagem"], **linha})
    print(f"{p['ponto']}: {len(linhas)} composições, {sum(l['valido_scl_cubo_b02'] for l in linhas)} válidas "
          f"(SCL do cubo), {sum(l['valido'] for l in linhas)} (cena de origem)", flush=True)
    return linhas


def cobertura(grupo: pd.DataFrame, regra: str) -> pd.Series:
    """Regra de cobertura do desenho (seção 6), aplicada ao pixel central: >= 10 válidas e >= 1 por trimestre."""
    validas = grupo[grupo[regra]]
    trimestres = pd.to_datetime(validas["data_observacao"]).dt.quarter.nunique()
    return pd.Series({"validas": len(validas), "trimestres_com_valida": trimestres,
                      "passa_cobertura": len(validas) >= 10 and trimestres == 4})


def main(permitir_sujo: bool) -> None:
    codigo = rastreio.estado_do_codigo(RAIZ, SAIDA, permitir_sujo)
    acesso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    tabela_pontos = pontos()
    with ThreadPoolExecutor(max_workers=4) as ex:
        partes = list(ex.map(serie_do_ponto, tabela_pontos.to_dict("records")))
    serie = pd.DataFrame([l for parte in partes for l in parte])
    serie["trimestre"] = pd.to_datetime(serie["inicio_composicao"]).dt.quarter

    resumo = []
    for regra, descricao in REGRAS.items():
        por_ponto = serie.groupby(["paisagem", "ponto"]).apply(cobertura, regra=regra).reset_index()
        for paisagem, g in por_ponto.groupby("paisagem"):
            resumo.append({"regra": descricao, "recorte": paisagem,
                           "fracao_validas": serie.loc[serie["paisagem"] == paisagem, regra].mean(),
                           "validas_mediana": g["validas"].median(), "validas_min": g["validas"].min(),
                           "validas_max": g["validas"].max(),
                           "pontos_passam": f"{int(g['passa_cobertura'].sum())} de {len(g)}"})
        resumo.append({"regra": descricao, "recorte": "todos", "fracao_validas": serie[regra].mean(),
                       "validas_mediana": por_ponto["validas"].median(), "validas_min": por_ponto["validas"].min(),
                       "validas_max": por_ponto["validas"].max(),
                       "pontos_passam": f"{int(por_ponto['passa_cobertura'].sum())} de {len(por_ponto)}"})
        for t, g in serie.groupby("trimestre"):
            resumo.append({"regra": descricao, "recorte": f"trimestre {t}", "fracao_validas": g[regra].mean()})
    resumo = pd.DataFrame(resumo)

    SAIDA.mkdir(parents=True, exist_ok=True)
    serie.to_csv(SAIDA / "serie_pontos.csv", index=False)
    resumo.to_csv(SAIDA / "resumo.csv", index=False)
    cliente = Client.open(stac.CATALOGO, headers={"User-Agent": stac.USER_AGENT})
    colecao = cliente.get_collection(stac.COLECAO)
    manifesto = {
        "catalogo": stac.CATALOGO,
        "colecao": stac.COLECAO,
        "colecao_versao": colecao.extra_fields.get("version"),
        "colecao_origem": stac.COLECAO_ORIGEM,
        "colecao_origem_versao": cliente.get_collection(stac.COLECAO_ORIGEM).extra_fields.get("version"),
        "licenca": [l.href for l in colecao.links if l.rel == "license"],
        "acesso_utc": acesso,
        "codigo": codigo,
        "ambiente": {"python": platform.python_version(), "pystac-client": version("pystac-client"),
                     "rasterio": version("rasterio"), "dependencias": "uv.lock"},
        "ano": ANO,
        "centros": {"fonte": "Rocha et al. 2019, DOI 10.1002/ece3.5021", "crs": CRS_CENTROS, "pontos": CENTROS},
        "grade": {"passo_m": PASSO_M, "deslocamentos_m": DESLOCAMENTOS},
        "pontos": tabela_pontos.to_dict("records"),
        "regras": REGRAS,
        "scl_validos": sorted(stac.SCL_VALIDOS),
        "b02_max_nevoa": stac.B02_MAX,
        "regra_cobertura": ">= 10 composições válidas e >= 1 por trimestre (data de observação), pixel central",
        "itens": sorted(serie["item_id"].unique()),
        "cenas_origem": sorted(serie["cena_origem"].dropna().unique()),
        "saida_sha256": {f: acustica.sha256(SAIDA / f) for f in ["serie_pontos.csv", "resumo.csv"]},
    }
    (SAIDA / "manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2, default=str))
    print("\n" + resumo.round(3).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--permitir-sujo", action="store_true", help="roda com código não commitado e salva o diff")
    main(parser.parse_args().permitir_sujo)
