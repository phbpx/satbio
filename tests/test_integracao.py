import itertools

import pandas as pd
import pytest

from satbio import integracao


def test_riqueza_rarefeita_bate_com_a_enumeracao():
    # 4 minutos; espécie A em 2 deles, B em 1, C em todos
    minutos = {"A": {0, 1}, "B": {2}, "C": {0, 1, 2, 3}}
    m = 2
    esperado = sum(len({e for e, ms in minutos.items() if ms & set(c)})
                   for c in itertools.combinations(range(4), m)) / 6
    obtido = integracao.riqueza_rarefeita(pd.Series({e: len(ms) for e, ms in minutos.items()}), 4, m)
    assert obtido == pytest.approx(esperado)


def test_riqueza_rarefeita_no_esforco_total_e_a_riqueza_observada():
    assert integracao.riqueza_rarefeita(pd.Series([1, 3, 5]), 5, 5) == pytest.approx(3)
    with pytest.raises(ValueError):
        integracao.riqueza_rarefeita(pd.Series([1]), 5, 6)


def _gravacoes(arquivos_sitio_data):
    return pd.DataFrame([{"arquivo": a, "sitio": s, "inicio_relogio": d, "erro": None}
                         for a, s, d in arquivos_sitio_data])


def _campanhas(linhas):
    return pd.DataFrame(linhas, columns=["sitio", "campanha_id", "inicio_relogio", "fim_relogio"])


def test_resumo_acustico_padroniza_pelo_menor_esforco():
    gravacoes = _gravacoes([("a1", "A", "2022-10-01"), ("a2", "A", "2022-10-02"), ("a3", "A", "2022-10-03"),
                            ("b1", "B", "2022-10-01")])
    deteccoes = pd.DataFrame({"arquivo": ["a1", "a1", "a2", "a3", "b1"], "especie": ["x", "x", "y", "z", "x"]})
    campanhas = _campanhas([("A", "A-1", "2022-10-01", "2022-10-03"), ("B", "B-1", "2022-10-01", "2022-10-01")])
    resumo = integracao.resumo_acustico(gravacoes, deteccoes, campanhas).set_index("sitio")
    assert resumo.loc["A", "especies_detectadas"] == 3 and resumo.loc["A", "esforco_padrao_min"] == 1
    assert resumo.loc["A", "riqueza_rarefeita"] == pytest.approx(1.0)  # cada minuto tem uma espécie distinta
    assert resumo.loc["A", "especies"] == "x;y;z"


def _serie(datas, ndvi=0.8, ndmi=0.3, n_validos=9):
    return pd.DataFrame({"sitio": "A", "campanha_id": "A-1", "corte": "2022-12-31",
                         "inicio_composicao": datas, "viz_n_validos": n_validos,
                         "viz_NDVI_mediana": ndvi, "viz_NDMI_mediana": ndmi})


def test_descritores_exigem_cobertura_em_todos_os_trimestres():
    # 12 composições, todas no primeiro semestre: falta cobertura
    datas = pd.date_range("2022-01-05", periods=12, freq="14D").strftime("%Y-%m-%d")
    linha = integracao.descritores_opticos(_serie(datas)).iloc[0]
    assert not linha["cobertura_ok"] and linha["trimestres_cobertos"] < 4 and pd.isna(linha["ndvi_mediana"])


def test_descritores_com_cobertura_completa():
    datas = pd.date_range("2022-01-05", periods=22, freq="16D").strftime("%Y-%m-%d")
    ndvi = [0.7 + 0.01 * i for i in range(22)]
    ndmi = [0.3] * 18 + [0.2] * 4  # queda no último trimestre
    serie = _serie(datas, ndvi=ndvi, ndmi=ndmi)
    serie.loc[0, "viz_n_validos"] = 3  # janela com minoria válida: não entra
    linha = integracao.descritores_opticos(serie).iloc[0]
    assert linha["cobertura_ok"] and linha["composicoes_usadas"] == 21
    usados = pd.Series(ndvi[1:])
    assert linha["ndvi_amplitude_p90_p10"] == pytest.approx(usados.quantile(0.9) - usados.quantile(0.1))
    assert linha["ndmi_mudanca_recente"] < 0


