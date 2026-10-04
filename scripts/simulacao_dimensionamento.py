"""Simulação de dimensionamento: quantas cabrucas para estimar o ganho temporal (H2)?

Uso:
    uv run python scripts/simulacao_dimensionamento.py [--repeticoes 500] [--permitir-sujo]

Duas estruturas de mundo, cada uma com cenários calibrados pelo ganho de
população de M3 sobre M2b, cruzadas com 10 a 120 cabrucas:

- otimista: preditores independentes, sem lacunas ópticas além do ruído,
  propriedades independentes e referência B1 (a estrutura das rodadas anteriores);
- pessimista: dinâmica correlacionada com o estado médio do dossel, lacunas
  ópticas na frequência observada no sul da Bahia, pares de propriedades
  vizinhas com resíduo e paisagem em comum e referência B2.

Também roda uma análise de sensibilidade com 30 cabrucas, ligando cada
suposição pessimista isoladamente no cenário otimista de ~20%, e o braço
Sentinel-1: descritor de dinâmica óptico realista contra um de radar, sem
lacunas e com menos ruído (suposição), no mundo pessimista. Em cada
repetição calcula o intervalo do ganho pelos quatro métodos e o teste de
permutação, e mede a cobertura contra o ganho de população e o alcançável.
Grava em data/processed/simulacao/ (fora do git) as repetições, o resumo e um
manifesto; a figura vai para docs/img/. Os resultados dependem das
suposições de satbio.simulacao.Cenario.
"""

from __future__ import annotations

import argparse
import json
import platform
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace
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
N_CABRUCAS = [10, 20, 30, 60, 90, 120]
SEMENTE = 20261004

# Suposições pessimistas. Lacunas: 1 de 20 pontos do sul da Bahia não passou na cobertura mínima
# (sem dinâmica: 5%); no trimestre mais nublado (39% de composições válidas, ~6 por trimestre) a
# chance de menos de 2 válidas, mínimo da mudança recente, é de ~25% (dinâmica degradada).
# Correlação dossel–dinâmica e vizinhança são suposições, não medidas.
PESSIMISTA = {"correlacao_estavel_dinamica": 0.5, "frac_sem_dinamica": 0.05, "frac_dinamica_degradada": 0.25,
              "fator_degradacao": 2.0, "tamanho_vizinhanca": 2, "correlacao_vizinhos": 0.5, "referencia": "B2"}
# Cenários calibrados pelo ganho de população médio (em MAE) em cada estrutura.
# Na pessimista, ~20% não é alcançável com dossel e paisagem explicando metade da variância:
# o máximo (~19%) exige resíduo nulo e descritor de dinâmica quase sem ruído.
ESTRUTURAS = {
    "otimista": ({}, {"ganho 0%": {"sinal_temporal": 0.0, "ruido_dinamica": 0.7},
                      "ganho ~10%": {"sinal_temporal": 0.30, "ruido_dinamica": 0.7},
                      "ganho ~20%": {"sinal_temporal": 0.45, "ruido_dinamica": 0.4}}),
    "pessimista": (PESSIMISTA, {"ganho 0%": {"sinal_temporal": 0.0, "ruido_dinamica": 0.7},
                                "ganho ~10%": {"sinal_temporal": 0.30, "ruido_dinamica": 0.2},
                                "ganho máximo (~19%)": {"sinal_temporal": 0.50, "ruido_dinamica": 0.1}}),
}
SENSIBILIDADE_N = 30
SENSIBILIDADE = {"dinâmica correlacionada com o dossel": ["correlacao_estavel_dinamica"],
                 "lacunas ópticas": ["frac_sem_dinamica", "frac_dinamica_degradada", "fator_degradacao"],
                 "vizinhos dependentes": ["tamanho_vizinhanca", "correlacao_vizinhos"],
                 "referência B2": ["referencia"],
                 "todas": list(PESSIMISTA)}
# Braço Sentinel-1 (docs/literatura/sentinel-1-dossel-fechado.md), no mundo pessimista com o mesmo sinal
# temporal do cenário de ~10%: descritor óptico com ruído realista e lacunas, contra um descritor de radar
# sem lacunas por nuvem e com menos ruído no dossel saturado. O ruído do radar é suposição.
SENTINEL1_N = [30, 60]
SENTINEL1 = {"óptico realista (ruído 0,7, lacunas)": {"ruido_dinamica": 0.7},
             "radar (ruído 0,4, sem lacunas)": {"ruido_dinamica": 0.4, "frac_sem_dinamica": 0.0,
                                                "frac_dinamica_degradada": 0.0}}
