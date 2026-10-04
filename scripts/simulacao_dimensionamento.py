"""Simulação de dimensionamento: quantas cabrucas para avaliar o ganho temporal (H2)?

Uso:
    uv run python scripts/simulacao_dimensionamento.py [--repeticoes 500] [--permitir-sujo]

Cruza 10, 20 e 30 cabrucas com cenários calibrados pelo ganho verdadeiro de M3
sobre M2b (0%, 10%, 15% e 20% do MAE, medidos na mesma comunidade com uma
amostra grande). Em cada repetição calcula o intervalo do ganho por três
métodos e o teste de permutação, e mede a cobertura de cada intervalo contra
o ganho de população e contra o ganho alcançável com o n do estudo. Grava em
data/processed/simulacao/ (fora do git) as repetições, o resumo e um
manifesto; a figura (classificação pelo método adotado) vai para docs/img/.
Os resultados dependem das suposições de satbio.simulacao.Cenario.
"""

from __future__ import annotations

import argparse
import json
import platform
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from satbio import acustica, rastreio, simulacao  # noqa: E402
from satbio.simulacao import Cenario  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "data" / "processed" / "simulacao"
FIGURA = RAIZ / "docs" / "img" / "simulacao-dimensionamento.png"
N_CABRUCAS = [10, 20, 30]
# Cenários calibrados pelo ganho verdadeiro médio (em MAE): (sinal temporal, ruído do descritor de dinâmica).
# Ganhos acima de ~24% não são alcançáveis com dossel e paisagem explicando metade da variância.
CENARIOS = {"ganho 0%": (0.0, 0.7), "ganho ~10%": (0.30, 0.7), "ganho ~15%": (0.30, 0.4), "ganho ~20%": (0.45, 0.4)}
SEMENTE = 20261003
RESULTADOS = simulacao.CATEGORIAS
CORES = dict(zip(RESULTADOS, ["#1c5cab", "#86b6ef", "#eda100", "#a8a7a2", "#eb6834"]))


