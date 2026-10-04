"""Nebulosidade do Sentinel-2 L2A em Canandé (REASSEMBLY), via Earth Search (docs/literatura/viabilidade-reassembly.md).

Uso:
    uv run python scripts/nebulosidade_reassembly.py [--permitir-sujo]

O Brazil Data Cube não cobre o Equador. Usa o catálogo aberto Earth Search
(Element 84, coleção sentinel-2-l2a, COGs públicos na AWS) e 9 pontos numa
grade 3×3 sobre a área das parcelas (lat 0,46–0,56; lon −79,24 a −79,14), no
ano anterior às gravações de 2021 (2020-10-01 a 2021-09-30). Conta, por
ponto e data, as observações com SCL 4, 5 ou 6 (a mesma classe aceita na
decisão D, sem o teste de névoa) e quantos períodos de 16 dias têm alguma
observação válida. Grava em data/processed/reassembly_nuvem/ (fora do git)
a tabela por cena × ponto, o resumo e um manifesto. Precisa de internet.
"""

from __future__ import annotations

import argparse
import json
import platform
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from pystac_client import Client
from rasterio.warp import transform

from satbio import acustica, rastreio, stac

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "data" / "processed" / "reassembly_nuvem"
CATALOGO = "https://earth-search.aws.element84.com/v1"
COLECAO = "sentinel-2-l2a"
INICIO, FIM = date(2020, 10, 1), date(2021, 9, 30)
LATS = [0.46, 0.51, 0.56]
LONS = [-79.24, -79.19, -79.14]
DIAS_PERIODO = 16
GDAL_ENV = {**stac.GDAL_ENV, "AWS_NO_SIGN_REQUEST": "YES"}


def ler_scl(item) -> list[dict]:
    """SCL de cada ponto numa cena (NaN fora do raster ou sem dado)."""
    href = item.assets["scl"].href
    with rasterio.Env(**GDAL_ENV), rasterio.open(href) as ds:
        lons = [lon for lat in LATS for lon in LONS]
        lats = [lat for lat in LATS for _ in LONS]
        xs, ys = transform("EPSG:4326", ds.crs, lons, lats)
        valores = [v[0] for v in ds.sample(zip(xs, ys), masked=True)]
    return [{"item_id": item.id, "data": item.datetime.date(), "nuvem_cena_pct": item.properties.get("eo:cloud_cover"),
             "ponto": f"P{i}", "longitude": lon, "latitude": lat,
             "scl": None if np.ma.is_masked(v) or int(v) == 0 else int(v)}
            for i, (lon, lat, v) in enumerate(zip(lons, lats, valores))]


def main(permitir_sujo: bool) -> None:
    codigo = rastreio.estado_do_codigo(RAIZ, SAIDA, permitir_sujo)
    acesso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    cliente = Client.open(CATALOGO, headers={"User-Agent": stac.USER_AGENT})
    area = {"type": "Polygon", "coordinates": [[[min(LONS), min(LATS)], [max(LONS), min(LATS)],
                                                 [max(LONS), max(LATS)], [min(LONS), max(LATS)],
                                                 [min(LONS), min(LATS)]]]}
    itens = list(cliente.search(collections=[COLECAO], intersects=area,
                                datetime=f"{INICIO.isoformat()}/{FIM.isoformat()}T23:59:59Z").items())
    print(f"{len(itens)} cenas de {INICIO} a {FIM}", flush=True)
    with ThreadPoolExecutor(max_workers=8) as ex:
        linhas = [l for parte in ex.map(ler_scl, itens) for l in parte]
    cenas = pd.DataFrame(linhas)
    cenas["valida"] = cenas["scl"].isin(list(stac.SCL_VALIDOS))
    # Uma observação por ponto e data: tiles vizinhos e reprocessamentos repetem a mesma passagem.
    obs = (cenas.dropna(subset=["scl"]).groupby(["ponto", "data"], as_index=False)
           .agg(valida=("valida", "any"), nuvem_cena_pct=("nuvem_cena_pct", "median")))
    obs["periodo16"] = (pd.to_datetime(obs["data"]) - pd.Timestamp(INICIO)).dt.days // DIAS_PERIODO
    obs["mes"] = pd.to_datetime(obs["data"]).dt.to_period("M").astype(str)
    n_periodos = ((FIM - INICIO).days + 1) // DIAS_PERIODO

    por_ponto = obs.groupby("ponto").agg(observacoes=("valida", "size"), limpas=("valida", "sum"),
                                         periodos_com_limpa=("periodo16", lambda s: 0))
    por_ponto["periodos_com_limpa"] = obs[obs["valida"]].groupby("ponto")["periodo16"].nunique()
    por_ponto = por_ponto.fillna(0)
    por_mes = obs.groupby("mes")["valida"].sum()
    resumo = {
        "cenas": len(itens),
        "nuvem_mediana_cena_pct": float(pd.Series([i.properties.get("eo:cloud_cover") for i in itens]).median()),
        "fracao_observacoes_limpas": float(obs["valida"].mean()),
        "limpas_por_ponto_mediana": float(por_ponto["limpas"].median()),
        "limpas_por_ponto_min": int(por_ponto["limpas"].min()),
        "limpas_por_ponto_max": int(por_ponto["limpas"].max()),
        "periodos_16d_total": n_periodos,
        "periodos_com_limpa_mediana": float(por_ponto["periodos_com_limpa"].median()),
        "periodos_com_limpa_min": int(por_ponto["periodos_com_limpa"].min()),
        "periodos_com_limpa_max": int(por_ponto["periodos_com_limpa"].max()),
        "meses_sem_observacao_limpa": sorted(por_mes[por_mes == 0].index.tolist()),
    }

    SAIDA.mkdir(parents=True, exist_ok=True)
    cenas.to_csv(SAIDA / "cenas_pontos.csv", index=False)
    por_ponto.reset_index().to_csv(SAIDA / "por_ponto.csv", index=False)
    colecao = cliente.get_collection(COLECAO)
    manifesto = {
        "catalogo": CATALOGO,
        "colecao": COLECAO,
        "colecao_titulo": colecao.title,
        "licenca": colecao.license,
        "acesso_utc": acesso,
        "codigo": codigo,
        "ambiente": {"python": platform.python_version(), "pystac-client": version("pystac-client"),
                     "rasterio": version("rasterio"), "dependencias": "uv.lock"},
        "periodo": [INICIO.isoformat(), FIM.isoformat()],
        "grade": {"latitudes": LATS, "longitudes": LONS},
        "regra": "SCL em scl_validos no pixel do ponto; uma observação por ponto e data (válida se alguma cena do dia for)",
        "scl_validos": sorted(stac.SCL_VALIDOS),
        "itens": sorted({(i.id, i.properties.get("s2:processing_baseline")) for i in itens}),
        "resumo": resumo,
        "saida_sha256": {f: acustica.sha256(SAIDA / f) for f in ["cenas_pontos.csv", "por_ponto.csv"]},
    }
    (SAIDA / "manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2, default=str))
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    print(por_ponto.to_string())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--permitir-sujo", action="store_true", help="roda com código não commitado e salva o diff")
    main(parser.parse_args().permitir_sujo)
