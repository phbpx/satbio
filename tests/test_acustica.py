import zlib
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import soundfile as sf

from satbio import acustica


def _wav(pasta: Path, nome: str, segundos: float = 60, taxa: int = 48000, canais: int = 1) -> Path:
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / nome
    forma = (int(segundos * taxa), canais) if canais > 1 else int(segundos * taxa)
    # ruído com semente fixa: conteúdos diferentes não colidem no sha256
    dados = np.random.default_rng(zlib.crc32(nome.encode())).integers(-100, 100, forma).astype("int16")
    sf.write(caminho, dados, taxa)
    return caminho


def _deteccoes(linhas: list[tuple]) -> pd.DataFrame:
    return pd.DataFrame(linhas, columns=["sitio", "arquivo", "especie", "inicio_s", "fim_s"])


def _pontos(**sobrescrever) -> pd.DataFrame:
    base = {"sitio": "RBA", "latitude": -6.2, "longitude": -35.2, "taxa_declarada_hz": 48000.0,
            "ano_declarado_metadata": "2022", "minutos_anotados": 1}
    base.update(sobrescrever)
    return pd.DataFrame([base])


def _tipos(problemas: pd.DataFrame) -> dict[str, set[str]]:
    return {t: set(g["arquivo"]) for t, g in problemas.groupby("tipo")}


def test_ler_nome_extrai_sitio_e_horario_do_relogio():
    nome = acustica.ler_nome("RBA_20221009_050240.wav")
    assert nome.sitio == "RBA"
    assert nome.inicio_relogio == datetime(2022, 10, 9, 5, 2, 40)
    assert nome.inicio_relogio.tzinfo is None


@pytest.mark.parametrize("nome", ["RBA_2022109_050240.wav", "RBA_20221009.wav", "RBA_20221340_050240.wav"])
def test_ler_nome_rejeita_nome_ou_data_invalidos(nome):
    with pytest.raises(ValueError):
        acustica.ler_nome(nome)


def test_tabela_gravacoes_le_cabecalho_e_acumula_erros(tmp_path):
    _wav(tmp_path / "RBA", "RBA_20221009_050240.wav")
    (tmp_path / "RBA" / "sem_padrao.wav").write_bytes(b"nao e wav")
    tabela = acustica.tabela_gravacoes(sorted((tmp_path / "RBA").glob("*.wav"))).set_index("arquivo")
    ok = tabela.loc["RBA_20221009_050240.wav"]
    assert ok["duracao_s"] == pytest.approx(60) and ok["taxa_hz"] == 48000 and ok["sitio_origem"] == "RBA"
    assert pd.isna(ok["erro"])
    erro = tabela.loc["sem_padrao.wav", "erro"]
    assert "fora do padrão" in erro and "cabeçalho ilegível" in erro


def test_tabela_campanhas_usa_primeira_e_ultima_gravacao(tmp_path):
    arquivos = [_wav(tmp_path / "RBA", "RBA_20221009_050240.wav"), _wav(tmp_path / "RBA", "RBA_20230123_110440.wav")]
    camp = acustica.tabela_campanhas(acustica.tabela_gravacoes(arquivos)).iloc[0]
    assert camp["campanha_id"] == "RBA-1"
    assert camp["inicio_relogio"] == datetime(2022, 10, 9, 5, 2, 40)
    assert camp["fim_relogio"] == datetime(2023, 1, 23, 11, 4, 40)
    assert camp["n_gravacoes"] == 2 and camp["esforco_min"] == pytest.approx(2)


