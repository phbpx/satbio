# Nebulosidade do Sentinel-2 no sul da Bahia (teste rápido)

**Data:** 2026-10-03, reproduzido em 2026-10-04 · **Status:** teste exploratório; script versionado em `scripts/nebulosidade_sul_bahia.py`, manifesto em `data/processed/nebulosidade/`

## Pergunta

O cubo S2-16D-2 tem composições válidas suficientes no sul da Bahia, região bem mais úmida que os sítios do piloto (RN/PB), para cumprir a regra de cobertura do desenho analítico (ao menos uma composição por trimestre e 10 no ano)?

## Como foi feito

Sem coordenadas publicadas de cabrucas, foram usados os dois únicos centros de paisagem publicados para a região (Rocha *et al.* 2019, Una e Ilhéus, UTM SAD69 24S) e uma grade de 10 pontos a cada 2 km em volta de cada um (2 linhas × 5 colunas). Os pontos não são necessariamente cabrucas; servem para medir a nebulosidade regional. Para cada ponto foram lidas as 23 composições de 2022 e contado o pixel central válido por duas regras: SCL do cubo e B02 ≤ 0,10 (a regra do teste original) e a regra principal da decisão D (SCL da cena de origem). A cobertura mínima é a do desenho: pelo menos 10 composições válidas e uma em cada trimestre.

## Resultado

Versão reproduzida (2026-10-04, commit `711d14b`):

| | Sul da Bahia (2022) | Piloto RN/PB (regra do cubo) |
|---|---|---|
| Fração de composições válidas | 57% (Ilhéus), 61% (Una) | 68% |
| Composições válidas por ponto no ano | mediana 13,5 (mínimo 10, máximo 16) | 13–20 por sítio |
| Pontos que passam na cobertura mínima | 20 de 20 | 4 de 4 |

Fração válida por trimestre de 2022 (pelo início da composição): 68% (jan–mar), 77% (abr–jun), 55% (jul–set), 32% (out–dez).

**As duas regras deram o mesmo resultado.** No pixel central, o SCL do cubo coincidiu com o da cena de origem nas 460 composições. A superestimação de ~6% da regra do cubo, vista no piloto (outros sítios, pixels da janela), não apareceu aqui.

**O que mudou em relação ao teste original (2026-10-03, script avulso).** O original tinha 52% e 59% de composições válidas, mediana de 12 por ponto (8 a 19), 19 de 20 pontos passando na cobertura e trimestres de 60%, 72%, 48% e 39%. A diferença provável é a grade de pontos, que o script avulso não registrou. A versão reproduzida é um pouco menos nublada no ano e **mais nublada no último trimestre** (32% em vez de 39%).

## O que isso quer dizer

- **A série é viável, mas com pouca folga.** A mediana de 13,5 composições válidas por ano fica pouco acima do mínimo de 10, e o pior ponto tem exatamente 10. No teste original, um ponto em 20 não passava.
- **O último trimestre do ano é o mais nublado.** Se as campanhas acústicas forem no início do ano, o trimestre antes do corte (out–dez) terá poucas composições válidas, e a "mudança recente", que exige 2 no último trimestre, vai falhar com frequência: com 32% de válidas e ~6 composições no trimestre, a chance de menos de 2 é de ~38% (com 39%, ~25%). Isso pesa na escolha das datas das campanhas.
- **Efeito na simulação de dimensionamento.** O mundo pessimista usou os números do teste original (5% sem dinâmica, 25% com dinâmica degradada). Com a reprodução, seriam ~0% e ~38%. Na sensibilidade, as lacunas foram o fator de menor efeito (ganho de 22% para 19% com 30 cabrucas), então a troca não muda as conclusões; a simulação não foi refeita.
- **Um ano só.** O teste usou 2022; outros anos podem ser mais ou menos nublados.

## Próximos passos

Repetir com pontos dentro de cabrucas (quando houver mapa ou coordenadas) e com a regra principal, e para mais de um ano. Se a folga continuar pequena, considerar janela de 18–24 meses para os descritores de estado médio ou o uso complementar do Landsat (LANDSAT-16D-1), com harmonização.