def figura(resumo: pd.DataFrame) -> None:
    plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#a8a7a2",
                         "text.color": "#0b0b0b", "axes.labelcolor": "#52514e", "xtick.color": "#52514e",
                         "ytick.color": "#52514e"})
    fig, eixos = plt.subplots(1, len(CENARIOS), figsize=(12, 3.9), sharey=True)
    for ax, rotulo in zip(eixos, CENARIOS):
        r = resumo[resumo["cenario"] == rotulo].set_index("n_cabrucas").loc[N_CABRUCAS]
        base = pd.Series(0.0, index=r.index)
        posicoes = list(range(len(N_CABRUCAS)))
        for res in RESULTADOS:
            barras = ax.bar(posicoes, r[res].to_numpy(), bottom=base.to_numpy(), color=CORES[res],
                            edgecolor="#fcfcfb", linewidth=2, width=0.6, label=res)
            for b, v, b0 in zip(barras, r[res], base):
                if v >= 0.06:
                    ax.text(b.get_x() + b.get_width() / 2, b0 + v / 2, f"{v:.0%}", ha="center", va="center",
                            fontsize=8.5, color="white" if res == RESULTADOS[0] else "#0b0b0b")
            base += r[res]
        real = r["ganho_verdadeiro_medio"].mean()
        ax.set_title(f"{rotulo} (real: {0.0 if abs(real) < 0.005 else real:.0%})", loc="left", fontsize=10,
                     fontweight="bold")
        ax.set_xticks(posicoes, [str(n) for n in N_CABRUCAS])
        ax.set_xlim(-0.6, len(N_CABRUCAS) - 0.4)
        ax.set_xlabel("cabrucas")
    eixos[0].set_ylabel("fração das simulações")
    eixos[0].set_yticks([0, 0.25, 0.5, 0.75, 1])
    eixos[0].set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    alcas, rotulos = eixos[0].get_legend_handles_labels()
    fig.legend(alcas, rotulos, loc="upper left", bbox_to_anchor=(0.01, 0.93), ncol=5, frameon=False, fontsize=9)
    fig.suptitle("O que a avaliação de M3 × M2b concluiria, por número de cabrucas", x=0.01, ha="left",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    FIGURA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURA, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _celula(args: tuple[int, int, str, float, float, int]) -> pd.DataFrame:
    i, n, rotulo, sinal, ruido, repeticoes = args
    c = Cenario(n_cabrucas=n, sinal_temporal=sinal, ruido_dinamica=ruido)
    return simulacao.rodar(c, repeticoes, SEMENTE + 100 * (i // len(CENARIOS)) + i % len(CENARIOS)).assign(
        cenario=rotulo)


def resumir(todas: pd.DataFrame) -> pd.DataFrame:
    g = todas.groupby(["n_cabrucas", "cenario"], sort=False)
    resumo = g.agg(ganho_verdadeiro_medio=("ganho_verdadeiro", "mean"),
                   ganho_verdadeiro_mse_medio=("ganho_verdadeiro_mse", "mean"),
                   ganho_alcancavel_medio=("ganho_alcancavel", "mean"),
                   ganho_estimado_medio=("ganho_m3_m2b", "mean"),
                   ganho_estimado_dp=("ganho_m3_m2b", "std"),
                   ic_inferior_acima_de_zero=("ic_inferior", lambda s: (s > 0).mean()),
                   rejeicao_permutacao_5pct=("p_permutacao", lambda p: (p <= 0.05).mean()),
                   mae_m2b_mediano=("mae_M2b", "median"))
    chave = [todas["n_cabrucas"], todas["cenario"]]
    for m in simulacao.METODOS:
        centro = (todas[f"ic_superior_{m}"] + todas[f"ic_inferior_{m}"]) / 2
        resumo[f"vies_centro_{m}"] = (centro - todas["ganho_alcancavel"]).groupby(chave, sort=False).mean()
        resumo[f"cobertura_alcancavel_{m}"] = g[f"cobre_alcancavel_{m}"].mean()
        resumo[f"cobertura_populacao_{m}"] = g[f"cobre_populacao_{m}"].mean()
        resumo[f"largura_mediana_{m}"] = (todas[f"ic_superior_{m}"] - todas[f"ic_inferior_{m}"]).groupby(
            [todas["n_cabrucas"], todas["cenario"]], sort=False).median()
    # erro de Monte Carlo da cobertura (binomial), igual para todos os métodos de uma célula
    resumo["ep_cobertura"] = np.sqrt(0.9 * 0.1 / g.size())
    return (resumo.join(pd.crosstab([todas["n_cabrucas"], todas["cenario"]], todas["resultado"], normalize="index")
                        .reindex(columns=RESULTADOS, fill_value=0.0))
            .reset_index())


def main(repeticoes: int, permitir_sujo: bool) -> None:
    codigo = rastreio.estado_do_codigo(RAIZ, SAIDA, permitir_sujo)
    tarefas = [(i * len(CENARIOS) + j, n, rotulo, sinal, ruido, repeticoes)
               for i, n in enumerate(N_CABRUCAS) for j, (rotulo, (sinal, ruido)) in enumerate(CENARIOS.items())]
    with ProcessPoolExecutor() as ex:
        partes = list(ex.map(_celula, tarefas))
    for res in partes:
        print(f"n={res['n_cabrucas'].iloc[0]:2d} {res['cenario'].iloc[0]:11s} "
              f"real={res['ganho_verdadeiro'].mean():.3f} alcançável={res['ganho_alcancavel'].mean():.3f} "
              + " ".join(f"{m}={res[f'cobre_alcancavel_{m}'].mean():.0%}" for m in simulacao.METODOS))
    todas = pd.concat(partes, ignore_index=True)
    todas["largura_ic"] = todas["ic_superior"] - todas["ic_inferior"]
    resumo = resumir(todas)
    print("\ncobertura geral do IC90 contra o ganho alcançável: " + ", ".join(
        f"{m} {todas[f'cobre_alcancavel_{m}'].mean():.1%}" for m in simulacao.METODOS))

    SAIDA.mkdir(parents=True, exist_ok=True)
    todas.to_csv(SAIDA / "repeticoes.csv", index=False)
    resumo.to_csv(SAIDA / "resumo.csv", index=False)
    figura(resumo)
    manifesto = {
        "executado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "codigo": codigo,
        "ambiente": {"python": platform.python_version(), "numpy": version("numpy"), "pandas": version("pandas")},
        "semente": SEMENTE,
        "repeticoes_por_cenario": repeticoes,
        "cenario_base": {k: (list(v) if isinstance(v, tuple) else v) for k, v in asdict(Cenario(n_cabrucas=0)).items()},
        "grade": {"n_cabrucas": N_CABRUCAS, "cenarios": {k: {"sinal_temporal": v[0], "ruido_dinamica": v[1]}
                                                         for k, v in CENARIOS.items()}},
        "ganho_verdadeiro": "mesma comunidade e referência, ajuste em 4000 propriedades e erro em outras 4000",
        "ganho_alcancavel": "mesma comunidade, 100 ajustes com n_cabrucas propriedades, erro nas mesmas 4000",
        "metodos_intervalo": simulacao.METODOS,
        "metodo_adotado": simulacao.METODO_ADOTADO,
        "nivel_ic": simulacao.NIVEL,
        "parametros_metodos": {"reajuste_n_boot": 200, "cv_k": 5, "cv_repeticoes": 20, "permutacoes": 199},
        "ganho_minimo": simulacao.GANHO_MINIMO,
        "saidas_sha256": {f: acustica.sha256(SAIDA / f) for f in ["repeticoes.csv", "resumo.csv"]},
    }
    (SAIDA / "manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2))
    print("\n" + resumo.round(3).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repeticoes", type=int, default=500)
    parser.add_argument("--permitir-sujo", action="store_true", help="roda com código não commitado e salva o diff")
    args = parser.parse_args()
    main(args.repeticoes, args.permitir_sujo)
