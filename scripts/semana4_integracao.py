"""Semana 4 do piloto: tabela analítica de exemplo e dicionário de dados.

Uso:
    uv run python scripts/semana4_integracao.py [--permitir-sujo]

Junta as saídas das semanas 2 e 3 numa tabela por sítio × campanha
(data/processed/integracao/, fora do git) e gera docs/dicionario-dados.md.
A tabela é um exemplo da integração: 4 sítios do WABAD, sem matas de
referência e sem cabrucas; não serve para estimar associações.
"""

from __future__ import annotations

import argparse
import json
import platform
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import pandas as pd

from satbio import acustica, dicionario, integracao, rastreio

RAIZ = Path(__file__).resolve().parents[1]
WABAD = RAIZ / "data" / "processed" / "wabad"
STAC = RAIZ / "data" / "processed" / "stac"
SAIDA = RAIZ / "data" / "processed" / "integracao"


def main(permitir_sujo: bool = False) -> None:
    codigo = rastreio.estado_do_codigo(RAIZ, SAIDA, permitir_sujo)
    gravacoes = pd.read_csv(WABAD / "gravacoes.csv")
    deteccoes = pd.read_csv(WABAD / "deteccoes.csv")
    campanhas = pd.read_csv(WABAD / "campanhas.csv")
    pontos = pd.read_csv(WABAD / "pontos.csv")
    serie = pd.read_csv(STAC / "serie_s2.csv")

    acustico = integracao.resumo_acustico(gravacoes, deteccoes, campanhas)
    optico = integracao.descritores_opticos(serie)
    tabela = integracao.tabela_analitica(acustico, optico, pontos)

    SAIDA.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(SAIDA / "tabela_piloto.csv", index=False)
    (RAIZ / "docs" / "dicionario-dados.md").write_text(dicionario.gerar_markdown(RAIZ))

    entradas = {f"wabad/{f}": WABAD / f for f in ["gravacoes.csv", "deteccoes.csv", "campanhas.csv", "pontos.csv"]}
    entradas["stac/serie_s2.csv"] = STAC / "serie_s2.csv"
    manifesto = {
        "executado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "codigo": codigo,
        "ambiente": {"python": platform.python_version(), "pandas": version("pandas"), "dependencias": "uv.lock"},
        "regras": {
            "min_composicoes_validas": integracao.MIN_COMPOSICOES_VALIDAS,
            "trimestres": integracao.TRIMESTRES,
            "min_pixels_validos_janela": integracao.MIN_PIXELS_VALIDOS_JANELA,
            "min_composicoes_ultimo_trimestre": integracao.MIN_COMPOSICOES_ULTIMO_TRIMESTRE,
            "trimestre_da_composicao": "data de observação do pixel central (PROVENANCE)",
            "esforco_padrao_min": int(acustico["esforco_padrao_min"].iloc[0]),
        },
        "aviso": "exemplo de integração do piloto; 4 sítios do WABAD, sem matas de referência e sem cabrucas",
        "entradas_sha256": {nome: acustica.sha256(c) for nome, c in entradas.items()},
        "saida_sha256": {"tabela_piloto.csv": acustica.sha256(SAIDA / "tabela_piloto.csv"),
                         "docs/dicionario-dados.md": acustica.sha256(RAIZ / "docs" / "dicionario-dados.md")},
        # Encadeia as execuções anteriores: commit e hash de cada manifesto de origem.
        "etapas_anteriores": {
            etapa: {"manifesto_sha256": acustica.sha256(m), "commit": json.loads(m.read_text()).get("codigo", {}).get("commit")}
            for etapa, m in {"semana2": WABAD / "manifesto.json", "semana3": STAC / "manifesto.json"}.items()
        },
    }
    (SAIDA / "manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2, default=str))

    colunas = ["sitio", "minutos_validos", "especies_detectadas", "riqueza_rarefeita", "composicoes_usadas",
               "trimestres_cobertos", "n_ultimo_trimestre", "cobertura_ok", "ndvi_mediana", "ndmi_mediana", "ndvi_amplitude_p90_p10",
               "ndmi_mudanca_recente"]
    print(tabela[colunas].round(3).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--permitir-sujo", action="store_true", help="roda com código não commitado e salva o diff")
    main(parser.parse_args().permitir_sujo)
