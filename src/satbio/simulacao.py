"""Simulação para dimensionar o número de cabrucas (desenho analítico, seção 9).

Gera propriedades com uma condição ecológica latente, comunidades de aves,
detecção imperfeita, erro do reconhecedor e descritores ópticos com ruído;
calcula a resposta (distância de Jaccard até a referência formada por matas
independentes, decisão B1) e aplica a análise principal do desenho: ridge
com predições deixando uma propriedade de fora, ganho de M3 sobre M2b e
classificação pela decisão E (ganho mínimo relevante de 10% do MAE).

Os resultados valem para as suposições do `Cenario`. Elas não foram medidas
em cabruca; as que vêm do piloto ou da literatura estão indicadas.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

GANHO_MINIMO = 0.10  # decisão E


@dataclass(frozen=True)
class Cenario:
    n_cabrucas: int
    # Fração da variância da condição ecológica latente explicada por cada fonte.
    sinal_estavel: float = 0.30  # estado médio do dossel (mediana anual)
    sinal_paisagem: float = 0.20  # cobertura nativa no entorno
    sinal_temporal: float = 0.15  # dinâmica (amplitude, mudança): o que H2 testa
    n_matas: int = 5
    condicao_matas: float = 2.0  # condição das matas, em desvios-padrão acima da média das cabrucas
    # Comunidade: 140 espécies, metade florestais (Oliveira et al. 2026: 139 espécies, 73 florestais).
    n_especies: int = 140
    frac_florestais: float = 0.5
    # Detecção: minutos por propriedade × campanha (protocolo inicial, 1 ponto: 252 min) e
    # probabilidade de vocalizar e ser gravada por minuto, por espécie presente, sorteada
    # log-uniforme no intervalo (muitas espécies raras, como em curvas de acumulação acústica).
    minutos: int = 252
    p_minuto: tuple[float, float] = (0.0005, 0.03)
    sensibilidade: float = 0.8  # fração das vocalizações gravadas que o reconhecedor acerta
    falso_positivo: float = 0.01  # chance de uma espécie ausente entrar na lista por erro
    # Ruído dos descritores ópticos, em desvios-padrão do sinal verdadeiro.
    ruido_recente: float = 1.0  # uma composição só (M1/M2)
    ruido_mediana: float = 0.3  # mediana de um ano (M2b)
    ruido_dinamica: float = 0.7  # amplitude/mudança, sensíveis a lacunas (M3)
    ruido_paisagem: float = 0.2
    lambda_ridge: float = 1.0


def _jaccard_distancia(lista: np.ndarray, referencia: np.ndarray) -> float:
    uniao = np.logical_or(lista, referencia).sum()
    return 1.0 - np.logical_and(lista, referencia).sum() / uniao if uniao else 0.0


@dataclass(frozen=True)
class Comunidade:
    """Parâmetros das espécies, sorteados uma vez e compartilhados pela amostra e pelo ganho verdadeiro."""
    inclinacao: np.ndarray
    intercepto: np.ndarray
    p_det: np.ndarray


def sortear_comunidade(c: Cenario, rng: np.random.Generator) -> Comunidade:
    k = c.n_especies
    florestal = np.arange(k) < int(c.frac_florestais * k)
    inclinacao = np.where(florestal, rng.uniform(0.8, 1.5, k), rng.uniform(-0.5, 0.3, k))
    intercepto = np.where(florestal, rng.normal(-0.5, 1.0, k), rng.normal(0.5, 1.0, k))
    p_min = np.exp(rng.uniform(np.log(c.p_minuto[0]), np.log(c.p_minuto[1]), k))
    return Comunidade(inclinacao, intercepto, 1 - (1 - p_min * c.sensibilidade) ** c.minutos)


def simular_dados(c: Cenario, rng: np.random.Generator, comunidade: Comunidade | None = None,
                  n: int | None = None) -> pd.DataFrame:
    """Uma amostra de propriedades com resposta e preditores observados.

    Sem `comunidade`, sorteia uma nova; `n` substitui `c.n_cabrucas` (usado no ganho verdadeiro).
    """
    n = n or c.n_cabrucas
    com = comunidade or sortear_comunidade(c, rng)
    s, l, d, e = rng.standard_normal((4, n))
    residuo = 1.0 - c.sinal_estavel - c.sinal_paisagem - c.sinal_temporal
    if residuo < 0:
        raise ValueError("as frações de sinal somam mais que 1")
    condicao = (np.sqrt(c.sinal_estavel) * s + np.sqrt(c.sinal_paisagem) * l
                + np.sqrt(c.sinal_temporal) * d + np.sqrt(residuo) * e)
    condicao_matas = c.condicao_matas + 0.3 * rng.standard_normal(c.n_matas)

    def listas(condicoes: np.ndarray) -> np.ndarray:
        psi = 1 / (1 + np.exp(-(com.intercepto + np.outer(condicoes, com.inclinacao))))
        presente = rng.random(psi.shape) < psi
        detectada = presente & (rng.random(psi.shape) < com.p_det)
        falsa = ~presente & (rng.random(psi.shape) < c.falso_positivo)
        return detectada | falsa

    referencia = listas(condicao_matas).any(axis=0)
    resposta = np.array([_jaccard_distancia(lst, referencia) for lst in listas(condicao)])

    return pd.DataFrame({
        "resposta": resposta,
        "estavel_recente": s + c.ruido_recente * rng.standard_normal(n),
        "estavel_mediana": s + c.ruido_mediana * rng.standard_normal(n),
        "dinamica": d + c.ruido_dinamica * rng.standard_normal(n),
        "paisagem": l + c.ruido_paisagem * rng.standard_normal(n),
    })


MODELOS = {
    "M2": ["estavel_recente", "paisagem"],
    "M2b": ["estavel_recente", "paisagem", "estavel_mediana"],
    "M3": ["estavel_recente", "paisagem", "estavel_mediana", "dinamica"],
}


def _ridge_prever(x_treino, y_treino, x_teste, lam: float) -> np.ndarray:
    media, dp = x_treino.mean(axis=0), x_treino.std(axis=0)
    dp[dp == 0] = 1.0
    zt, zs = (x_treino - media) / dp, (x_teste - media) / dp
    ym = y_treino.mean()
    beta = np.linalg.solve(zt.T @ zt + lam * np.eye(zt.shape[1]), zt.T @ (y_treino - ym))
    return ym + zs @ beta


def erros_deixando_um_fora(dados: pd.DataFrame, colunas: list[str], lam: float) -> np.ndarray:
    """Erro absoluto de cada propriedade, prevista por um modelo ajustado sem ela."""
    x, y = dados[colunas].to_numpy(), dados["resposta"].to_numpy()
    erros = np.empty(len(y))
    for i in range(len(y)):
        treino = np.arange(len(y)) != i
        erros[i] = abs(_ridge_prever(x[treino], y[treino], x[i:i + 1], lam)[0] - y[i])
    return erros


def ganho_com_intervalo(erros_base: np.ndarray, erros_maior: np.ndarray, rng: np.random.Generator,
                        n_boot: int = 1000, nivel: float = 0.90) -> tuple[float, float, float]:
    """Ganho relativo 1 − MAE_maior/MAE_base e intervalo por reamostragem pareada de propriedades."""
    ganho = 1 - erros_maior.mean() / erros_base.mean()
    idx = rng.integers(0, len(erros_base), (n_boot, len(erros_base)))
    boot = 1 - erros_maior[idx].mean(axis=1) / erros_base[idx].mean(axis=1)
    alfa = (1 - nivel) / 2
    return float(ganho), float(np.quantile(boot, alfa)), float(np.quantile(boot, 1 - alfa))


CATEGORIAS = ["relevante confirmado", "positivo, estimativa acima do mínimo", "positivo, abaixo do mínimo",
              "inconclusivo", "relevante descartado"]


def classificar(ganho: float, inferior: float, superior: float, minimo: float = GANHO_MINIMO) -> str:
    """Leitura do intervalo frente à decisão E (ganho mínimo relevante).

    "relevante confirmado": o intervalo inteiro está acima do mínimo. "positivo,
    estimativa acima do mínimo": o intervalo exclui zero e a estimativa passa
    do mínimo, mas o intervalo ainda admite um ganho irrelevante. "positivo,
    abaixo do mínimo": há ganho, mas o intervalo inteiro fica abaixo do mínimo.
    "relevante descartado": o intervalo fica abaixo do mínimo e inclui zero.
    Qual dessas leituras o estudo vai exigir é uma decisão do desenho.
    """
    if inferior >= minimo:
        return CATEGORIAS[0]
    if inferior > 0 and ganho >= minimo:
        return CATEGORIAS[1]
    if inferior > 0 and superior < minimo:
        return CATEGORIAS[2]
    if superior < minimo:
        return CATEGORIAS[4]
    return CATEGORIAS[3]


def ganho_verdadeiro(c: Cenario, comunidade: Comunidade, rng: np.random.Generator,
                     n: int = 4000) -> tuple[float, float]:
    """Ganho de M3 sobre M2b na população (mesma comunidade): (em MAE, em MSE).

    Ajusta numa amostra grande e mede o erro em outra, do mesmo tamanho.
    """
    treino = simular_dados(c, rng, comunidade, n)
    teste = simular_dados(c, rng, comunidade, n)
    erros = {}
    for m in ("M2b", "M3"):
        cols = MODELOS[m]
        pred = _ridge_prever(treino[cols].to_numpy(), treino["resposta"].to_numpy(), teste[cols].to_numpy(),
                             c.lambda_ridge)
        erros[m] = pred - teste["resposta"].to_numpy()
    mae = 1 - np.abs(erros["M3"]).mean() / np.abs(erros["M2b"]).mean()
    mse = 1 - (erros["M3"] ** 2).mean() / (erros["M2b"] ** 2).mean()
    return float(mae), float(mse)


def rodar(c: Cenario, repeticoes: int, semente: int) -> pd.DataFrame:
    """Uma linha por repetição: MAEs, ganho de M3 sobre M2b com intervalo e classificação."""
    rng = np.random.default_rng(semente)
    linhas = []
    for r in range(repeticoes):
        comunidade = sortear_comunidade(c, rng)
        dados = simular_dados(c, rng, comunidade)
        verdadeiro_mae, verdadeiro_mse = ganho_verdadeiro(c, comunidade, rng)
        erros = {m: erros_deixando_um_fora(dados, cols, c.lambda_ridge) for m, cols in MODELOS.items()}
        ganho, inf, sup = ganho_com_intervalo(erros["M2b"], erros["M3"], rng)
        linhas.append({"repeticao": r, **{f"mae_{m}": e.mean() for m, e in erros.items()},
                       "dp_resposta": dados["resposta"].std(), "ganho_m3_m2b": ganho,
                       "ic_inferior": inf, "ic_superior": sup,
                       "ganho_verdadeiro": verdadeiro_mae, "ganho_verdadeiro_mse": verdadeiro_mse,
                       "ic_cobre_verdadeiro": inf <= verdadeiro_mae <= sup,
                       "resultado": classificar(ganho, inf, sup)})
    return pd.DataFrame(linhas).assign(**{k: (str(v) if isinstance(v, tuple) else v) for k, v in asdict(c).items()})
