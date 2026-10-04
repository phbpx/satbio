# Piloto — semana 4: inventário, integração reproduzível e portão G1

**Data:** 2026-10-03 · **Status:** concluída; G1 aprovado de forma condicional em 2026-10-03

## Reproduzir o piloto inteiro

```
uv sync
uv run python scripts/reproduzir_piloto.py
```

Roda as semanas 2, 3 e 4 e gera as figuras, nesta ordem. Precisa de internet (Zenodo e catálogo STAC do INPE), baixa cerca de 213 MB na primeira vez e leva cerca de 10 minutos. As etapas das semanas 2 a 4 recusam rodar com código não commitado (ou salvam o diff, com `--permitir-sujo`) e gravam um manifesto com commit, versões, regras e hashes das entradas e saídas; o manifesto da semana 4 registra o commit e o hash dos manifestos das semanas 2 e 3. O script de figuras não grava manifesto: as figuras são derivadas das tabelas e regeneradas a cada execução.

## Inventário de dados

### Fontes

| Fonte | O que é | Versão / identificador | Licença | Acesso | Uso no projeto | Local |
|---|---|---|---|---|---|---|
| WABAD | Áudios de 1 min e anotações de especialistas por espécie | v4, DOI 10.5281/zenodo.20513304 | Divergente: CC BY 4.0 (campo do Zenodo) × CC BY-NC 4.0 (descrição); tratada como não comercial | 2026-10-03 | Teste do fluxo: 4 sítios do RN/PB | `data/raw/wabad/` (423 MB) |
| Soundscape_CCM1 | Rótulos por grupo; áudios no Google Drive | GitHub LEEClab, último push 2021-02-05 | GPL-3.0 no repositório; áudios sem licença declarada | 2026-10-03 | Não usado: sem coordenadas | — |
| AnuraSet | Áudios e rótulos de anuros | DOI 10.5281/zenodo.8342596 | Divergente: CC BY (Zenodo) × CC0 (artigo) | 2026-10-03 | Não usado: grupo e sítios inadequados | — |
| Rosa *et al.* 2024 | Listas espécie × minuto de aves, sem áudio | DOI 10.5281/zenodo.10556620 | CC BY 4.0 | 2026-10-03 | Não usado: sem coordenadas por ponto; referência de desenho amostral | — |
| S2-16D-2 (BDC/INPE) | Cubo Sentinel-2 de 16 dias | Coleção v2, catálogo `data.inpe.br/bdc/stac/v1` | Aviso legal do Copernicus Sentinel (uso livre com atribuição) | 2026-10-03, leitura remota | Série óptica: 90 composições | Só os valores extraídos |
| S2_L2A-1 (BDC/INPE) | Cenas Sentinel-2 L2A individuais | Coleção v1 | Copernicus Sentinel | 2026-10-03, leitura remota | Conferência do SCL (decisão D): 70 cenas | Só os valores extraídos |

As auditorias completas estão em [`docs/bases/`](../bases/README.md). Ainda faltam o mapa de cobertura para o contexto da paisagem (candidato: MapBiomas Cacau, usado por Oliveira *et al.* 2026) e o PRODES Mata Atlântica.

### Tabelas derivadas

Todas ficam em `data/processed/` (fora do git, por volume e licença) e são descritas coluna a coluna no [dicionário de dados](../dicionario-dados.md), gerado a partir dos cabeçalhos reais:

| Tabela | Linhas | Gerada por |
|---|---|---|
| `wabad/pontos`, `campanhas`, `gravacoes`, `deteccoes`, `controle_qualidade` | 4 sítios, 4 campanhas, 72 gravações, 1.347 anotações | `scripts/semana2_wabad.py` |
| `stac/serie_s2` | 90 composições | `scripts/semana3_stac.py` |
| `integracao/tabela_piloto` | 4 sítios × campanha | `scripts/semana4_integracao.py` |

## Integração: exemplo da tabela analítica

A tabela junta, por sítio × campanha, o resumo acústico e os descritores ópticos definidos no [desenho analítico](../desenho-analitico.md) (seções 2, 5 e 6). Ela demonstra que o fluxo funciona de ponta a ponta; **não serve para estimar associações**: são 4 sítios do WABAD, fora de cabruca, sem matas de referência, e o esforço acústico não segue um protocolo padronizado.

