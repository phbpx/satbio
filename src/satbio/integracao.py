"""Tabela analítica: acústica e série óptica por sítio × campanha.

Implementa, para o piloto, as regras do desenho analítico
(docs/desenho-analitico.md): descritores ópticos da seção 5, cobertura mínima
da seção 6 e riqueza detectada com esforço padronizado da seção 2. O
indicador principal (Jaccard até a referência) não é calculado aqui porque
o piloto não tem matas de referência.
"""

from __future__ import annotations

from math import comb

import numpy as np
import pandas as pd

# Cobertura mínima da série (desenho analítico, seção 6).
MIN_COMPOSICOES_VALIDAS = 10
TRIMESTRES = 4
# Uma composição entra nos descritores se a maioria da janela 3×3 for válida.
MIN_PIXELS_VALIDOS_JANELA = 5
# A mudança recente só é calculada com pelo menos isto de composições no último trimestre.
MIN_COMPOSICOES_ULTIMO_TRIMESTRE = 2


def riqueza_rarefeita(minutos_por_especie: pd.Series, total_minutos: int, m: int) -> float:
    """Riqueza esperada em `m` minutos sorteados sem reposição entre `total_minutos`.

    Rarefação por amostras (minutos como unidades): para cada espécie detectada
    em n_i minutos, a chance de aparecer em m minutos é 1 − C(N − n_i, m) / C(N, m).
    """
    if not 0 < m <= total_minutos:
        raise ValueError(f"m={m} precisa estar entre 1 e o total de minutos ({total_minutos})")
    total = comb(total_minutos, m)
    return float(sum(1 - comb(total_minutos - int(n), m) / total for n in minutos_por_especie))


def gravacoes_por_campanha(gravacoes: pd.DataFrame, campanhas: pd.DataFrame) -> pd.DataFrame:
    """Atribui cada gravação válida à campanha do seu sítio cujo intervalo a contém.

    Levanta ValueError se uma gravação válida não cair em nenhuma campanha.
    """
    validas = gravacoes[gravacoes["erro"].isna()].copy()
    inicio = pd.to_datetime(validas["inicio_relogio"])
    validas["campanha_id"] = None
    for _, camp in campanhas.iterrows():
        dentro = ((validas["sitio"] == camp["sitio"]) & (inicio >= pd.Timestamp(camp["inicio_relogio"]))
                  & (inicio <= pd.Timestamp(camp["fim_relogio"])))
        validas.loc[dentro, "campanha_id"] = camp["campanha_id"]
    soltas = validas.loc[validas["campanha_id"].isna(), "arquivo"].tolist()
    if soltas:
        raise ValueError(f"gravações fora de qualquer campanha: {soltas[:5]}")
    return validas


def resumo_acustico(gravacoes: pd.DataFrame, deteccoes: pd.DataFrame, campanhas: pd.DataFrame,
                    m_padrao: int | None = None) -> pd.DataFrame:
    """Esforço e riqueza detectada por sítio × campanha.

    `m_padrao` é o esforço comum da rarefação. No estudo ele deve ser fixado
    pelo protocolo antes da coleta (desenho analítico, seção 2); se não for
    informado, usa o menor número de minutos entre as campanhas, o que só
    vale como demonstração, porque deixa unidades de teste definirem a
    resposta das de treino. A riqueza rarefeita é a média em subconjuntos
    aleatórios de `m` minutos; data e horário dos minutos não são
    padronizados. Não detecção não é ausência.
    """
    validas = gravacoes_por_campanha(gravacoes, campanhas)
    m = m_padrao or int(validas.groupby("campanha_id")["arquivo"].nunique().min())
    linhas = []
    for _, camp in campanhas.iterrows():
        sitio = camp["sitio"]
        arquivos = set(validas.loc[validas["campanha_id"] == camp["campanha_id"], "arquivo"])
        d = deteccoes[deteccoes["arquivo"].isin(arquivos)]
        por_especie = d.groupby("especie")["arquivo"].nunique()
        linhas.append({
            "sitio": sitio,
            "campanha_id": camp["campanha_id"],
            "minutos_validos": len(arquivos),
            "especies_detectadas": int(por_especie.size),
            "esforco_padrao_min": m,
            "riqueza_rarefeita": riqueza_rarefeita(por_especie, len(arquivos), m),
            "especies": ";".join(sorted(por_especie.index)),
        })
    return pd.DataFrame(linhas)


