"""Leitura de gravações e controle de qualidade.

As funções aqui não dependem de uma base específica: recebem caminhos e
tabelas e devolvem tabelas. O fuso horário nunca é presumido: a data e a hora
lidas do nome do arquivo são o horário do relógio do gravador
(`inicio_relogio`), sem fuso, até que a fonte confirme qual é.

Unidades: a gravação (um arquivo de áudio) é subamostra do sítio × campanha.
Ela não é réplica independente.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
import soundfile as sf

# Padrão SITIO_AAAAMMDD_HHMMSS.wav, usado pelo WABAD.
_PADRAO_NOME = re.compile(r"^(?P<sitio>[A-Za-z0-9]+)_(?P<data>\d{8})_(?P<hora>\d{6})\.wav$", re.IGNORECASE)

PARAMETROS_QC = {
    "duracao_minima_s": 55.0,
    "tolerancia_fim_anotacao_s": 0.01,
}


@dataclass(frozen=True)
class NomeGravacao:
    sitio: str
    inicio_relogio: datetime


def ler_nome(nome: str) -> NomeGravacao:
    """Extrai sítio e início da gravação do nome do arquivo.

    Levanta ValueError se o nome não seguir o padrão ou a data for inválida,
    para que nomes inesperados apareçam no controle de qualidade em vez de
    virarem datas erradas.
    """
    m = _PADRAO_NOME.match(nome)
    if m is None:
        raise ValueError(f"nome fora do padrão SITIO_AAAAMMDD_HHMMSS.wav: {nome!r}")
    inicio = datetime.strptime(m["data"] + m["hora"], "%Y%m%d%H%M%S")
    return NomeGravacao(sitio=m["sitio"].upper(), inicio_relogio=inicio)


def sha256(caminho: Path, bloco: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        while chunk := f.read(bloco):
            h.update(chunk)
    return h.hexdigest()


def tabela_gravacoes(arquivos: list[Path]) -> pd.DataFrame:
    """Uma linha por arquivo de áudio, lendo só o cabeçalho de cada WAV.

    `sitio_origem` é o nome da pasta do arquivo, usado para conferir o sítio do
    nome. Arquivos com nome fora do padrão ou cabeçalho ilegível entram na
    tabela com a coluna `erro` preenchida, em vez de serem descartados.
    """
    linhas = []
    for caminho in sorted(arquivos):
        erros: list[str] = []
        linha: dict = {"arquivo": caminho.name, "sitio": None, "sitio_origem": caminho.parent.name.upper(),
                       "inicio_relogio": pd.NaT, "duracao_s": None, "taxa_hz": None, "canais": None,
                       "sha256": sha256(caminho)}
        try:
            nome = ler_nome(caminho.name)
            linha["sitio"] = nome.sitio
            linha["inicio_relogio"] = nome.inicio_relogio
        except ValueError as e:
            erros.append(str(e))
        try:
            info = sf.info(caminho)
            linha["duracao_s"] = info.frames / info.samplerate
            linha["taxa_hz"] = info.samplerate
            linha["canais"] = info.channels
        except RuntimeError as e:
            erros.append(f"cabeçalho ilegível: {e}")
        linha["erro"] = "; ".join(erros) or None
        linhas.append(linha)
    return pd.DataFrame(linhas)


def tabela_campanhas(gravacoes: pd.DataFrame) -> pd.DataFrame:
    """Uma campanha por sítio, delimitada pelas próprias gravações.

    Supõe uma única campanha por sítio, o que vale para a seleção do WABAD
    usada no piloto. `inicio_relogio` é a data que limita as janelas de
    imagem: usar o fim da campanha traria informação posterior às primeiras
    gravações.
    """
    validas = gravacoes[gravacoes["erro"].isna()]
    camp = validas.groupby("sitio").agg(
        inicio_relogio=("inicio_relogio", "min"),
        fim_relogio=("inicio_relogio", "max"),
        n_gravacoes=("arquivo", "size"),
        esforco_min=("duracao_s", lambda s: s.sum() / 60),
    ).reset_index()
    camp.insert(1, "campanha_id", camp["sitio"] + "-1")
    return camp


def controle_qualidade(
    gravacoes: pd.DataFrame,
    deteccoes: pd.DataFrame,
    pontos: pd.DataFrame | None = None,
    duracao_minima_s: float = PARAMETROS_QC["duracao_minima_s"],
    tolerancia_s: float = PARAMETROS_QC["tolerancia_fim_anotacao_s"],
) -> pd.DataFrame:
    """Lista problemas nos áudios, nas anotações e no vínculo com os metadados.

    `gravacoes` vem de `tabela_gravacoes`. `deteccoes` precisa de `sitio`,
    `arquivo`, `especie`, `inicio_s` e `fim_s`. `pontos`, se informado, precisa
    de `sitio`, `latitude`, `longitude`, `taxa_declarada_hz`,
    `ano_declarado_metadata` e `minutos_anotados`. Devolve uma linha por
    problema, com `tipo`, `arquivo` (ou sítio) e `detalhe`.
    """
    problemas: list[dict] = []

    def registrar(tipo: str, alvo: str, detalhe: str) -> None:
        problemas.append({"tipo": tipo, "arquivo": alvo, "detalhe": detalhe})

    # Áudios
    for _, g in gravacoes[gravacoes["erro"].notna()].iterrows():
        registrar("erro_leitura", g["arquivo"], g["erro"])
    for arquivo in gravacoes.loc[gravacoes["arquivo"].duplicated(), "arquivo"]:
        registrar("gravacao_duplicada", arquivo, "mesmo nome de arquivo repetido")
    for _, g in gravacoes[gravacoes["sha256"].duplicated(keep=False)].iterrows():
        registrar("gravacao_duplicada", g["arquivo"], f"conteúdo idêntico a outro arquivo (sha256 {g['sha256'][:12]})")

    validas = gravacoes[gravacoes["erro"].isna()]
    for _, g in validas[validas["sitio"] != validas["sitio_origem"]].iterrows():
        registrar("sitio_divergente", g["arquivo"], f"nome indica {g['sitio']}, arquivo veio de {g['sitio_origem']}")
    for _, g in validas[validas["duracao_s"] < duracao_minima_s].iterrows():
        registrar("duracao_curta", g["arquivo"], f"{g['duracao_s']:.2f} s < {duracao_minima_s} s")
    for _, g in validas[validas["canais"] != 1].iterrows():
        registrar("canais_nao_mono", g["arquivo"], f"{g['canais']} canais")
    # Mesmo horário repetido no sítio indica mais de um gravador sob o mesmo "sítio".
    for _, g in validas[validas.duplicated(["sitio", "inicio_relogio"], keep=False)].iterrows():
        registrar("horario_repetido", g["arquivo"], f"outro arquivo de {g['sitio']} começa em {g['inicio_relogio']}")
    # Taxa diferente da predominante no sítio indica gravador ou configuração diferente.
    for sitio, grupo in validas.groupby("sitio"):
        moda = grupo["taxa_hz"].mode().iloc[0]
        for _, g in grupo[grupo["taxa_hz"] != moda].iterrows():
            registrar("taxa_divergente", g["arquivo"], f"{g['taxa_hz']} Hz; predominante no sítio {sitio}: {moda} Hz")

    # Anotações
    incompletas = deteccoes[deteccoes[["especie", "inicio_s", "fim_s"]].isna().any(axis=1)]
    for _, d in incompletas.iterrows():
        registrar("anotacao_incompleta", str(d["arquivo"]), "espécie, início ou fim ausente")
    for _, d in deteccoes[deteccoes.duplicated(["arquivo", "especie", "inicio_s", "fim_s"])].iterrows():
        registrar("anotacao_duplicada", d["arquivo"], f"{d['especie']} {d['inicio_s']}–{d['fim_s']} s")

    sitio_do_nome = validas.set_index("arquivo")["sitio"]
    for _, d in deteccoes[deteccoes["arquivo"].isin(sitio_do_nome.index)].iterrows():
        if d["sitio"] != sitio_do_nome[d["arquivo"]]:
            registrar("sitio_divergente", d["arquivo"], f"anotação indica {d['sitio']}, nome indica {sitio_do_nome[d['arquivo']]}")

    com_audio = set(gravacoes["arquivo"])
    anotados = set(deteccoes["arquivo"])
    for arquivo in sorted(anotados - com_audio):
        registrar("anotacao_sem_audio", arquivo, "arquivo anotado ausente no zip")
    for arquivo in sorted(com_audio - anotados):
        registrar("audio_sem_anotacao", arquivo, "áudio sem nenhuma anotação")

    duracoes = validas.drop_duplicates("arquivo").set_index("arquivo")["duracao_s"]
    juntas = deteccoes[deteccoes["arquivo"].isin(duracoes.index)].dropna(subset=["inicio_s", "fim_s"]).copy()
    juntas["duracao_s"] = juntas["arquivo"].map(duracoes)
    fora = juntas[(juntas["fim_s"] > juntas["duracao_s"] + tolerancia_s) | (juntas["inicio_s"] < 0)
                  | (juntas["fim_s"] < juntas["inicio_s"])]
    for _, d in fora.iterrows():
        registrar("anotacao_fora_do_audio", d["arquivo"],
                  f"{d['inicio_s']}–{d['fim_s']} s em áudio de {d['duracao_s']:.2f} s")

    if pontos is not None:
        _controle_pontos(validas, pontos, registrar)

    return pd.DataFrame(problemas, columns=["tipo", "arquivo", "detalhe"])


def _controle_pontos(validas: pd.DataFrame, pontos: pd.DataFrame, registrar) -> None:
    """Confere o vínculo entre as gravações e a tabela de pontos (metadados da fonte)."""
    for sitio in sorted(set(validas["sitio"]) - set(pontos["sitio"])):
        registrar("sitio_sem_ponto", sitio, "sítio das gravações ausente na tabela de pontos")
    for sitio in pontos.loc[pontos["sitio"].duplicated(), "sitio"]:
        registrar("ponto_duplicado", sitio, "sítio repetido na tabela de pontos")

    lat = pd.to_numeric(pontos["latitude"], errors="coerce")
    lon = pd.to_numeric(pontos["longitude"], errors="coerce")
    invalidas = lat.isna() | lon.isna() | ~lat.between(-90, 90) | ~lon.between(-180, 180)
    for _, p in pontos[invalidas].iterrows():
        registrar("coordenada_invalida", p["sitio"], f"lat={p['latitude']!r}, lon={p['longitude']!r}")

    info = pontos.drop_duplicates("sitio").set_index("sitio")
    for sitio, grupo in validas[validas["sitio"].isin(info.index)].groupby("sitio"):
        p = info.loc[sitio]
        anos_declarados = {int(a) for a in re.findall(r"\d{4}", str(p["ano_declarado_metadata"]))}
        anos_arquivos = set(grupo["inicio_relogio"].dt.year)
        if anos_declarados and anos_arquivos - anos_declarados:
            registrar("ano_fora_do_declarado", sitio,
                      f"arquivos de {sorted(anos_arquivos)}; metadado declara {sorted(anos_declarados)}")
        if pd.notna(p["minutos_anotados"]) and len(grupo) != int(p["minutos_anotados"]):
            registrar("minutos_divergentes", sitio,
                      f"{len(grupo)} gravações; metadado declara {int(p['minutos_anotados'])} minutos anotados")
        if pd.notna(p["taxa_declarada_hz"]):
            for _, g in grupo[grupo["taxa_hz"] != p["taxa_declarada_hz"]].iterrows():
                registrar("taxa_diferente_da_declarada", g["arquivo"],
                          f"{g['taxa_hz']} Hz; metadado declara {int(p['taxa_declarada_hz'])} Hz")