| Sítio | Minutos | Espécies detectadas | Riqueza rarefeita (13 min) | Composições usadas | No último trimestre | NDVI mediana | NDMI mediana | Amplitude NDVI (P90−P10) | Mudança recente NDMI |
|---|---|---|---|---|---|---|---|---|---|
| RBA | 15 | 28 | 26,1 | 14 | 4 | 0,84 | 0,38 | 0,14 | +0,01 |
| RFP | 31 | 41 | 26,3 | 13 | 5 | 0,83 | 0,34 | 0,09 | −0,01 |
| RGU | 13 | 14 | 14,0 | 13 | 2 | 0,87 | 0,41 | 0,10 | −0,06 |
| RME | 13 | 21 | 21,0 | 20 | 6 | 0,87 | 0,39 | 0,11 | −0,04 |

- **Riqueza rarefeita.** Média da riqueza detectada em subconjuntos aleatórios de 13 minutos (o menor esforço entre as campanhas), por rarefação com os minutos como unidades. Ela padroniza só o número de minutos: data e horário não são padronizados, e os minutos do WABAD foram escolhidos pelos autores, incluindo minutos noturnos. No RGU e no RME, com 13 minutos, o valor é o próprio observado. É riqueza **detectada**: não detecção não é ausência. No estudo, o esforço será fixado pelo protocolo, não pelo menor esforço observado.
- **Descritores ópticos.** Calculados com a mediana da janela 3×3 de cada composição em que a maioria da janela é válida, e só se a série tiver ao menos 10 composições e uma em cada trimestre (pela data de observação). As quatro séries atendem à cobertura. A mudança recente exige 2 composições no último trimestre e, como os cortes caem entre outubro e dezembro, mistura fase sazonal com perturbação; aqui ela não deve ser lida como perturbação.
- **O indicador principal não aparece.** A distância de Jaccard até a referência exige matas de referência com o mesmo protocolo (decisão B, aberta), que o piloto não tem.

## Portão G1 — decisão

**Pergunta do G1 (PRD, seção 7):** qual base sustenta o projeto — cabruca via parceria ou campanha própria (caminho A), só dados abertos (B), ou estudo metodológico (C)?

**Evidência do piloto:**

- Nenhuma das quatro bases abertas auditadas tem gravações de aves em cabruca ou no sul da Bahia, e nenhuma tem áreas independentes com coordenadas por ponto em número próximo ao necessário.
- O grupo de ecologia de aves da UESC (Morante-Filho, Faria e colaboradores) já amostrou aves com pontos de escuta em 10 a 30 agroflorestas de cacau no sul da Bahia. É o parceiro mais provável para propriedades e validação taxonômica. O contato foi enviado em 2026-10-04 (atualização posterior ao portão).
- O fluxo técnico funciona de ponta a ponta com dados abertos: vínculo áudio–ponto–data, série óptica sem vazamento, máscara conferida contra as cenas de origem e tabela analítica com rastreabilidade completa.

**Decisão (aprovada em 2026-10-03):**

1. **Caminho B descartado.** Não existe base aberta que responda à pergunta em cabruca.
2. **Caminho A como principal, condicional à parceria.** O G1 fica aprovado de forma condicional: o projeto segue para a fase 2 (piloto de campo e dimensionamento) se a parceria com a UESC, ou outra equivalente, for confirmada.
3. **Caminho C como alternativa com prazo.** Se não houver parceria confirmada até **2026-12-02**, o projeto segue como estudo metodológico de integração com dados abertos, e o título e as afirmações mudam para refletir isso.

As decisões B (referência) e C (número de cabrucas) do desenho analítico dependem da mesma conversa com a UESC.

**Atualização (2026-10-04):** o contato com a UESC foi enviado; o prazo de 2026-12-02 continua valendo. Foi acrescentado ao PRD (seção 7) o caminho A-retro: estudo retrospectivo com os pontos de escuta que a UESC já coletou, sem campanha nova nem áudio.

## Encerramento do piloto

| Semana | Entrega | Situação |
|---|---|---|
| 1 | Auditoria das bases | Concluída ([`docs/bases/`](../bases/README.md)) |
| 2 | Áudios vinculados a datas e pontos | Concluída ([semana 2](semana-2.md)) |
| 3 | Série óptica com máscara de qualidade | Concluída ([semana 3](semana-3.md)) |
| 4 | Inventário, integração reproduzível e decisão do G1 | Concluída ([semana 4](semana-4.md)) |

O piloto testou o fluxo técnico. Ele não mediu desempenho de reconhecedor, não validou o protocolo de gravação e não estimou capacidade preditiva; essas são tarefas da fase 2, que depende do G1.
