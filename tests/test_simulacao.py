import numpy as np
import pandas as pd
import pytest

from satbio import simulacao
from satbio.simulacao import Cenario


def test_simular_dados_gera_resposta_entre_0_e_1_e_preditores():
    dados = simulacao.simular_dados(Cenario(n_cabrucas=15), np.random.default_rng(1))
    assert len(dados) == 15
    assert dados["resposta"].between(0, 1).all() and dados["resposta"].std() > 0
    assert set(simulacao.MODELOS["M3"]) <= set(dados.columns)


def test_fracoes_de_sinal_acima_de_1_sao_recusadas():
    with pytest.raises(ValueError, match="somam mais que 1"):
        simulacao.simular_dados(Cenario(n_cabrucas=5, sinal_estavel=0.6, sinal_paisagem=0.3, sinal_temporal=0.2),
                                np.random.default_rng(1))


def test_resposta_acompanha_a_condicao_ecologica():
    # com toda a variância no sinal estável e preditor quase sem ruído, a mediana prevê a resposta
    c = Cenario(n_cabrucas=200, sinal_estavel=0.9, sinal_paisagem=0.0, sinal_temporal=0.0, ruido_mediana=0.05)
    dados = simulacao.simular_dados(c, np.random.default_rng(2))
    assert dados["resposta"].corr(dados["estavel_mediana"]) < -0.5  # melhor condição, mais perto da referência


def _ridge_independente(x_treino, y_treino, x_teste, lam):
    """Ridge como mínimos quadrados aumentados, com padronização feita só no treino."""
    media, dp = x_treino.mean(axis=0), x_treino.std(axis=0)
    zt, zs = (x_treino - media) / dp, (x_teste - media) / dp
    a = np.vstack([zt, np.sqrt(lam) * np.eye(zt.shape[1])])
    b = np.concatenate([y_treino - y_treino.mean(), np.zeros(zt.shape[1])])
    beta = np.linalg.lstsq(a, b, rcond=None)[0]
    return y_treino.mean() + zs @ beta


def test_erros_deixando_um_fora_batem_com_implementacao_independente():
    dados = simulacao.simular_dados(Cenario(n_cabrucas=14), np.random.default_rng(3))
    cols = simulacao.MODELOS["M3"]
    x, y = dados[cols].to_numpy(), dados["resposta"].to_numpy()
    esperado = []
    for i in range(len(y)):
        treino = np.arange(len(y)) != i
        esperado.append(abs(_ridge_independente(x[treino], y[treino], x[i:i + 1], 1.0)[0] - y[i]))
    assert simulacao.erros_deixando_um_fora(dados, cols, lam=1.0) == pytest.approx(esperado, abs=1e-10)


@pytest.mark.parametrize("ganho,inf,sup,esperado", [
    (0.20, 0.11, 0.30, "relevante confirmado"),
    (0.10, 0.10, 0.12, "relevante confirmado"),  # fronteira: limite inferior igual ao mínimo
    (0.15, 0.02, 0.30, "positivo, estimativa acima do mínimo"),
    (0.05, 0.01, 0.08, "positivo, abaixo do mínimo"),
    (0.02, -0.05, 0.08, "relevante descartado"),
    (0.12, -0.03, 0.25, "inconclusivo"),
    (0.05, 0.01, 0.12, "inconclusivo"),
])
def test_classificacao_segue_a_decisao_e(ganho, inf, sup, esperado):
    assert simulacao.classificar(ganho, inf, sup) == esperado


def test_ganho_verdadeiro_e_nulo_sem_sinal_e_positivo_com_sinal():
    rng = np.random.default_rng(6)
    sem = Cenario(n_cabrucas=10, sinal_temporal=0.0)
    com = Cenario(n_cabrucas=10, sinal_temporal=0.4, ruido_dinamica=0.2)
    g_sem = simulacao.ganho_verdadeiro(sem, simulacao.sortear_comunidade(sem, rng), rng, n=2000)
    g_com = simulacao.ganho_verdadeiro(com, simulacao.sortear_comunidade(com, rng), rng, n=2000, treinos=30)
    assert abs(g_sem["populacao_mae"]) < 0.01 and g_com["populacao_mae"] > 0.1
    assert g_com["populacao_mse"] > g_com["populacao_mae"]  # MSE ganha mais que MAE
    # com 10 propriedades o modelo maior paga pelo parâmetro extra: o ganho alcançável é menor
    assert g_com["alcancavel_mae"] < g_com["populacao_mae"]


