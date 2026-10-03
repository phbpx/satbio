"""Semana 2 do piloto: vincula áudios do WABAD a pontos, datas e anotações.

Uso:
    uv run python scripts/semana2_wabad.py [SITIO ...]

Sem argumentos, processa os sítios escolhidos para o piloto. Os dados brutos
vão para data/raw/wabad/ e as tabelas para data/processed/wabad/ (ambos fora
do git).
"""

from __future__ import annotations

import json
import platform
import argparse
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from satbio import rastreio, acustica, wabad

SITIOS_PILOTO = ["RBA", "RGU", "RME", "RFP"]
RAIZ = Path(__file__).resolve().parents[1]
BRUTO = RAIZ / "data" / "raw" / "wabad"
PROCESSADO = RAIZ / "data" / "processed" / "wabad"



def main(sitios: list[str], permitir_sujo: bool = False) -> None:
    codigo = rastreio.estado_do_codigo(RAIZ, PROCESSADO, permitir_sujo)
    reg = wabad.registro()
    arquivos = wabad.arquivos_do_registro(reg)

    downloads = {
        "Metadata.csv": wabad.baixar(arquivos["Metadata.csv"], BRUTO / "Metadata.csv"),
        "Pooled annotations.csv": wabad.baixar(arquivos["Pooled annotations.csv"], BRUTO / "Pooled_annotations.csv"),
    }
    wavs: list[Path] = []
    wavs_por_zip = {}
    for sitio in sitios:
        nome_zip = f"{sitio}.zip"
        downloads[nome_zip] = wabad.baixar(arquivos[nome_zip], BRUTO / "zips" / nome_zip)
        extraidos = wabad.extrair_wavs(downloads[nome_zip]["caminho"], BRUTO / "audio" / sitio)
        wavs_por_zip[nome_zip] = len(extraidos)
        wavs += extraidos
        print(f"{sitio}: {len(extraidos)} áudios")

    pontos = wabad.ler_pontos(downloads["Metadata.csv"]["caminho"], sitios)
    deteccoes = wabad.ler_deteccoes(downloads["Pooled annotations.csv"]["caminho"], sitios)
    gravacoes = acustica.tabela_gravacoes(wavs)
    gravacoes["fuso"] = "desconhecido"
    gravacoes["ponto_id"] = "desconhecido (centro do sítio)"
    campanhas = acustica.tabela_campanhas(gravacoes)
    problemas = acustica.controle_qualidade(gravacoes, deteccoes, pontos)

    PROCESSADO.mkdir(parents=True, exist_ok=True)
    tabelas = {"pontos": pontos, "campanhas": campanhas, "gravacoes": gravacoes,
               "deteccoes": deteccoes, "controle_qualidade": problemas}
    for nome, tabela in tabelas.items():
        tabela.to_csv(PROCESSADO / f"{nome}.csv", index=False)

    manifesto = {
        "base": "WABAD",
        "doi": wabad.DOI,
        "concept_doi": wabad.CONCEPT_DOI,
        "registro_versao": reg.get("metadata", {}).get("version"),
        "registro_publicado": reg.get("metadata", {}).get("publication_date"),
        "registro_modificado": reg.get("modified"),
        "licenca_campo_zenodo": reg.get("metadata", {}).get("license", {}).get("id"),
        "licenca_observacao": "descrição do registro indica CC BY-NC 4.0; tratar como não comercial (ver docs/bases/wabad.md)",
        "executado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "codigo": codigo,
        "ambiente": {"python": platform.python_version(), "pandas": version("pandas"),
                     "soundfile": version("soundfile"), "dependencias": "uv.lock"},
        "parametros_qc": acustica.PARAMETROS_QC,
        "sitios": sitios,
        "downloads": {nome: {k: v for k, v in d.items() if k != "caminho"} for nome, d in downloads.items()},
        "wavs_extraidos_por_zip": wavs_por_zip,
        "saidas_sha256": {f"{nome}.csv": acustica.sha256(PROCESSADO / f"{nome}.csv") for nome in tabelas},
        "fuso": "desconhecido: inicio_relogio é o relógio do gravador, sem fuso declarado pela fonte",
    }
    (PROCESSADO / "manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2))

    print(f"\npontos: {len(pontos)} | campanhas: {len(campanhas)} | gravações: {len(gravacoes)} | anotações: {len(deteccoes)}")
    print("problemas de controle de qualidade:")
    print(problemas["tipo"].value_counts().to_string() if len(problemas) else "  nenhum")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sitios", nargs="*", help=f"sítios do WABAD (padrão: {' '.join(SITIOS_PILOTO)})")
    parser.add_argument("--permitir-sujo", action="store_true", help="roda com código não commitado e salva o diff")
    args = parser.parse_args()
    main([s.upper() for s in args.sitios] or SITIOS_PILOTO, args.permitir_sujo)
