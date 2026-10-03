"""Acesso ao WABAD (Zenodo) e montagem das tabelas de pontos e detecções.

O registro é fixado pelo ID da versão para que o resultado seja reproduzível.
Cada download é conferido contra o checksum publicado pelo Zenodo, e a data
do download fica registrada ao lado do arquivo.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REGISTRO_ID = "20513304"
DOI = "10.5281/zenodo.20513304"
CONCEPT_DOI = "10.5281/zenodo.14191523"
FONTE_ANOTACOES = "anotacao_especialista_wabad_v4"
_API = f"https://zenodo.org/api/records/{REGISTRO_ID}"
_USER_AGENT = "satbio/0.1 (+https://github.com/phbpx/satbio)"


def _abrir(url: str, tentativas: int = 4, espera_s: float = 20.0):
    """Abre a URL repetindo em 403/429/5xx, que o Zenodo usa para limitar requisições."""
    for i in range(tentativas):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": _USER_AGENT}), timeout=120)
        except urllib.error.HTTPError as e:
            if (e.code in (403, 429) or e.code >= 500) and i < tentativas - 1:
                time.sleep(espera_s * (i + 1))
                continue
            raise
    raise RuntimeError("inalcançável")


def registro() -> dict:
    with _abrir(_API) as r:
        return json.load(r)


def arquivos_do_registro(reg: dict) -> dict[str, dict]:
    """Mapeia nome do arquivo -> {url, tamanho, md5} a partir do JSON do registro."""
    saida = {}
    for f in reg["files"]:
        algoritmo, _, valor = f["checksum"].partition(":")
        saida[f["key"]] = {"url": f["links"]["self"], "tamanho": f["size"],
                           "md5": valor if algoritmo == "md5" else None}
    return saida


def md5(caminho: Path) -> str:
    h = hashlib.md5()
    with open(caminho, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def _registro_download(destino: Path) -> Path:
    return destino.with_name(destino.name + ".download.json")


def baixar(info: dict, destino: Path) -> dict:
    """Baixa um arquivo do registro e devolve {caminho, md5, baixado_em_utc}.

    Reaproveita a cópia local se o md5 conferir; nesse caso a data devolvida é
    a do download original, não a da execução. Recusa arquivos sem md5
    publicado, porque não haveria como verificar o conteúdo.
    """
    if not info.get("md5"):
        raise ValueError(f"registro sem md5 para {destino.name}; download não verificável")
    destino.parent.mkdir(parents=True, exist_ok=True)
    reg_dl = _registro_download(destino)
    if destino.exists() and md5(destino) == info["md5"] and reg_dl.exists():
        return {"caminho": destino, **json.loads(reg_dl.read_text())}

    parcial = destino.with_name(destino.name + ".parcial")
    with _abrir(info["url"]) as r, open(parcial, "wb") as f:
        shutil.copyfileobj(r, f)
    if md5(parcial) != info["md5"]:
        parcial.unlink()
        raise ValueError(f"md5 não confere para {destino.name}")
    parcial.replace(destino)
    meta = {"md5": info["md5"], "url": info["url"],
            "baixado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    reg_dl.write_text(json.dumps(meta, indent=2))
    return {"caminho": destino, **meta}


def extrair_wavs(zip_path: Path, destino: Path) -> list[Path]:
    """Extrai só os .wav do zip, achatando pastas.

    Levanta ValueError se dois membros tiverem o mesmo nome em pastas
    diferentes, porque achatar faria um sobrescrever o outro.
    """
    destino.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        membros = [m for m in zf.infolist()
                   if not m.is_dir() and m.filename.lower().endswith(".wav")
                   and not Path(m.filename).name.startswith("._")]
        nomes = [Path(m.filename).name for m in membros]
        repetidos = sorted({n for n in nomes if nomes.count(n) > 1})
        if repetidos:
            raise ValueError(f"{zip_path.name}: nomes de .wav repetidos em pastas diferentes: {repetidos[:5]}")

        extraidos = []
        for membro, nome in zip(membros, nomes):
            alvo = destino / nome  # `nome` é só o último componente: não sai de `destino`
            if not (alvo.exists() and alvo.stat().st_size == membro.file_size):
                with zf.open(membro) as origem, open(alvo, "wb") as f:
                    shutil.copyfileobj(origem, f)
            extraidos.append(alvo)
    return extraidos


def _ler_csv(caminho: Path) -> pd.DataFrame:
    """Lê CSV em UTF-8 e, se falhar, em Latin-1.

    O Metadata.csv da v4 mistura codificações: a maioria dos acentos está em
    cp1252 e alguns bytes estão corrompidos na origem (ex.: "Caraj\\x98s").
    Latin-1 lê qualquer byte, então só nomes em texto livre podem sair com
    caracteres estranhos; IDs de sítio e coordenadas são ASCII.
    """
    try:
        return pd.read_csv(caminho, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(caminho, encoding="latin-1")


def _taxa_em_hz(texto) -> float | None:
    m = re.search(r"([\d.,]+)\s*kHz", str(texto), re.IGNORECASE)
    return float(m.group(1).replace(",", ".")) * 1000 if m else None


def ler_pontos(metadata_csv: Path, sitios: list[str]) -> pd.DataFrame:
    """Tabela de pontos a partir do Metadata.csv, sem a coluna de contato (dado pessoal).

    Cada linha é o centro de um sítio, que pode reunir mais de um gravador.
    `grupo_validacao` é provisório (o próprio sítio): os blocos espaciais
    precisam ser definidos antes de qualquer avaliação, juntando sítios
    próximos ou da mesma equipe se for o caso.
    `ano_declarado_metadata` é só o que a fonte declara; as datas usadas no
    projeto vêm dos nomes dos arquivos.
    """
    meta = _ler_csv(metadata_csv)
    meta = meta[meta["Site ID"].isin(sitios)]
    return pd.DataFrame({
        "sitio": meta["Site ID"],
        "grupo_validacao": meta["Site ID"],
        "area_estudo": meta["Study area"],
        "pais": meta["Recording location"],
        "bioma_olson": meta["Biome"],
        "latitude": meta["Latitude"],
        "longitude": meta["Longitude"],
        "precisao_coord": "centro do sítio (Metadata.csv)",
        "gravador": meta["Recorder (+ microphone)"],
        "taxa_declarada_hz": meta["Sampling rate"].map(_taxa_em_hz),
        "ano_declarado_metadata": meta["Recording date"].astype(str),
        "minutos_anotados": meta["Minutes Annotated"],
    }).reset_index(drop=True)


def ler_deteccoes(anotacoes_csv: Path, sitios: list[str]) -> pd.DataFrame:
    """Anotações do Pooled annotations.csv dos sítios pedidos.

    Cada linha é uma vocalização anotada por especialista: a mesma espécie
    pode aparecer várias vezes no mesmo minuto. Contar linhas mede atividade
    vocal, não presença. A ausência de uma espécie num minuto é não detecção.
    """
    anot = _ler_csv(anotacoes_csv)
    anot = anot[anot["Site"].isin(sitios)]
    return pd.DataFrame({
        "sitio": anot["Site"],
        "arquivo": anot["Recording"],
        "especie": anot["Species"],
        "inicio_s": anot["Begin_Time_(s)"],
        "fim_s": anot["End_Time_(s)"],
        "freq_min_hz": anot["Low_Freq_(Hz)"],
        "freq_max_hz": anot["High_Freq_(Hz)"],
        "fonte": FONTE_ANOTACOES,
    }).reset_index(drop=True)