def test_com_muitas_propriedades_e_sinal_forte_o_ganho_e_confirmado():
    c = Cenario(n_cabrucas=150, sinal_estavel=0.2, sinal_paisagem=0.1, sinal_temporal=0.6, ruido_dinamica=0.2)
    res = simulacao.rodar(c, repeticoes=3, semente=4, n_perm=0, treinos=0)
    assert (res["resultado"] == "relevante confirmado").all()
    assert (res["metodo"] == simulacao.METODO_ADOTADO).all()


def test_sem_sinal_temporal_o_ganho_raramente_parece_positivo():
    c = Cenario(n_cabrucas=30, sinal_temporal=0.0)
    res = simulacao.rodar(c, repeticoes=40, semente=5, n_boot=100, treinos=0)
    assert (res["ic_inferior"] > 0).mean() <= 0.10
    assert (res["p_permutacao"] <= 0.05).mean() <= 0.15


# --- Métodos de inferência -------------------------------------------------------------------------

def test_ridge_ponderado_equivale_a_repetir_linhas():
    rng = np.random.default_rng(7)
    x, y = rng.standard_normal((12, 3)), rng.standard_normal(12)
    contagem = np.array([0, 1, 2, 3, 0, 1, 1, 2, 0, 1, 1, 1])
    repetido = np.repeat(np.arange(12), contagem)
    esperado = _ridge_independente(x[repetido], y[repetido], x, 1.0)
    obtido = simulacao._ridge_ponderado(x, y, contagem[None], 1.0)[0]
    assert obtido == pytest.approx(esperado, abs=1e-10)


def test_previsoes_sem_grupo_retiram_o_grupo_inteiro():
    rng = np.random.default_rng(8)
    x, y = rng.standard_normal((9, 2)), rng.standard_normal(9)
    grupos = np.array([0, 0, 1, 1, 1, 2, 3, 3, 4])
    contagens = np.array([[1, 1, 2, 2, 2, 0, 1, 1, 3], [1] * 9])
    obtido = simulacao.previsoes_sem_grupo(x, y, grupos, 1.0, contagens)
    for b, cont in enumerate(contagens):
        for i in range(9):
            treino = np.repeat(np.flatnonzero(grupos != grupos[i]), cont[grupos != grupos[i]])
            assert obtido[b, i] == pytest.approx(_ridge_independente(x[treino], y[treino], x[i:i + 1], 1.0)[0])


def _dados(n, sinal, semente):
    c = Cenario(n_cabrucas=n, sinal_estavel=0.2, sinal_paisagem=0.1, sinal_temporal=sinal, ruido_dinamica=0.2)
    return simulacao.simular_dados(c, np.random.default_rng(semente))


def test_intervalo_reajuste_exclui_zero_com_sinal_forte_e_inclui_sem_sinal():
    rng = np.random.default_rng(9)
    forte, nulo = _dados(60, 0.6, 10), _dados(60, 0.0, 11)
    for tipo in ("percentil", "basico"):
        inf, sup = simulacao.intervalo_reajuste(forte, np.arange(60), 1.0, rng, n_boot=200)[tipo]
        assert 0 < inf < sup
        inf, sup = simulacao.intervalo_reajuste(nulo, np.arange(60), 1.0, rng, n_boot=200)[tipo]
        assert inf < 0 < sup


def test_intervalo_basico_reflete_o_percentil_em_torno_do_ganho_loo():
    dados = _dados(30, 0.4, 19)
    r = simulacao.intervalo_reajuste(dados, np.arange(30), 1.0, np.random.default_rng(2), n_boot=100)
    loo = {m: simulacao.erros_deixando_um_fora(dados, simulacao.MODELOS[m], 1.0) for m in ("M2b", "M3")}
    ganho = 1 - loo["M3"].mean() / loo["M2b"].mean()
    assert r["basico"] == pytest.approx((2 * ganho - r["percentil"][1], 2 * ganho - r["percentil"][0]))


def test_intervalo_reajuste_reamostra_grupos_e_nao_linhas():
    # duas cópias de cada propriedade: tratadas como grupos, o intervalo não encolhe como se n dobrasse
    dados = _dados(30, 0.4, 12)
    dobrado = pd.concat([dados, dados], ignore_index=True)
    inf1, sup1 = simulacao.intervalo_reajuste(dados, np.arange(30), 1.0, np.random.default_rng(1),
                                              n_boot=300)["percentil"]
    inf2, sup2 = simulacao.intervalo_reajuste(dobrado, np.tile(np.arange(30), 2), 1.0, np.random.default_rng(1),
                                              n_boot=300)["percentil"]
    assert sup2 - inf2 == pytest.approx(sup1 - inf1, rel=0.25)


