# Simulação de dimensionamento: quantas cabrucas?

**Data:** 2026-10-03 · **Status:** segunda rodada, revisada; informa a decisão C do [desenho analítico](desenho-analitico.md) (seção 9) e mostra que o método de intervalo da seção 4 precisa ser trocado

## Pergunta

Com 10, 20 ou 30 cabrucas, a análise principal do desenho consegue avaliar se a dimensão temporal do Sentinel-2 acrescenta um ganho relevante (H2: M3 × M2b; decisão E: pelo menos 10% do MAE de M2b)?

## O que foi simulado

A simulação gera dados com a estrutura que o estudo supõe e aplica a análise do desenho:

1. **Condição ecológica latente** de cada cabruca: estado médio do dossel (30% da variância), contexto da paisagem (20%), dinâmica temporal (o que H2 testa) e um resíduo que nenhum preditor capta.
2. **Comunidade de aves:** 140 espécies, metade florestais (escala de Oliveira *et al.* 2026); a chance de ocupar a cabruca sobe com a condição para as florestais. Os parâmetros das espécies são sorteados por repetição.
3. **Observação:** 252 minutos por cabruca × campanha (um ponto do protocolo inicial); chance por minuto de cada espécie presente ser gravada sorteada entre 0,0005 e 0,03, o que detecta cerca de 56% das espécies presentes; o reconhecedor acerta 80% das vocalizações gravadas e inclui por engano 1% das espécies ausentes.
4. **Referência (decisão B1):** união das listas de 5 matas independentes.
5. **Resposta:** distância de Jaccard entre a lista da cabruca e a referência.
6. **Preditores com ruído:** janela recente, mediana anual, dinâmica e paisagem.
7. **Análise do desenho:** M2b e M3 em regressão ridge (λ = 1), cada cabruca prevista por um modelo ajustado sem ela; ganho = 1 − MAE(M3)/MAE(M2b), com intervalo de 90% por reamostragem pareada de cabrucas.
8. **Ganho verdadeiro** de cada repetição: mesma comunidade, modelo ajustado em 4.000 propriedades e avaliado em outras 4.000.

Os cenários foram **calibrados pelo ganho verdadeiro**: 0%, ~10%, ~15% e ~20% do MAE. Os dois últimos exigem um descritor de dinâmica menos ruidoso que o suposto inicialmente (ruído 0,4 em vez de 0,7); ganhos acima de ~24% não são alcançáveis nesta estrutura, porque dossel e paisagem já explicam metade da variância. São 500 repetições por cenário; código em `src/satbio/simulacao.py`, execução com `uv run python scripts/simulacao_dimensionamento.py` (cerca de 3 minutos).

## Resultado

![Resultado da simulação por número de cabrucas e ganho verdadeiro](img/simulacao-dimensionamento.png)

**Precisão e confiabilidade da estimativa do ganho** (o que fecha a decisão C):

| Cabrucas | Ganho verdadeiro | Estimativa média | Desvio-padrão da estimativa | Largura do IC90 | Cobertura do IC90 |
|---|---|---|---|---|---|
| 10 | 0% | −6% | 0,17 | 0,39 | 56% |
| 10 | 21% | 14% | 0,24 | 0,47 | 55% |
| 20 | 0% | −3% | 0,06 | 0,17 | 60% |
| 20 | 21% | 18% | 0,14 | 0,37 | 73% |
| 30 | 0% | −2% | 0,04 | 0,11 | 61% |
| 30 | 21% | 20% | 0,11 | 0,31 | 78% |

**O que a regra da decisão E concluiria** (fração das repetições):

| Cabrucas | Ganho verdadeiro | Relevante confirmado | Positivo, estimativa ≥ 10% | Positivo, abaixo de 10% | Inconclusivo | Relevante descartado |
|---|---|---|---|---|---|---|
| 10 | 0% | 4% | 2% | 0% | 33% | 61% |
| 10 | 21% | 19% | 9% | 0% | 54% | 17% |
| 20 | 0% | 0% | 2% | 0% | 23% | 75% |
| 20 | 21% | 19% | 22% | 0% | 54% | 5% |
| 30 | 0% | 0% | 1% | 0% | 15% | 84% |
| 30 | 21% | 26% | 32% | 0% | 39% | 3% |

