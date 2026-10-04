"""Simulação para dimensionar o número de cabrucas (desenho analítico, seção 9).

Gera propriedades com uma condição ecológica latente, comunidades de aves,
detecção imperfeita, erro do reconhecedor e descritores ópticos com ruído;
calcula a resposta (distância de Jaccard até a referência formada por matas
independentes, decisão B1) e aplica a análise principal do desenho: ridge
com predições deixando uma propriedade de fora e ganho de M3 sobre M2b.

O intervalo do ganho é calculado por vários métodos, para medir a cobertura
de cada um contra dois estimandos: o ganho de população (modelo ajustado com
muitas propriedades) e o ganho alcançável com o n do estudo (modelo ajustado
com n propriedades, avaliado em propriedades novas). A leitura do intervalo
segue a decisão E (ganho mínimo relevante de 10% do MAE).

Os resultados valem para as suposições do `Cenario`. Elas não foram medidas
em cabruca; as que vêm do piloto ou da literatura estão indicadas.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import NormalDist

import numpy as np
import pandas as pd

GANHO_MINIMO = 0.10  # decisão E
NIVEL = 0.90


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
    """O "mundo" de uma repetição: parâmetros das espécies e lista de referência.

    É compartilhado pela amostra e pelos ganhos de referência, para que todos
    meçam a distância até as mesmas matas (decisão B1: conjunto fixo de matas).
    """
    inclinacao: np.ndarray
    intercepto: np.ndarray
    p_det: np.ndarray
    referencia: np.ndarray


def _listas(c: Cenario, especies: dict[str, np.ndarray], condicoes: np.ndarray,
            rng: np.random.Generator) -> np.ndarray:
    """Listas observadas (propriedade × espécie): presença, detecção e erro do reconhecedor."""
    psi = 1 / (1 + np.exp(-(especies["intercepto"] + np.outer(condicoes, especies["inclinacao"]))))
    presente = rng.random(psi.shape) < psi
    detectada = presente & (rng.random(psi.shape) < especies["p_det"])
    falsa = ~presente & (rng.random(psi.shape) < c.falso_positivo)
    return detectada | falsa


def sortear_comunidade(c: Cenario, rng: np.random.Generator) -> Comunidade:
    k = c.n_especies
    florestal = np.arange(k) < int(c.frac_florestais * k)
    especies = {
        "inclinacao": np.where(florestal, rng.uniform(0.8, 1.5, k), rng.uniform(-0.5, 0.3, k)),
        "intercepto": np.where(florestal, rng.normal(-0.5, 1.0, k), rng.normal(0.5, 1.0, k)),
    }
    p_min = np.exp(rng.uniform(np.log(c.p_minuto[0]), np.log(c.p_minuto[1]), k))
    especies["p_det"] = 1 - (1 - p_min * c.sensibilidade) ** c.minutos
    condicao_matas = c.condicao_matas + 0.3 * rng.standard_normal(c.n_matas)
    referencia = _listas(c, especies, condicao_matas, rng).any(axis=0)
    return Comunidade(**especies, referencia=referencia)


def simular_dados(c: Cenario, rng: np.random.Generator, comunidade: Comunidade | None = None,
                  n: int | None = None) -> pd.DataFrame:
    """Uma amostra de propriedades com resposta e preditores observados.

    Sem `comunidade`, sorteia uma nova; `n` substitui `c.n_cabrucas` (usado nos ganhos de referência).
    """
    n = n or c.n_cabrucas
    com = comunidade or sortear_comunidade(c, rng)
    s, l, d, e = rng.standard_normal((4, n))
    residuo = 1.0 - c.sinal_estavel - c.sinal_paisagem - c.sinal_temporal
    if residuo < 0:
        raise ValueError("as frações de sinal somam mais que 1")
    condicao = (np.sqrt(c.sinal_estavel) * s + np.sqrt(c.sinal_paisagem) * l
                + np.sqrt(c.sinal_temporal) * d + np.sqrt(residuo) * e)
    especies = {"intercepto": com.intercepto, "inclinacao": com.inclinacao, "p_det": com.p_det}
    resposta = np.array([_jaccard_distancia(lst, com.referencia) for lst in _listas(c, especies, condicao, rng)])

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


# --- Ajuste ---------------------------------------------------------------------------------------

def _ridge_ponderado(x: np.ndarray, y: np.ndarray, pesos: np.ndarray, lam: float) -> np.ndarray:
    """Ajusta m ridges de uma vez e prevê todas as n linhas com cada um.

    `x` (n, p) ou (m, n, p); `y` (n,) ou (m, n); `pesos` (m, n), o número de
    vezes que cada linha entra no treino de cada ajuste (0 = fora do treino).
    Padronização e média da resposta vêm só das linhas de treino, ponderadas;
    com pesos inteiros, equivale a repetir as linhas.
    """
    w = pesos.astype(float)
    soma = w.sum(axis=1)
    x = np.broadcast_to(x, (w.shape[0], *x.shape[-2:]))
    y = np.broadcast_to(y, w.shape)
    media = np.einsum("mn,mnp->mp", w, x) / soma[:, None]
    dp = np.sqrt(np.einsum("mn,mnp->mp", w, (x - media[:, None]) ** 2) / soma[:, None])
    dp[dp == 0] = 1.0
    z = (x - media[:, None]) / dp[:, None]
    ym = (w * y).sum(axis=1) / soma
    a = np.einsum("mnp,mn,mnq->mpq", z, w, z) + lam * np.eye(z.shape[2])
    b = np.einsum("mnp,mn->mp", z, w * (y - ym[:, None]))
    beta = np.linalg.solve(a, b[..., None])[..., 0]
    return ym[:, None] + np.einsum("mnp,mp->mn", z, beta)


def _ridge_prever(x_treino, y_treino, x_teste, lam: float) -> np.ndarray:
    """Um ridge ajustado no treino, previsto no teste."""
    x = np.vstack([x_treino, x_teste])
    y = np.concatenate([y_treino, np.zeros(len(x_teste))])
    pesos = np.concatenate([np.ones(len(x_treino)), np.zeros(len(x_teste))])[None]
    return _ridge_ponderado(x, y, pesos, lam)[0, len(x_treino):]


def previsoes_sem_grupo(x: np.ndarray, y: np.ndarray, grupos: np.ndarray, lam: float,
                        contagens: np.ndarray | None = None) -> np.ndarray:
    """Previsão de cada linha por um modelo ajustado sem o grupo dela.

    `grupos` identifica as unidades que saem juntas (propriedade, ou vizinhas).
    `contagens` (B, n) são pesos de reamostragem; sem elas, B = 1. Devolve (B, n).
    """
    n = len(y)
    _, idx = np.unique(grupos, return_inverse=True)
    k = idx.max() + 1
    fora = idx[None, :] != np.arange(k)[:, None]  # (k, n): treino de cada dobra
    cont = np.ones((1, n)) if contagens is None else contagens
    bloco = max(1, 400_000 // (k * n))  # limita a memória dos ajustes simultâneos
    partes = []
    for i in range(0, len(cont), bloco):
        c = cont[i:i + bloco]
        pesos = (c[:, None, :] * fora[None]).reshape(-1, n)
        previsto = _ridge_ponderado(x, y, pesos, lam).reshape(len(c), k, n)
        partes.append(previsto[:, idx, np.arange(n)])
    return np.concatenate(partes)


def erros_deixando_um_fora(dados: pd.DataFrame, colunas: list[str], lam: float) -> np.ndarray:
    """Erro absoluto de cada propriedade, prevista por um modelo ajustado sem ela."""
    x, y = dados[colunas].to_numpy(), dados["resposta"].to_numpy()
    return np.abs(previsoes_sem_grupo(x, y, np.arange(len(y)), lam)[0] - y)


def _ganho(erros_base: np.ndarray, erros_maior: np.ndarray, pesos: np.ndarray | None = None) -> np.ndarray:
    """1 − MAE_maior/MAE_base, ao longo do último eixo (ponderado, se houver pesos)."""
    if pesos is None:
        return 1 - erros_maior.mean(axis=-1) / erros_base.mean(axis=-1)
    return 1 - (pesos * erros_maior).sum(axis=-1) / (pesos * erros_base).sum(axis=-1)


# --- Métodos de intervalo para o ganho de M3 sobre M2b ------------------------------------------

def ganho_com_intervalo(erros_base: np.ndarray, erros_maior: np.ndarray, rng: np.random.Generator,
                        n_boot: int = 1000, nivel: float = NIVEL) -> tuple[float, float, float]:
    """Método original do desenho: reamostragem pareada dos erros deixando um fora.

    Os erros são tratados como fixos e independentes; a simulação mostrou que
    o intervalo sai estreito demais. Mantido só para comparação.
    """
    idx = rng.integers(0, len(erros_base), (n_boot, len(erros_base)))
    boot = _ganho(erros_base[idx], erros_maior[idx])
    alfa = (1 - nivel) / 2
    return float(_ganho(erros_base, erros_maior)), float(np.quantile(boot, alfa)), float(np.quantile(boot, 1 - alfa))


def _xy(dados: pd.DataFrame, modelo: str) -> tuple[np.ndarray, np.ndarray]:
    return dados[MODELOS[modelo]].to_numpy(), dados["resposta"].to_numpy()


def intervalo_reajuste(dados: pd.DataFrame, grupos: np.ndarray, lam: float, rng: np.random.Generator,
                       n_boot: int = 200, nivel: float = NIVEL) -> dict[str, tuple[float, float] | float]:
    """Reamostragem de grupos de propriedades que reajusta os modelos a cada réplica.

    Cada réplica sorteia grupos com reposição e refaz a validação por grupo
    retido dentro dela (cópias do grupo retido saem juntas do treino, para não
    haver vazamento). Como as cópias não trazem informação nova, cada réplica
    treina com cerca de 63% de propriedades distintas, e a distribuição sai
    deslocada para baixo em relação ao ganho por LOO. Devolve:

    - "percentil": quantis da distribuição das réplicas;
    - "basico": 2·ganho_LOO − quantis, que desconta esse deslocamento;
    - "media_reamostras": média das réplicas, para medir o deslocamento.
    """
    rotulos, idx = np.unique(grupos, return_inverse=True)
    sorteio = rng.integers(0, len(rotulos), (n_boot, len(rotulos)))
    contagens = np.stack([np.bincount(s, minlength=len(rotulos)) for s in sorteio])[:, idx]
    erros, erros_loo = {}, {}
    for m in ("M2b", "M3"):
        x, y = _xy(dados, m)
        erros[m] = np.abs(previsoes_sem_grupo(x, y, grupos, lam, contagens) - y)
        erros_loo[m] = np.abs(previsoes_sem_grupo(x, y, grupos, lam)[0] - y)
    with np.errstate(invalid="ignore", divide="ignore"):  # réplica degenerada (um só grupo) vira NaN
        boot = _ganho(erros["M2b"], erros["M3"], contagens)
    ganho = float(_ganho(erros_loo["M2b"], erros_loo["M3"]))
    alfa = (1 - nivel) / 2
    q_inf, q_sup = float(np.nanquantile(boot, alfa)), float(np.nanquantile(boot, 1 - alfa))
    return {"percentil": (q_inf, q_sup), "basico": (2 * ganho - q_sup, 2 * ganho - q_inf),
            "media_reamostras": float(np.nanmean(boot))}


def intervalo_cv_corrigido(dados: pd.DataFrame, grupos: np.ndarray, lam: float, rng: np.random.Generator,
                           k: int = 5, repeticoes: int = 20, nivel: float = NIVEL) -> tuple[float, float, float]:
    """Validação cruzada em k dobras de grupos, repetida, com correção de variância.

    O ganho é r = média(D)/média(B), com D = MAE(M2b) − MAE(M3) e B = MAE(M2b)
    em cada dobra. A variância de r vem do método delta sobre os pares (D, B)
    das dobras, multiplicada pela correção de Nadeau & Bengio (2003) na forma
    de Bouckaert & Frank (2004), (1/J + n_teste/n_treino), que compensa a
    sobreposição dos treinos (J = k·r dobras; n_teste/n_treino observado, para
    dobras desiguais). Usa o quantil normal: com J = 100, difere do t em menos
    de 1%. Devolve (estimativa, inferior, superior).
    """
    rotulos, idx = np.unique(grupos, return_inverse=True)
    n_grupos = len(rotulos)
    teste = []
    for _ in range(repeticoes):
        dobra_linha = rng.permutation(np.arange(n_grupos) % k)[idx]
        teste.extend(dobra_linha == f for f in range(k))
    teste = np.array(teste)
    mae = {}
    for m in ("M2b", "M3"):
        x, y = _xy(dados, m)
        err = np.abs(_ridge_ponderado(x, y, ~teste, lam) - y)
        mae[m] = (err * teste).sum(axis=1) / teste.sum(axis=1)
    d, b = mae["M2b"] - mae["M3"], mae["M2b"]
    r = d.mean() / b.mean()
    u = (d - r * b) / b.mean()  # linearização da razão (método delta)
    n_teste = teste.sum(axis=1)
    correcao = 1 / len(d) + np.mean(n_teste / (len(idx) - n_teste))
    se = np.sqrt(correcao * u.var(ddof=1))
    z = NormalDist().inv_cdf(1 - (1 - nivel) / 2)
    return float(r), float(r - z * se), float(r + z * se)


def _permutar_por_grupo(valores: np.ndarray, grupos: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Troca os valores de grupos inteiros entre grupos do mesmo tamanho."""
    rotulos, idx, tamanhos = np.unique(grupos, return_inverse=True, return_counts=True)
    saida = valores.copy()
    for tam in np.unique(tamanhos):
        mesmos = np.flatnonzero(tamanhos == tam)
        for destino, origem in zip(mesmos, rng.permutation(mesmos)):
            saida[idx == destino] = valores[idx == origem]
    return saida