def test_permutacao_por_grupo_troca_grupos_inteiros():
    valores = np.array([1.0, 1.0, 2.0, 2.0, 3.0, 3.0, 9.0])
    grupos = np.array([0, 0, 1, 1, 2, 2, 3])
    saida = simulacao._permutar_por_grupo(valores, grupos, np.random.default_rng(3))
    assert saida[6] == 9.0  # grupo de tamanho único não troca com ninguém
    for g in range(3):
        assert len(set(saida[grupos == g])) == 1
    assert sorted(saida[:6]) == sorted(valores[:6])


def test_intervalo_cv_corrigido_contem_a_estimativa_e_responde_ao_sinal():
    rng = np.random.default_rng(13)
    est, inf, sup = simulacao.intervalo_cv_corrigido(_dados(60, 0.6, 14), np.arange(60), 1.0, rng)
    assert 0 < inf < est < sup
    est, inf, sup = simulacao.intervalo_cv_corrigido(_dados(60, 0.0, 15), np.arange(60), 1.0, rng)
    assert inf < 0 < sup


def test_permutacao_rejeita_com_sinal_forte_e_nao_sem_sinal():
    rng = np.random.default_rng(16)
    assert simulacao.teste_permutacao(_dados(40, 0.6, 17), np.arange(40), 1.0, rng, n_perm=99) == 0.01
    assert simulacao.teste_permutacao(_dados(40, 0.0, 18), np.arange(40), 1.0, rng, n_perm=99) > 0.05


# --- Suposições menos otimistas ----------------------------------------------------------------------

def test_correlacao_entre_dossel_e_dinamica():
    c = Cenario(n_cabrucas=2000, correlacao_estavel_dinamica=0.8, ruido_dinamica=0.1, ruido_mediana=0.1)
    dados = simulacao.simular_dados(c, np.random.default_rng(20))
    assert dados["dinamica"].corr(dados["estavel_mediana"]) == pytest.approx(0.8 / (1 + 0.01), abs=0.05)


def test_lacunas_opticas_zeram_e_degradam_a_dinamica():
    c = Cenario(n_cabrucas=4000, frac_sem_dinamica=0.3, frac_dinamica_degradada=0.3, fator_degradacao=3.0,
                ruido_dinamica=0.5)
    dados = simulacao.simular_dados(c, np.random.default_rng(21))
    assert (dados["dinamica"] == 0).mean() == pytest.approx(0.3, abs=0.03)
    # variância observada: 0,3·0 + 0,3·(1 + 1,5²) + 0,4·(1 + 0,5²)
    assert dados["dinamica"].var() == pytest.approx(0.3 * 3.25 + 0.4 * 1.25, rel=0.1)


def test_vizinhos_formam_grupos_e_compartilham_paisagem():
    c = Cenario(n_cabrucas=2000, tamanho_vizinhanca=2, correlacao_vizinhos=0.6, ruido_paisagem=0.0)
    dados = simulacao.simular_dados(c, np.random.default_rng(22))
    assert (dados["grupo"].value_counts() == 2).all()
    pares = dados.groupby("grupo")["paisagem"].agg(["first", "last"])
    assert pares["first"].corr(pares["last"]) == pytest.approx(0.6, abs=0.06)


def test_referencia_b2_exclui_as_matas_da_vizinhanca_retida():
    c = Cenario(n_cabrucas=20, referencia="B2", n_matas=5)
    dados = simulacao.simular_dados(c, np.random.default_rng(23))
    nenhum = np.zeros((1, 20), bool)
    assert simulacao.respostas(dados, nenhum)[0] == pytest.approx(dados["resposta"].to_numpy())
    linha = dados.attrs["linha_da_mata"][0]
    retido = np.zeros((1, 20), bool)
    retido[0, linha] = True
    ref = dados.attrs["matas"][dados.attrs["linha_da_mata"] != linha].any(axis=0)
    esperado = [simulacao._jaccard_distancia(lst, ref) for lst in dados.attrs["listas"]]
    assert simulacao.respostas(dados, retido)[0] == pytest.approx(esperado)


def test_rodar_com_todas_as_suposicoes_menos_otimistas():
    c = Cenario(n_cabrucas=20, correlacao_estavel_dinamica=0.5, frac_sem_dinamica=0.05,
                frac_dinamica_degradada=0.25, tamanho_vizinhanca=2, correlacao_vizinhos=0.5, referencia="B2")
    res = simulacao.rodar(c, repeticoes=2, semente=24, n_boot=50, n_perm=19, treinos=5)
    assert res[["ic_inferior", "ic_superior", "p_permutacao", "ganho_alcancavel"]].notna().all().all()