"Relevante confirmado": o intervalo inteiro acima de 10%. "Positivo, estimativa ≥ 10%": o intervalo exclui zero e a estimativa passa de 10%, mas o intervalo ainda admite ganho irrelevante. A tabela completa (com os cenários de ~10% e ~15%) fica em `data/processed/simulacao/resumo.csv`.

## O que isso quer dizer

- **O intervalo do desenho não é confiável com 10 a 30 cabrucas.** Um IC90 deveria cobrir o ganho verdadeiro em 90% das vezes; aqui cobre de 54% a 81%. Há duas causas. (1) **Viés para baixo**: com poucas cabrucas, o modelo maior paga o custo de estimar um parâmetro a mais, e a estimativa sai abaixo do ganho de população (−6 a −8 pontos com 10 cabrucas, −1 a −2 com 30). (2) **Intervalo estreito demais**: a reamostragem dos erros da validação deixando um fora trata esses erros como independentes, mas eles compartilham dados de treino; com 10 cabrucas o intervalo tem largura 0,47 quando a dispersão real pediria cerca de 0,7. Por isso, sem nenhum ganho real e com 10 cabrucas, a regra "confirma" ganho relevante em 4% das vezes.
- **10 cabrucas não informam sobre H2.** A estimativa varia ±0,2 a 0,24 (um desvio-padrão), mais que qualquer ganho plausível.
- **Com 30 cabrucas, um ganho de 20% começa a aparecer.** O intervalo exclui zero em 58% das repetições e o ganho é descartado em só 3%; o desvio-padrão da estimativa cai para 0,11. Um ganho de 10% continua majoritariamente inconclusivo em qualquer n testado.
- **Precisão por número de cabrucas.** O desvio-padrão da estimativa cai de ~0,22 (10) para ~0,13 (20) e ~0,10 (30). Distinguir com folga um ganho de 20% de zero pediria desvio-padrão de cerca de 0,07, o que, pela tendência, exigiria por volta de 60 cabrucas.
- **O MAE comprime o ganho.** Como propriedade da métrica: com erros aproximadamente normais, a razão dos MAE é a raiz da razão dos MSE, então 10% de ganho em MAE corresponde a cerca de 19% de redução do erro quadrático. Nos cenários, um ganho de 21% em MAE corresponde a cerca de 37% em MSE.

## Limites

Os números valem para as suposições acima, que não foram medidas em cabruca: frações de sinal, detectabilidade, erro do reconhecedor, ruído dos descritores e condição das matas. Preditores independentes entre si tornam a simulação otimista (na prática, a dinâmica do dossel se correlaciona com o estado médio). A simulação usa uma campanha por cabruca, não modela lacunas ópticas além do ruído, nem dependência espacial entre propriedades vizinhas, nem a opção B2 de referência, e usa ridge com λ fixo (quase uma regressão comum com tão poucas cabrucas). O piloto de campo e a parceria devem trazer valores melhores para essas suposições, e a simulação deve ser rodada de novo antes de fechar a decisão C.

## Decisões que isto levanta

1. **Método de inferência (seção 4 do desenho).** O intervalo por reamostragem dos erros da validação deixando um fora precisa ser substituído por um método cuja cobertura seja verificada nesta mesma simulação antes de congelar o desenho. Candidatos: teste de permutação para "o ganho é maior que zero" (permutar o descritor de dinâmica entre cabrucas e refazer a validação); validação cruzada repetida com correção de variância; ou reamostragem que reajusta os modelos a cada réplica.
2. **Estimando.** Decidir se H2 é sobre o ganho de população (a informação existe no satélite) ou sobre o ganho alcançável com o número de cabrucas do estudo (o que esta amostra consegue aproveitar). Com poucas cabrucas eles diferem.
3. **Decisão C.** 10 cabrucas parecem insuficientes; 30 começam a informar sobre ganhos de ~20%; ganhos de ~10% pediriam bem mais. Isso depende do método de inferência que for adotado.
4. **Como reportar H2.** Estimativa com intervalo (precisão) como resultado principal, com a decisão E para interpretar, e a leitura da regra fechada por escrito (ver as categorias acima).
5. **Esforço e descritores.** Mais minutos por campanha e um descritor de dinâmica menos sensível a lacunas aumentam o ganho alcançável; ganhos de 15% a 20% só existem nesta estrutura com descritor de dinâmica pouco ruidoso.