RESULTADOS = simulacao.CATEGORIAS
CORES = ["#2a78d6", "#eb6834", "#1baf7a"]  # validadas (scripts/validate_palette.js da skill de visualização)


def tarefas() -> list[dict]:
    lista = []
    for estrutura, (extra, cenarios) in ESTRUTURAS.items():
        for rotulo, params in cenarios.items():
            for n in N_CABRUCAS:
                lista.append({"bloco": "grade", "estrutura": estrutura, "cenario": rotulo,
                              "cenario_obj": Cenario(n_cabrucas=n, **params, **extra)})
    base = Cenario(n_cabrucas=SENSIBILIDADE_N, **ESTRUTURAS["otimista"][1]["ganho ~20%"])
    for rotulo, campos in SENSIBILIDADE.items():
        lista.append({"bloco": "sensibilidade", "estrutura": rotulo, "cenario": "ganho ~20% (otimista)",
                      "cenario_obj": replace(base, **{k: PESSIMISTA[k] for k in campos})})
    for rotulo, params in SENTINEL1.items():
        for n in SENTINEL1_N:
            lista.append({"bloco": "sentinel-1", "estrutura": rotulo, "cenario": "pessimista, sinal temporal 0,30",
                          "cenario_obj": Cenario(n_cabrucas=n, **{**PESSIMISTA, "sinal_temporal": 0.30, **params})})
    for i, t in enumerate(lista):
        t["semente"] = SEMENTE + i
    return lista


def _celula(args: tuple[dict, int]) -> pd.DataFrame:
    t, repeticoes = args
    return simulacao.rodar(t["cenario_obj"], repeticoes, t["semente"]).assign(
        bloco=t["bloco"], estrutura=t["estrutura"], cenario=t["cenario"])


def resumir(todas: pd.DataFrame) -> pd.DataFrame:
    chave = ["bloco", "estrutura", "cenario", "n_cabrucas"]
    g = todas.groupby(chave, sort=False)
    resumo = g.agg(ganho_verdadeiro_medio=("ganho_verdadeiro", "mean"),
                   ganho_verdadeiro_mse_medio=("ganho_verdadeiro_mse", "mean"),
                   ganho_alcancavel_medio=("ganho_alcancavel", "mean"),
                   ganho_estimado_medio=("ganho_m3_m2b", "mean"),
                   ganho_estimado_dp=("ganho_m3_m2b", "std"),
                   largura_ic_mediana=("largura_ic", "median"),
                   ic_inferior_acima_de_zero=("ic_inferior", lambda s: (s > 0).mean()),
                   rejeicao_permutacao_5pct=("p_permutacao", lambda p: (p <= 0.05).mean()),
                   mae_m2b_mediano=("mae_M2b", "median"))
    colunas = [todas[c] for c in chave]
    for m in simulacao.METODOS:
        centro = (todas[f"ic_superior_{m}"] + todas[f"ic_inferior_{m}"]) / 2
        resumo[f"vies_centro_{m}"] = (centro - todas["ganho_alcancavel"]).groupby(colunas, sort=False).mean()
        resumo[f"cobertura_alcancavel_{m}"] = g[f"cobre_alcancavel_{m}"].mean()
        resumo[f"cobertura_populacao_{m}"] = g[f"cobre_populacao_{m}"].mean()
        resumo[f"largura_mediana_{m}"] = (todas[f"ic_superior_{m}"] - todas[f"ic_inferior_{m}"]).groupby(
            colunas, sort=False).median()
    resumo["ep_cobertura"] = np.sqrt(0.9 * 0.1 / g.size())  # erro de Monte Carlo da cobertura
    return (resumo.join(pd.crosstab(colunas, todas["resultado"], normalize="index")
                        .reindex(columns=RESULTADOS, fill_value=0.0))
            .reset_index())


