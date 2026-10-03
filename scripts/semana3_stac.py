"""Semana 3 do piloto: série S2-16D-2 nos pontos do WABAD, até a véspera da campanha.

Uso:
    uv run python scripts/semana3_stac.py

Lê as tabelas da semana 2 (data/processed/wabad/) e grava a série em
data/processed/stac/ (fora do git), com um manifesto dos itens STAC usados.
"""

from __future__ import annotations

import json
import platform
import argparse
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import pandas as pd
from pystac_client import Client

from satbio import rastreio, acustica, stac

RAIZ = Path(__file__).resolve().parents[1]
WABAD = RAIZ / "data" / "processed" / "wabad"
SAIDA = RAIZ / "data" / "processed" / "stac"
DIAS_DE_SERIE = 365



def main(permitir_sujo: bool = False) -> None:
    codigo = rastreio.estado_do_codigo(RAIZ, SAIDA, permitir_sujo)
    acesso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    campanhas = pd.read_csv(WABAD / "campanhas.csv", parse_dates=["inicio_relogio"])
    pontos = pd.read_csv(WABAD / "pontos.csv").set_index("sitio")
    cliente = Client.open(stac.CATALOGO, headers={"User-Agent": stac.USER_AGENT})
    colecao = cliente.get_collection(stac.COLECAO)

    verificador = stac.VerificadorOrigem()
    linhas, consultas, itens_usados = [], {}, {}
    for _, camp in campanhas.iterrows():
        sitio = camp["sitio"]
        lon, lat = float(pontos.loc[sitio, "longitude"]), float(pontos.loc[sitio, "latitude"])
        inicio, corte = stac.janela(camp["inicio_relogio"].to_pydatetime(), DIAS_DE_SERIE)
        itens = stac.buscar_itens(lon, lat, inicio, corte)
        escolhidos = stac.um_item_por_periodo(itens, lon, lat)
        for item, posicao in escolhidos:
            linha = stac.linha_da_composicao(item, lon, lat, posicao, verificador=verificador)
            linhas.append({"sitio": sitio, "campanha_id": camp["campanha_id"], "corte": corte, **linha})
            checksums = {b: item.assets[b].extra_fields.get("checksum:multihash") for b in stac.BANDAS_LIDAS}
            sem_checksum = [b for b, c in checksums.items() if not c]
            if sem_checksum:
                print(f"  aviso: {item.id} sem checksum em {sem_checksum}")
            itens_usados[item.id] = {"criado": item.properties.get("created"), "atualizado": item.properties.get("updated"),
                                     "checksum_multihash": checksums}
        consultas[camp["campanha_id"]] = {
            "lon": lon, "lat": lat, "inicio": inicio.isoformat(), "corte": corte.isoformat(),
            "itens_encontrados": len(itens), "periodos": len(escolhidos),
            "periodos_esperados": DIAS_DE_SERIE // 16,
            "cobertura_dias": (stac.periodo(escolhidos[-1][0])[1].date() - stac.periodo(escolhidos[0][0])[0].date()).days
            if escolhidos else 0,
        }
        validas = sum(l["valido"] for l in linhas if l["campanha_id"] == camp["campanha_id"])
        print(f"{sitio}: {len(escolhidos)} composições de {inicio} a {corte}; {validas} válidas")

    serie = pd.DataFrame(linhas)
    SAIDA.mkdir(parents=True, exist_ok=True)
    serie.to_csv(SAIDA / "serie_s2.csv", index=False)

    manifesto = {
        "catalogo": stac.CATALOGO,
        "colecao": stac.COLECAO,
        "colecao_versao": colecao.extra_fields.get("version"),
        "colecao_titulo": colecao.title,
        "licenca": [l.href for l in colecao.links if l.rel == "license"],
        "acesso_utc": acesso,
        "codigo": codigo,
        "ambiente": {"python": platform.python_version(), "pystac-client": version("pystac-client"),
                     "rasterio": version("rasterio"), "dependencias": "uv.lock"},
        "colecao_origem": stac.COLECAO_ORIGEM,
        "regra_validade": "SCL da cena de origem em scl_validos, B02 <= b02_max_nevoa, bandas presentes, PROVENANCE no período (PRD 6.3, decisão D)",
        "variantes_sensibilidade": ["valido_scl_cubo_b02", "valido_somente_scl_cubo"],
        "colecao_origem_versao": cliente.get_collection(stac.COLECAO_ORIGEM).extra_fields.get("version"),
        "tolerancia_b04_origem": stac.TOLERANCIA_B04,
        "cenas_origem_usadas": sorted({c for cs in serie["cenas_origem_janela"].dropna() for c in cs.split(";")}),
        "cenas_origem_consultadas": verificador.cenas_consultadas(),
        "regra_de_corte": "composições com end_datetime <= véspera da primeira gravação (PRD 6.3)",
        "dias_de_serie": DIAS_DE_SERIE,
        "scl_validos": sorted(stac.SCL_VALIDOS),
        "b02_max_nevoa": stac.B02_MAX,
        "janela_px": 2 * stac.RAIO_JANELA_PX + 1,
        "bandas": stac.BANDAS_LIDAS,
        "consultas": consultas,
        "itens_checksum_multihash": itens_usados,
        "entradas_sha256": {f: acustica.sha256(WABAD / f) for f in ["campanhas.csv", "pontos.csv"]},
        "saida_sha256": {"serie_s2.csv": acustica.sha256(SAIDA / "serie_s2.csv")},
    }
    (SAIDA / "manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2, default=str))
    print(f"\n{len(serie)} linhas em {SAIDA / 'serie_s2.csv'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--permitir-sujo", action="store_true", help="roda com código não commitado e salva o diff")
    main(parser.parse_args().permitir_sujo)
