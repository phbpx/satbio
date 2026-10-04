# Simulação de dimensionamento: quantas cabrucas?

**Data:** 2026-10-04 · **Status:** terceira rodada; fecha o método de inferência e o estimando de H2 ([desenho analítico](desenho-analitico.md), seção 4) e informa a decisão C (seção 9)

## Pergunta

Com 10, 20 ou 30 cabrucas, com que precisão a análise principal do desenho estima o ganho da dimensão temporal do Sentinel-2 (H2: M3 × M2b), e qual método de intervalo tem a cobertura que promete?

## O que foi simulado

A simulação gera dados com a estrutura que o estudo supõe e aplica a análise do desenho:

1. **Condição ecológica latente** de cada cabruca: estado médio do dossel (30% da variância), contexto da paisagem (20%), dinâmica temporal (o que H2 testa) e um resíduo que nenhum preditor capta.
2. **Comunidade de aves:** 140 espécies, metade florestais (escala de Oliveira *et al.* 2026); a chance de ocupar a cabruca sobe com a condição para as florestais. Os parâmetros das espécies são sorteados por repetição.
3. **Observação:** 252 minutos por cabruca × campanha (um ponto do protocolo inicial); chance por minuto de cada espécie presente ser gravada sorteada entre 0,0005 e 0,03, o que detecta cerca de 56% das espécies presentes; o reconhecedor acerta 80% das vocalizações gravadas e inclui por engano 1% das espécies ausentes.
4. **Referência (decisão B1):** união das listas de 5 matas independentes, sorteada uma vez por repetição e compartilhada pela amostra e pelos ganhos de referência (na rodada anterior cada amostra tinha a sua, o que somava ruído aos ganhos de referência).
5. **Resposta:** distância de Jaccard entre a lista da cabruca e a referência.
6. **Preditores com ruído:** janela recente, mediana anual, dinâmica e paisagem.
7. **Análise do desenho:** M2b e M3 em regressão ridge (λ = 1), cada cabruca prevista por um modelo ajustado sem ela; ganho = 1 − MAE(M3)/MAE(M2b).
8. **Dois estimandos**, no mesmo mundo da repetição, medidos em 4.000 propriedades novas: o **ganho de população** (modelos ajustados em outras 4.000) e o **ganho alcançável com o n do estudo** (média de 100 ajustes com n cabrucas).

Os cenários foram **calibrados pelo ganho de população**: 0%, ~10%, ~15% e ~20% do MAE. Os dois últimos exigem um descritor de dinâmica menos ruidoso que o suposto inicialmente (ruído 0,4 em vez de 0,7). São 500 repetições por cenário; código em `src/satbio/simulacao.py`, execução com `uv run python scripts/simulacao_dimensionamento.py` (cerca de 3 minutos em 10 núcleos). Saídas e manifesto em `data/processed/simulacao/` (fora do git).

## Método de inferência

Quatro intervalos de 90% foram calculados em cada repetição:

- **Erros fixos** (o método anterior do desenho): reamostragem pareada dos erros da validação deixando um fora.
- **Reajuste, percentil:** reamostragem de propriedades com reposição; em cada réplica os modelos são reajustados e a validação por propriedade retida é refeita, com as cópias da retida fora do treino (200 réplicas na simulação). Intervalo pelos quantis das réplicas.
- **Reajuste, básico:** as mesmas réplicas, intervalo 2·ganho − quantis. Cada réplica treina com cerca de 63% de propriedades distintas e por isso sai deslocada para baixo; o intervalo básico desconta esse deslocamento.
- **Validação cruzada corrigida:** 5 dobras repetidas 20 vezes, variância da razão pelo método delta com a correção de Nadeau & Bengio (2003) na forma de Bouckaert & Frank (2004).

Também foi feito o **teste de permutação** do descritor de dinâmica (199 permutações), que testa só se o ganho é maior que zero.

**Cobertura do IC90 contra o ganho alcançável** (erro de Monte Carlo de ±1,3 ponto por célula):

| Cabrucas | Ganho de população | Ganho alcançável | Erros fixos | Reajuste, percentil | **Reajuste, básico** | CV corrigida |
|---|---|---|---|---|---|---|
| 10 | 0% | −6% | 79% | 100% | 93% | 92% |
| 10 | 11% | 5% | 60% | 99% | 87% | 78% |
| 10 | 14% | 9% | 58% | 100% | 86% | 74% |
| 10 | 22% | 17% | 63% | 99% | 85% | 74% |
| 20 | 0% | −3% | 82% | 100% | 99% | 99% |
| 20 | 11% | 8% | 72% | 94% | 92% | 78% |
| 20 | 14% | 12% | 75% | 93% | 91% | 80% |
| 20 | 22% | 20% | 78% | 96% | 89% | 82% |
| 30 | 0% | −2% | 83% | 100% | 100% | 99% |
| 30 | 11% | 9% | 77% | 90% | 86% | 81% |
| 30 | 14% | 13% | 81% | 93% | 89% | 84% |
| 30 | 22% | 21% | 83% | 93% | 87% | 85% |
| **Geral** | | | **74%** | **97%** | **90%** | **84%** |

