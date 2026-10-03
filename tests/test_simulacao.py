import numpy as np
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
    g_com = simulacao.ganho_verdadeiro(com, simulacao.sortear_comunidade(com, rng), rng, n=2000)
    assert abs(g_sem[0]) < 0.01 and g_com[0] > 0.1 and g_com[1] > g_com[0]  # MSE ganha mais que MAE


def test_com_muitas_propriedades_e_sinal_forte_o_ganho_e_confirmado():
    c = Cenario(n_cabrucas=150, sinal_estavel=0.2, sinal_paisagem=0.1, sinal_temporal=0.6, ruido_dinamica=0.2)
    res = simulacao.rodar(c, repeticoes=3, semente=4)
    assert (res["resultado"] == "relevante confirmado").all()


def test_sem_sinal_temporal_o_ganho_raramente_parece_positivo():
    c = Cenario(n_cabrucas=30, sinal_temporal=0.0)
    res = simulacao.rodar(c, repeticoes=60, semente=5)
    assert (res["ic_inferior"] > 0).mean() <= 0.10