def test_dicionario_falha_se_coluna_nao_tem_descricao(tmp_path, monkeypatch):
    from satbio import dicionario
    (tmp_path / "t.csv").write_text("sitio,coluna_nova\nA,1\n")
    monkeypatch.setattr(dicionario, "TABELAS", {"t": ("t.csv", "tabela de teste")})
    with pytest.raises(ValueError, match="t.coluna_nova"):
        dicionario.gerar_markdown(tmp_path)
    (tmp_path / "t.csv").write_text("sitio\nA\n")
    assert "| `sitio` | código do sítio no WABAD |" in dicionario.gerar_markdown(tmp_path)


def test_resumo_acustico_separa_duas_campanhas_do_mesmo_sitio():
    gravacoes = _gravacoes([("a1", "A", "2022-03-01"), ("a2", "A", "2022-03-02"), ("a3", "A", "2022-09-01")])
    deteccoes = pd.DataFrame({"arquivo": ["a1", "a2", "a3"], "especie": ["x", "y", "z"]})
    campanhas = _campanhas([("A", "A-1", "2022-03-01", "2022-03-02"), ("A", "A-2", "2022-09-01", "2022-09-01")])
    resumo = integracao.resumo_acustico(gravacoes, deteccoes, campanhas).set_index("campanha_id")
    assert resumo.loc["A-1", "especies"] == "x;y" and resumo.loc["A-2", "especies"] == "z"
    assert resumo.loc["A-1", "esforco_padrao_min"] == 1  # menor esforço entre campanhas, não entre sítios


def test_gravacao_fora_de_campanha_e_erro():
    with pytest.raises(ValueError, match="fora de qualquer campanha"):
        integracao.gravacoes_por_campanha(_gravacoes([("a1", "A", "2023-01-01")]),
                                          _campanhas([("A", "A-1", "2022-03-01", "2022-03-02")]))


def test_mudanca_recente_exige_duas_composicoes_no_ultimo_trimestre():
    datas = list(pd.date_range("2022-01-05", periods=20, freq="14D").strftime("%Y-%m-%d"))
    datas = [d for d in datas if d < "2022-09-20"] + ["2022-11-20"]  # meio do período: só uma no último trimestre
    linha = integracao.descritores_opticos(_serie(datas)).iloc[0]
    assert linha["cobertura_ok"] and linha["n_ultimo_trimestre"] == 1 and pd.isna(linha["ndmi_mudanca_recente"])


def test_trimestre_usa_a_data_de_observacao():
    datas = list(pd.date_range("2022-01-05", periods=22, freq="16D").strftime("%Y-%m-%d"))
    serie = _serie(datas)
    serie["data_observacao"] = serie["inicio_composicao"]
    serie.loc[serie.index[-1], "data_observacao"] = "2022-09-01"  # observação antes do último trimestre
    com_obs = integracao.descritores_opticos(serie).iloc[0]["n_ultimo_trimestre"]
    sem_obs = integracao.descritores_opticos(serie.drop(columns="data_observacao")).iloc[0]["n_ultimo_trimestre"]
    assert com_obs == sem_obs - 1


def test_tabela_analitica_marca_campanha_sem_serie_e_recusa_serie_orfa():
    acustico = pd.DataFrame({"sitio": ["A", "B"], "campanha_id": ["A-1", "B-1"]})
    pontos = pd.DataFrame({"sitio": ["A", "B"], "grupo_validacao": ["A", "B"], "latitude": 0, "longitude": 0,
                           "gravador": "x"})
    optico = pd.DataFrame({"sitio": ["A"], "campanha_id": ["A-1"], "cobertura_ok": [True]})
    tabela = integracao.tabela_analitica(acustico, optico, pontos).set_index("campanha_id")
    assert tabela.loc["A-1", "cobertura_ok"] and not tabela.loc["B-1", "cobertura_ok"]
    with pytest.raises(ValueError, match="sem campanha acústica"):
        integracao.tabela_analitica(acustico, pd.concat([optico, optico.assign(sitio="C", campanha_id="C-1")]),
                                    pontos)
