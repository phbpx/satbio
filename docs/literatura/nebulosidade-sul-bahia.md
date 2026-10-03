# Nebulosidade do Sentinel-2 no sul da Bahia (teste rápido)

**Data:** 2026-10-03 · **Status:** teste exploratório, feito com script avulso (não versionado)

## Pergunta

O cubo S2-16D-2 tem composições válidas suficientes no sul da Bahia, região bem mais úmida que os sítios do piloto (RN/PB), para cumprir a regra de cobertura do desenho analítico (ao menos uma composição por trimestre e 10 no ano)?

## Como foi feito

Sem coordenadas publicadas de cabrucas, foram usados os dois únicos centros de paisagem publicados para a região (Rocha *et al.* 2019, Una e Ilhéus, UTM SAD69 24S) e uma grade de 10 pontos a cada ~2 km em volta de cada um. Os pontos não são necessariamente cabrucas; servem para medir a nebulosidade regional. Para cada ponto foram lidas as 23 composições de 2022 (tiles 037021 e 037022) e contado o pixel válido pela regra com o SCL do cubo e B02 ≤ 0,10. Essa regra superestima a validade em cerca de 6% em relação à regra principal (SCL da cena de origem), segundo a semana 3 do piloto.

## Resultado

| | Sul da Bahia (2022) | Piloto RN/PB (mesma regra) |
|---|---|---|
| Fração de composições válidas | 52% (Ilhéus), 59% (Una) | 68% |
| Composições válidas por ponto no ano | mediana 12 (mínimo 8, máximo 19) | 13–20 por sítio |
| Pontos que passam na cobertura mínima | 19 de 20 | 4 de 4 |

Fração válida por trimestre de 2022: 60% (jan–mar), 72% (abr–jun), 48% (jul–set), 39% (out–dez).

## O que isso quer dizer

- **A série é viável, mas com pouca folga.** A mediana de 12 composições válidas por ano fica logo acima do mínimo de 10, e um ponto em 20 não passaria. Com a regra principal (SCL da cena de origem), a folga diminui mais um pouco.
- **O último trimestre do ano é o mais nublado.** Se as campanhas acústicas forem no início do ano, o trimestre antes do corte (out–dez) terá poucas composições válidas, e a "mudança recente", que exige 2 no último trimestre, vai falhar com frequência. Isso pesa na escolha das datas das campanhas.
- **Um ano só.** O teste usou 2022; outros anos podem ser mais ou menos nublados.

## Próximos passos

Repetir com pontos dentro de cabrucas (quando houver mapa ou coordenadas) e com a regra principal, e para mais de um ano. Se a folga continuar pequena, considerar janela de 18–24 meses para os descritores de estado médio ou o uso complementar do Landsat (LANDSAT-16D-1), com harmonização.