def figura(resumo: pd.DataFrame) -> None:
    plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#a8a7a2",
                         "text.color": "#0b0b0b", "axes.labelcolor": "#52514e", "xtick.color": "#52514e",
                         "ytick.color": "#52514e", "axes.grid": True, "grid.color": "#e6e5e0",
                         "grid.linewidth": 0.8})
    grade = resumo[resumo["bloco"] == "grade"]
    metricas = [("largura_ic_mediana", "largura mediana do IC90", 0.20, "±0,10"),
                ("ic_inferior_acima_de_zero", "fração com IC90 acima de zero", 0.80, "80%")]
    fig, eixos = plt.subplots(2, 2, figsize=(11, 7.2), sharex=True, sharey="row")
    for col, estrutura in enumerate(ESTRUTURAS):
        for lin, (coluna, rotulo_y, ref, rotulo_ref) in enumerate(metricas):
            ax = eixos[lin, col]
            ax.axhline(ref, color="#52514e", linewidth=1, linestyle=(0, (4, 3)), zorder=1)
            ax.text(6, ref + 0.01, rotulo_ref, va="bottom", ha="left", fontsize=8.5, color="#52514e")
            finais = []
            for cor, cenario in zip(CORES, ESTRUTURAS[estrutura][1]):
                r = grade[(grade["estrutura"] == estrutura) & (grade["cenario"] == cenario)].sort_values(
                    "n_cabrucas")
                ax.plot(r["n_cabrucas"], r[coluna], color=cor, linewidth=2, marker="o", markersize=5,
                        markeredgecolor="#fcfcfb", markeredgewidth=1.5, zorder=3, label=cenario)
                finais.append([float(r[coluna].iloc[-1]), cenario])
            # rótulos diretos na ponta, afastados para não se sobreporem
            altura = ax.get_ylim()[1] - ax.get_ylim()[0] if lin == 0 else 1.04
            finais.sort()
            for i in range(1, len(finais)):
                finais[i][0] = max(finais[i][0], finais[i - 1][0] + 0.06 * altura)
            for y, cenario in finais:
                ax.text(N_CABRUCAS[-1] + 5, y, cenario, va="center", fontsize=8.5, color="#0b0b0b")
            ax.set_xticks(N_CABRUCAS)
            ax.set_xlim(5, N_CABRUCAS[-1] + 45)
            if col == 0:
                ax.set_ylabel(rotulo_y)
            if lin == 0:
                ax.set_title(f"mundo {estrutura}", loc="left", fontsize=10.5, fontweight="bold")
            else:
                ax.set_xlabel("cabrucas")
                ax.set_ylim(-0.02, 1.02)
    eixos[0, 0].set_ylim(0, None)
    alcas, _ = eixos[0, 0].get_legend_handles_labels()
    fig.legend(alcas, ["sem ganho", "ganho ~10%", "ganho ~20% (otimista) / máximo ~19% (pessimista)"],
               loc="upper left", bbox_to_anchor=(0.01, 0.955), ncol=3, frameon=False, fontsize=9)
    fig.suptitle("Precisão do ganho de M3 sobre M2b por número de cabrucas (reajuste, intervalo básico)",
                 x=0.01, ha="left", fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    FIGURA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURA, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main(repeticoes: int, permitir_sujo: bool) -> None:
    codigo = rastreio.estado_do_codigo(RAIZ, SAIDA, permitir_sujo)
    lista = tarefas()
    with ProcessPoolExecutor() as ex:
        partes = list(ex.map(_celula, [(t, repeticoes) for t in lista]))
    todas = pd.concat(partes, ignore_index=True)
    todas["largura_ic"] = todas["ic_superior"] - todas["ic_inferior"]
    resumo = resumir(todas)
    for _, r in resumo.iterrows():
        print(f"{r['estrutura']:38s} {r['cenario']:22s} n={r['n_cabrucas']:3d} pop={r['ganho_verdadeiro_medio']:.3f} "
              f"alc={r['ganho_alcancavel_medio']:.3f} largura={r['largura_ic_mediana']:.2f} "
              f"IC>0={r['ic_inferior_acima_de_zero']:.0%} perm={r['rejeicao_permutacao_5pct']:.0%} "
              f"cobertura={r[f'cobertura_alcancavel_{simulacao.METODO_ADOTADO}']:.0%}")
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
        "repeticoes_por_celula": repeticoes,
        "cenario_base": {k: (list(v) if isinstance(v, tuple) else v) for k, v in asdict(Cenario(n_cabrucas=0)).items()},
        "n_cabrucas": N_CABRUCAS,
        "estruturas": {k: {"suposicoes": v[0], "cenarios": v[1]} for k, v in ESTRUTURAS.items()},
        "sensibilidade": {"n_cabrucas": SENSIBILIDADE_N, "base": "otimista, ganho ~20%", "fatores": SENSIBILIDADE},
        "sentinel1": {"n_cabrucas": SENTINEL1_N, "base": "pessimista, sinal temporal 0,30", "descritores": SENTINEL1},
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repeticoes", type=int, default=500)
    parser.add_argument("--permitir-sujo", action="store_true", help="roda com código não commitado e salva o diff")
    args = parser.parse_args()
    main(args.repeticoes, args.permitir_sujo)