def teste_permutacao(dados: pd.DataFrame, grupos: np.ndarray, lam: float, rng: np.random.Generator,
                     n_perm: int = 199) -> float:
    """Valor-p unilateral para "M3 ganha de M2b": permuta o descritor de dinâmica entre grupos.

    Testa só se o ganho é maior que zero; não dá intervalo. Grupos inteiros
    trocam de valor entre si (só entre grupos do mesmo tamanho). Se a dinâmica
    for correlacionada com outros preditores, a permutação quebra essa
    correlação e a hipótese nula testada passa a ser "dinâmica é ruído puro".
    """
    x2b, y = _xy(dados, "M2b")
    x3 = dados[MODELOS["M3"]].to_numpy()
    e2b = np.abs(previsoes_sem_grupo(x2b, y, grupos, lam)[0] - y)
    observado = _ganho(e2b, np.abs(previsoes_sem_grupo(x3, y, grupos, lam)[0] - y))
    col = MODELOS["M3"].index("dinamica")
    n = len(y)
    perm = np.repeat(x3[None], n_perm, axis=0)
    if len(np.unique(grupos)) == n:
        perm[:, :, col] = x3[np.argsort(rng.random((n_perm, n)), axis=1), col]
    else:
        for i in range(n_perm):
            perm[i, :, col] = _permutar_por_grupo(x3[:, col], grupos, rng)
    _, idx = np.unique(grupos, return_inverse=True)
    k = idx.max() + 1
    fora = (idx[None, :] != np.arange(k)[:, None]).astype(float)  # (k, n)
    xs = np.repeat(perm, k, axis=0)  # (n_perm·k, n, p)
    previsto = _ridge_ponderado(xs, y, np.tile(fora, (n_perm, 1)), lam).reshape(n_perm, k, n)[:, idx, np.arange(n)]
    ganhos = _ganho(e2b, np.abs(previsto - y))
    return float((1 + (ganhos >= observado).sum()) / (1 + n_perm))