Contra o ganho de população, as coberturas gerais são 67%, 95%, 90% e 81%.

**Escolha (2026-10-04): reamostragem de propriedades com reajuste, intervalo básico**, por ter a cobertura geral mais próxima de 90%. Ela fica abaixo de 90% em alguns cenários com ganho (85% a 89%, até 4 pontos além do erro de Monte Carlo) e acima sem ganho (93% a 100%), o que torna falsos positivos raros. O intervalo percentil nunca fica abaixo de 90%, mas é conservador (97% no geral, largura igual); fica registrado como análise de sensibilidade. A validação cruzada corrigida e o método anterior cobrem pouco quando há ganho. O teste de permutação tem o tamanho correto (rejeita 4,6% a 5% das vezes sem ganho, para α = 5%) e é reportado ao lado do intervalo.

**Estimando: ganho alcançável com o n do estudo.** A justificativa está no desenho analítico (seção 4). O ganho alcançável fica 5 pontos abaixo do de população com 10 cabrucas e 1,5 com 30.

## Resultado

![Resultado da simulação por número de cabrucas e ganho verdadeiro](img/simulacao-dimensionamento.png)

**Precisão da estimativa do ganho, com o método adotado:**

| Cabrucas | Ganho alcançável | Estimativa média | Desvio-padrão da estimativa | Largura mediana do IC90 | IC exclui zero | Permutação rejeita (5%) |
|---|---|---|---|---|---|---|
| 10 | −6% | −6% | 0,16 | 1,04 | 4% | 5% |
| 10 | 17% | 14% | 0,22 | 1,02 | 26% | 34% |
| 20 | −3% | −3% | 0,06 | 0,40 | 0% | 5% |
| 20 | 8% | 8% | 0,12 | 0,54 | 11% | 38% |
| 20 | 20% | 19% | 0,14 | 0,59 | 37% | 74% |
| 30 | −2% | −2% | 0,04 | 0,23 | 0% | 5% |
| 30 | 9% | 9% | 0,10 | 0,38 | 18% | 56% |
| 30 | 21% | 20% | 0,11 | 0,44 | 50% | 89% |

A tabela completa (todos os cenários, leituras da decisão E, viés de cada método) fica em `data/processed/simulacao/resumo.csv`.

## O que isso quer dizer

- **O intervalo antigo prometia mais precisão do que havia.** Com intervalos que cobrem o que prometem, a largura do IC90 é 1,0 com 10 cabrucas, 0,4 a 0,6 com 20 e 0,23 a 0,44 com 30. A largura com ganho é maior que sem ganho porque a variância do ganho cresce com ele.
- **10 cabrucas não informam sobre H2:** o intervalo cobre de −50% a +50%.
- **Com 30 cabrucas, um ganho de 20% é estimado com intervalo de ±0,22.** O intervalo exclui zero em metade das repetições; o teste de permutação rejeita em 89%. Um ganho de 10% fica com intervalo de ±0,19, do tamanho do próprio ganho.
- **O teste de permutação tem bem mais poder que o intervalo** para dizer que há ganho, mas não diz quanto. É o resultado complementar natural para "a dinâmica acrescenta algo?".
- **O MAE comprime o ganho.** Com erros aproximadamente normais, a razão dos MAE é a raiz da razão dos MSE: 10% de ganho em MAE corresponde a cerca de 19% em MSE.

## Limites

Os números valem para as suposições acima, que não foram medidas em cabruca: frações de sinal, detectabilidade, erro do reconhecedor, ruído dos descritores e condição das matas. Esta rodada ainda é otimista: os preditores são independentes entre si, não há lacunas ópticas além do ruído nem dependência espacial entre propriedades vizinhas, a referência é sempre B1 e o ridge usa λ fixo. A cobertura foi medida nos mesmos cenários em que o método foi escolhido; ela precisa ser conferida de novo nos cenários menos otimistas.

## Decisões que isto fecha ou levanta

1. **Fechado:** método de inferência e estimando de H2 (desenho analítico, seção 4).
2. **Fechado:** H2 é reportada como estimativa com intervalo; a decisão E vira regra de leitura, com as categorias escritas no desenho.
3. **Decisão C:** depende da rodada menos otimista.