def descritores_opticos(serie: pd.DataFrame) -> pd.DataFrame:
    """Descritores da série por sítio × campanha (desenho analítico, seção 5).

    Usa a mediana da janela 3×3 de cada composição em que a maioria da janela
    é válida pela regra principal. O trimestre de cada composição é o da
    data de observação do pixel central (PROVENANCE), ou o meio do período se
    ela faltar. A cobertura exige ao menos uma composição em cada trimestre da
    janela de 12 meses e MIN_COMPOSICOES_VALIDAS no total; sem cobertura, os
    descritores ficam vazios e `cobertura_ok` é falso. A mudança recente só é
    calculada com MIN_COMPOSICOES_ULTIMO_TRIMESTRE no último trimestre; ela
    mistura fase sazonal e perturbação quando os cortes caem em meses
    diferentes.
    """
    linhas = []
    for (sitio, campanha), s in serie.groupby(["sitio", "campanha_id"]):
        corte = pd.Timestamp(s["corte"].iloc[0])
        inicio = corte - pd.Timedelta(days=365)
        usadas = s[s["viz_n_validos"] >= MIN_PIXELS_VALIDOS_JANELA].copy()
        meio = pd.to_datetime(usadas["inicio_composicao"]) + pd.Timedelta(days=8)
        obs = usadas["data_observacao"] if "data_observacao" in usadas else pd.Series(pd.NaT, index=usadas.index)
        usadas["data"] = pd.to_datetime(obs, errors="coerce").fillna(meio)
        trimestre = ((usadas["data"] - inicio).dt.days // (365 / TRIMESTRES)).clip(0, TRIMESTRES - 1)
        trimestres_cobertos = int(trimestre.nunique())
        cobertura_ok = len(usadas) >= MIN_COMPOSICOES_VALIDAS and trimestres_cobertos == TRIMESTRES

        n_ultimo = int((trimestre == TRIMESTRES - 1).sum())
        linha = {"sitio": sitio, "campanha_id": campanha, "corte": corte.date(), "composicoes": len(s),
                 "composicoes_usadas": len(usadas), "trimestres_cobertos": trimestres_cobertos,
                 "n_ultimo_trimestre": n_ultimo, "cobertura_ok": cobertura_ok}
        if cobertura_ok:
            ndvi, ndmi = usadas["viz_NDVI_mediana"], usadas["viz_NDMI_mediana"]
            ultimo_trimestre = usadas[trimestre == TRIMESTRES - 1]["viz_NDMI_mediana"]
            linha.update({
                "ndvi_mediana": float(ndvi.median()),
                "ndmi_mediana": float(ndmi.median()),
                "ndvi_amplitude_p90_p10": float(np.percentile(ndvi, 90) - np.percentile(ndvi, 10)),
                "ndmi_mudanca_recente": float(ultimo_trimestre.median() - ndmi.median())
                if n_ultimo >= MIN_COMPOSICOES_ULTIMO_TRIMESTRE else None,
            })
        else:
            linha.update({"ndvi_mediana": None, "ndmi_mediana": None, "ndvi_amplitude_p90_p10": None,
                          "ndmi_mudanca_recente": None})
        linhas.append(linha)
    return pd.DataFrame(linhas)


def tabela_analitica(acustico: pd.DataFrame, optico: pd.DataFrame, pontos: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por sítio × campanha do resumo acústico, com a unidade de validação explícita.

    Campanha sem série óptica fica com `cobertura_ok` falso; série óptica sem
    campanha acústica é erro.
    """
    sobras = set(optico["campanha_id"]) - set(acustico["campanha_id"])
    if sobras:
        raise ValueError(f"séries ópticas sem campanha acústica: {sorted(sobras)}")
    tabela = acustico.merge(optico, on=["sitio", "campanha_id"], how="left", validate="one_to_one")
    tabela["cobertura_ok"] = tabela["cobertura_ok"].astype("boolean").fillna(False).astype(bool)
    contexto = pontos[["sitio", "grupo_validacao", "latitude", "longitude", "gravador"]]
    return contexto.merge(tabela, on="sitio", how="right", validate="one_to_many")