METODOS = ["erros_fixos", "reajuste", "reajuste_basico", "cv_corrigido"]
# Adotado em 2026-10-04: cobertura do IC90 mais próxima de 90% contra o ganho alcançável nos
# cenários da simulação (docs/simulacao-dimensionamento.md). Na análise real, usar n_boot >= 2000.
METODO_ADOTADO = "reajuste_basico"


# --- Leitura do intervalo (decisão E) -------------------------------------------------------------

CATEGORIAS = ["relevante confirmado", "positivo, estimativa acima do mínimo", "positivo, abaixo do mínimo",
              "inconclusivo", "relevante descartado"]


def classificar(ganho: float, inferior: float, superior: float, minimo: float = GANHO_MINIMO) -> str:
    """Leitura do intervalo frente à decisão E (ganho mínimo relevante).

    "relevante confirmado": o intervalo inteiro está acima do mínimo. "positivo,
    estimativa acima do mínimo": o intervalo exclui zero e a estimativa passa
    do mínimo, mas o intervalo ainda admite um ganho irrelevante. "positivo,
    abaixo do mínimo": há ganho, mas o intervalo inteiro fica abaixo do mínimo.
    "relevante descartado": o intervalo fica abaixo do mínimo e inclui zero.
    "inconclusivo": o intervalo inclui zero e o mínimo, ou exclui zero com a
    estimativa abaixo do mínimo e o limite superior acima dele.
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


# --- Ganhos de referência (estimandos) ------------------------------------------------------------

def ganho_verdadeiro(c: Cenario, comunidade: Comunidade, rng: np.random.Generator,
                     n: int = 4000, treinos: int = 0) -> dict[str, float]:
    """Ganhos de M3 sobre M2b no mesmo mundo, medidos numa amostra de teste de tamanho `n`.

    - populacao_mae, populacao_mse: modelos ajustados numa amostra de treino de tamanho `n`;
    - alcancavel_mae (se `treinos` > 0): modelos ajustados em `treinos` amostras de
      `c.n_cabrucas` propriedades; razão entre os MAE médios.
    """
    teste = simular_dados(c, rng, comunidade, n)
    treino = simular_dados(c, rng, comunidade, n)
    erros = {}
    for m in ("M2b", "M3"):
        x, y = _xy(treino, m)
        erros[m] = _ridge_prever(x, y, teste[MODELOS[m]].to_numpy(), c.lambda_ridge) - teste["resposta"].to_numpy()
    out = {"populacao_mae": float(1 - np.abs(erros["M3"]).mean() / np.abs(erros["M2b"]).mean()),
           "populacao_mse": float(1 - (erros["M3"] ** 2).mean() / (erros["M2b"] ** 2).mean())}
    if treinos:
        mae = {"M2b": 0.0, "M3": 0.0}
        for _ in range(treinos):
            amostra = simular_dados(c, rng, comunidade)
            for m in mae:
                x, y = _xy(amostra, m)
                prev = _ridge_prever(x, y, teste[MODELOS[m]].to_numpy(), c.lambda_ridge)
                mae[m] += np.abs(prev - teste["resposta"].to_numpy()).mean()
        out["alcancavel_mae"] = float(1 - mae["M3"] / mae["M2b"])
    return out


def rodar(c: Cenario, repeticoes: int, semente: int, metodo: str = METODO_ADOTADO, n_boot: int = 200,
          n_perm: int = 199, treinos: int = 100) -> pd.DataFrame:
    """Uma linha por repetição: MAEs, ganho de M3 sobre M2b, intervalos de cada método e classificação.

    `metodo` é o método cujo intervalo vai para a classificação da decisão E.
    `n_perm` = 0 pula o teste de permutação; `treinos` = 0 pula o ganho alcançável.
    """
    rng = np.random.default_rng(semente)
    linhas = []
    for r in range(repeticoes):
        comunidade = sortear_comunidade(c, rng)
        dados = simular_dados(c, rng, comunidade)
        grupos = np.arange(len(dados))
        verdadeiro = ganho_verdadeiro(c, comunidade, rng, treinos=treinos)
        erros = {m: erros_deixando_um_fora(dados, cols, c.lambda_ridge) for m, cols in MODELOS.items()}
        ganho, inf_f, sup_f = ganho_com_intervalo(erros["M2b"], erros["M3"], rng)
        reaj = intervalo_reajuste(dados, grupos, c.lambda_ridge, rng, n_boot)
        est_cv, inf_cv, sup_cv = intervalo_cv_corrigido(dados, grupos, c.lambda_ridge, rng)
        ics = {"erros_fixos": (ganho, inf_f, sup_f), "reajuste": (ganho, *reaj["percentil"]),
               "reajuste_basico": (ganho, *reaj["basico"]), "cv_corrigido": (est_cv, inf_cv, sup_cv)}
        alcancavel = verdadeiro.get("alcancavel_mae", np.nan)
        linha = {"repeticao": r, **{f"mae_{m}": e.mean() for m, e in erros.items()},
                 "dp_resposta": dados["resposta"].std(), "ganho_m3_m2b": ganho, "ganho_cv": est_cv,
                 "media_reamostras": reaj["media_reamostras"],
                 "ganho_verdadeiro": verdadeiro["populacao_mae"],
                 "ganho_verdadeiro_mse": verdadeiro["populacao_mse"],
                 "ganho_alcancavel": alcancavel}
        for nome, (_, inf, sup) in ics.items():
            linha |= {f"ic_inferior_{nome}": inf, f"ic_superior_{nome}": sup,
                      f"cobre_populacao_{nome}": inf <= verdadeiro["populacao_mae"] <= sup,
                      f"cobre_alcancavel_{nome}": (inf <= alcancavel <= sup) if treinos else np.nan}
        if n_perm:
            linha["p_permutacao"] = teste_permutacao(dados, grupos, c.lambda_ridge, rng, n_perm)
        est, inf, sup = ics[metodo]
        linha |= {"metodo": metodo, "ic_inferior": inf, "ic_superior": sup, "resultado": classificar(est, inf, sup)}
        linhas.append(linha)
    return pd.DataFrame(linhas).assign(**{k: (str(v) if isinstance(v, tuple) else v) for k, v in asdict(c).items()})