def test_controle_qualidade_aponta_problemas_de_audio_e_anotacao(tmp_path):
    pasta = tmp_path / "RBA"
    arquivos = [
        _wav(pasta, "RBA_20221009_050240.wav"),
        _wav(pasta, "RBA_20221010_050240.wav", segundos=30),
        _wav(pasta, "RBA_20221011_050240.wav", taxa=44100),
        _wav(pasta, "RBA_20221013_050240.wav", canais=2),
        _wav(tmp_path / "RGU", "RBA_20221014_050240.wav"),
    ]
    gravacoes = acustica.tabela_gravacoes(arquivos)
    deteccoes = _deteccoes([
        ("RBA", "RBA_20221009_050240.wav", "Vireo chivi", 1.0, 2.0),
        ("RBA", "RBA_20221009_050240.wav", "Vireo chivi", 1.0, 2.0),
        ("RBA", "RBA_20221009_050240.wav", "Vireo chivi", 50.0, 75.0),
        ("RBA", "RBA_20221009_050240.wav", None, 3.0, 4.0),
        ("RGU", "RBA_20221009_050240.wav", "Turdus leucomelas", np.nan, 4.0),
        ("RBA", "RBA_20221012_050240.wav", "Vireo chivi", 1.0, 2.0),
    ])
    tipos = _tipos(acustica.controle_qualidade(gravacoes, deteccoes))
    assert tipos["anotacao_sem_audio"] == {"RBA_20221012_050240.wav"}
    assert tipos["duracao_curta"] == {"RBA_20221010_050240.wav"}
    assert tipos["taxa_divergente"] == {"RBA_20221011_050240.wav"}
    assert tipos["canais_nao_mono"] == {"RBA_20221013_050240.wav"}
    assert tipos["anotacao_fora_do_audio"] == {"RBA_20221009_050240.wav"}
    assert tipos["anotacao_duplicada"] == {"RBA_20221009_050240.wav"}
    assert tipos["anotacao_incompleta"] == {"RBA_20221009_050240.wav"}
    # sítio do nome × pasta de origem, e sítio da anotação × nome
    assert tipos["sitio_divergente"] == {"RBA_20221014_050240.wav", "RBA_20221009_050240.wav"}


def test_controle_qualidade_aponta_gravacao_e_horario_repetidos(tmp_path):
    a = _wav(tmp_path / "RBA", "RBA_20221009_050240.wav")
    copia = tmp_path / "copia" / "RBA_20221009_050240.wav"
    copia.parent.mkdir()
    copia.write_bytes(a.read_bytes())
    gravacoes = acustica.tabela_gravacoes([a, copia])
    tipos = _tipos(acustica.controle_qualidade(gravacoes, _deteccoes([])))
    assert tipos["gravacao_duplicada"] == {"RBA_20221009_050240.wav"}
    assert tipos["horario_repetido"] == {"RBA_20221009_050240.wav"}


def test_controle_qualidade_confere_metadados_dos_pontos(tmp_path):
    arquivos = [_wav(tmp_path / "RBA", "RBA_20221009_050240.wav"), _wav(tmp_path / "RBA", "RBA_20230123_110440.wav"),
                _wav(tmp_path / "RGU", "RGU_20221204_211245.wav", taxa=44100)]
    gravacoes = acustica.tabela_gravacoes(arquivos)
    pontos = pd.concat([_pontos(), _pontos(sitio="RBA"), _pontos(sitio="XYZ", latitude="-6,2")])
    tipos = _tipos(acustica.controle_qualidade(gravacoes, _deteccoes([]), pontos))
    assert tipos["ano_fora_do_declarado"] == {"RBA"}
    assert tipos["minutos_divergentes"] == {"RBA"}
    assert tipos["sitio_sem_ponto"] == {"RGU"}
    assert tipos["ponto_duplicado"] == {"RBA"}
    assert tipos["coordenada_invalida"] == {"XYZ"}


def test_controle_qualidade_confere_taxa_declarada(tmp_path):
    gravacoes = acustica.tabela_gravacoes([_wav(tmp_path / "RBA", "RBA_20221009_050240.wav", taxa=44100)])
    tipos = _tipos(acustica.controle_qualidade(gravacoes, _deteccoes([]), _pontos()))
    assert tipos["taxa_diferente_da_declarada"] == {"RBA_20221009_050240.wav"}


def test_controle_qualidade_sem_problemas_devolve_tabela_vazia(tmp_path):
    gravacoes = acustica.tabela_gravacoes([_wav(tmp_path / "RBA", "RBA_20221009_050240.wav")])
    deteccoes = _deteccoes([("RBA", "RBA_20221009_050240.wav", "Vireo chivi", 1.0, 2.0)])
    problemas = acustica.controle_qualidade(gravacoes, deteccoes, _pontos())
    assert problemas.empty and list(problemas.columns) == ["tipo", "arquivo", "detalhe"]
