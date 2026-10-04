# Desenho analítico — satbio

**Status:** rascunho, 2026-10-03; decisões A, D e E fechadas em 2026-10-03, inferência e estimando de H2 em 2026-10-04; B e C abertas. Responde à revisão externa do projeto feita após o piloto técnico. Substitui a seção 6.4 do PRD quando aprovado. As decisões marcadas **[aberta]** precisam ser fechadas antes da coleta definitiva; depois disso este documento é congelado (versão e data registradas) e qualquer mudança passa a ser registrada como desvio.

Este documento existe porque o PRD descreve bem o que medir, mas não fixa a ligação entre o que será gravado, o indicador ecológico calculado e o que o modelo prevê. Sem essa ligação, um modelo pode ter bom desempenho respondendo a uma pergunta diferente da proposta.

## 1. O que o estudo mede

**Grupo efetivamente estudado.** Aves que vocalizam nas três horas após o amanhecer, detectáveis por gravação passiva e identificáveis pelo reconhecedor validado. Espécies noturnas, pouco vocais ou ativas em outros horários ficam sub-representadas, e os resultados se restringem a esse grupo.

**Decisão A — o que a resposta representa [fechada em 2026-10-03: A1].**

| Opção | O que se prevê | Exige | Risco |
|---|---|---|---|
| **A1. Comunidade detectada sob protocolo padronizado** (recomendada) | A lista de espécies detectadas com esforço, horário, equipamento e reconhecedor fixos | Protocolo idêntico em todas as propriedades; covariáveis de detecção registradas (ruído, chuva, vento, equipamento) | Diferenças de detectabilidade entre ambientes entram na resposta; precisam ser discutidas, não corrigidas |
| A2. Ocorrência ou uso do habitat | Probabilidade de ocupação por espécie, corrigida por detecção imperfeita (e, idealmente, por falsos positivos) | Repetições suficientes por espécie; modelo de observação; mais pressupostos | Com poucas propriedades, só espécies comuns têm dados; se a ocupação usar os preditores ópticos, a regressão sobre ela não é validação independente do satélite |

Escolhida A1, pela escala do projeto. A afirmação do estudo é "o satélite prevê a comunidade detectada sob este protocolo", não "a comunidade presente".

## 2. Resposta principal

**Decisão B — referência ecológica [aberta].**

| Opção | Como funciona | Vantagem | Custo |
|---|---|---|---|
| **B1. Matas de referência independentes** (recomendada, se houver acesso) | Um conjunto fixo de fragmentos de mata, gravados com o mesmo protocolo, forma a comunidade de referência; esses fragmentos nunca são observações do modelo | A referência não muda entre partições e nenhuma área ajuda a construir a própria resposta | Exige campanhas extras fora das cabrucas |
| B2. Referência construída no treino | Em cada partição, a referência é a união das listas das matas do conjunto de treino | Não exige amostra separada | A referência muda entre partições; exige análise de estabilidade e comparação dos modelos sempre com a mesma referência dentro de cada partição |

**Indicador.** Distância de Jaccard entre a lista da propriedade × campanha e a lista de referência, com esforço padronizado: o número de minutos por propriedade × campanha é fixado pelo protocolo antes da coleta, e não pelo menor esforço observado (que deixaria propriedades de teste definirem a resposta das de treino). Como a rarefação dá riqueza esperada, e não uma lista, o Jaccard com esforço padronizado é a média do índice em subamostras repetidas desse número de minutos. A distância é decomposta em substituição e aninhamento (Baselga, 2012) e as duas componentes são reportadas: distância alta por perda de espécies e por troca de espécies têm interpretações ecológicas diferentes, e nenhuma delas equivale automaticamente a degradação.

**Indicador secundário, um só.** Número de espécies especialistas florestais detectadas com o mesmo esforço, com a lista de especialistas definida pela literatura antes da coleta (ex.: classificação usada por Oliveira *et al.* 2026). Não se acrescentam outros desfechos.

**Lista por propriedade × campanha.** União das detecções validadas acima de um limiar fixo do reconhecedor, definido na validação (seção 7) e não ajustado depois.

## 3. Unidades e papel de cada área

- A unidade independente é a **propriedade de cabruca**. Pontos, dias e minutos são subamostras; duas campanhas na mesma propriedade não dobram o n.
- As **matas de referência não entram na avaliação principal.** A avaliação principal é **entre cabrucas retidas**, porque o objetivo é distinguir cabrucas em condições diferentes, não separar mata de cabruca. Uma análise com todos os ambientes pode ser complementar e é reportada como tal.
- **Decisão C — número viável de cabrucas [aberta].** As 24–36 áreas do PRD incluem as matas. O número de cabrucas e de matas depende da parceria (UESC) e define a precisão de H2 (seção 9): pela [simulação](simulacao-dimensionamento.md), com 10 a 30 cabrucas o IC90 do ganho tem largura de 0,4 a 1,0 e H2 fica exploratória; ~60 cabrucas são o mínimo para ver um ganho de ~20%, e 85 a 95 para precisão de ±0,10.

## 4. Hipóteses e comparações

H1 é uma hipótese de **associação**; H2 e H3 são hipóteses de **ganho de predição**. Elas são avaliadas por análises separadas.

| Hipótese | Análise | Comparação |
|---|---|---|
| H1 Contexto da paisagem | Modelo simples de associação (regressão com poucos termos), coeficiente e intervalo de confiança | Sinal e magnitude da associação entre cobertura nativa no entorno e a resposta |
| H2 Informação temporal | Predição em propriedades retidas | **M3 × M2b** (dinâmica) e **M2b × M2** (estabilidade da estimativa) |
| H3 Escala espacial | Predição em propriedades retidas | M2 × M1 |

| Modelo | Preditores |
|---|---|
| M0 | Esforço e covariáveis de detecção (ruído, chuva, equipamento) |
| M1 | M0 + descritores de uma janela recente (última composição válida antes do corte) |
| M2 | M1 + contexto da paisagem |
| **M2b** (novo) | M2 + mediana histórica dos índices, sem amplitude nem mudança |
| M3 | M2b + amplitude robusta e descritor de mudança |

O controle M2b separa dois benefícios possíveis da série: uma estimativa mais estável do estado da vegetação (M2b × M2) e informação sobre dinâmica (M3 × M2b). Só o segundo sustenta a afirmação de que a dimensão temporal acrescenta informação.

**Métrica principal:** erro absoluto médio (MAE) da resposta nas propriedades retidas.

**H2 é uma estimação, não um teste de limiar [fechado em 2026-10-04].** O resultado principal de H2 é a estimativa do ganho de M3 sobre M2b, 1 − MAE(M3)/MAE(M2b), com intervalo de 90%. A largura do intervalo (precisão) é reportada junto, porque com o número de cabrucas viável ela é da ordem do próprio ganho ([simulação](simulacao-dimensionamento.md)).

- **Estimando: o ganho alcançável com o n do estudo.** É o ganho que modelos ajustados com as n cabrucas do estudo teriam em propriedades novas da mesma região. A alternativa, o ganho de população (com modelos ajustados em muitas propriedades), mede se a informação existe no satélite, mas a validação cruzada estima o desempenho do ajuste com cerca de n propriedades, e passar dele ao de população exigiria extrapolar em n, o que os dados não sustentam. Nas simulações o ganho alcançável fica abaixo do de população (5 pontos a menos com 10 cabrucas, 2 com 30), então um ganho alcançável positivo é uma leitura conservadora do de população; o contrário não vale, e um ganho alcançável nulo com poucas cabrucas não descarta informação no satélite.
- **Método de inferência: reamostragem de propriedades com reajuste, intervalo básico.** Cada réplica sorteia propriedades (ou grupos de propriedades vizinhas) com reposição e refaz a validação por propriedade retida, com as cópias da retida fora do treino; o intervalo é 2·ganho − quantis das réplicas, o que desconta o deslocamento para baixo das réplicas (cada uma treina com ~63% de propriedades distintas). Escolhido por ter a cobertura mais próxima de 90% contra o estimando: 90% no geral e 85% a 100% por cenário, contra 74% do método anterior (reamostragem dos erros fixos), 84% da validação cruzada repetida com correção de variância e 97% do intervalo percentil (conservador). Na análise real, com pelo menos 2.000 réplicas. Detalhes em [`simulacao-dimensionamento.md`](simulacao-dimensionamento.md).
- **Análise complementar:** teste de permutação do descritor de dinâmica entre propriedades (valor-p unilateral para ganho > 0). Tem o tamanho correto (4,6% a 5% para α = 5%) e mais poder que o intervalo, mas não diz o tamanho do ganho; é reportado ao lado, não no lugar.

**Decisão E — ganho mínimo relevante, como regra de interpretação [fechada em 2026-10-03; papel revisto em 2026-10-04].** O ganho é relevante se for de pelo menos 10% do MAE do modelo de base de cada comparação (para H2, 10% do MAE de M2b). A decisão E não decide H2; ela diz como ler o intervalo. As leituras, fixadas antes dos dados:

| Leitura | Quando | O que se escreve |
|---|---|---|
| Ganho relevante | Intervalo inteiro ≥ 10% | A dinâmica acrescenta um ganho relevante com este n |
| Positivo, tamanho incerto | Intervalo exclui zero, estimativa ≥ 10%, limite inferior < 10% | Há ganho; não se sabe se é relevante |
| Positivo pequeno | Intervalo entre 0 e 10% | Há ganho, abaixo do relevante |
| Relevante descartado | Limite superior < 10% e intervalo inclui zero | Um ganho relevante é improvável com este n; não é evidência de que a informação não existe no satélite |
| Inconclusivo | Os demais casos (o intervalo inclui zero e 10%) | O estudo não tem precisão para dizer; reporta-se a largura do intervalo |

## 5. Descritores (limitados e ligados a hipóteses)

Todos calculados na janela de 12 meses que termina na véspera da primeira gravação, sobre composições válidas.

| Descritor | Índice | Hipótese ecológica |
|---|---|---|
| Mediana anual | NDVI | Estado médio do dossel (quantidade de folhagem verde) |
| Mediana anual | NDMI | Umidade e estrutura do dossel, menos saturado que o NDVI em vegetação densa |
| Amplitude robusta (P90 − P10) | NDVI | Variação sazonal de folhagem; pode refletir composição das árvores de sombra ou manejo |
| Mudança recente (último trimestre − mediana anual) | NDMI | Perturbação recente, como raleamento de sombra ou roçada. **Ressalva:** quando os cortes caem em meses diferentes, essa diferença mistura fase sazonal com perturbação (visto no piloto: o NDMI cai de agosto a novembro nos quatro sítios). Antes de congelar, decidir entre calcular a mudança como anomalia em relação ao mesmo trimestre de anos anteriores ou alinhar as campanhas no calendário |
| Cobertura nativa a 500 m | Mapa de cobertura (MapBiomas Cacau, a confirmar) | Contexto da paisagem (H1, H3) |

Os índices não captam estrutura abaixo do dossel. Para interpretar sucessos e fracassos do satélite, cada propriedade registra em campo: densidade de árvores de sombra, cobertura do dossel, intensidade de manejo (roçada, poda, adubação, densidade de cacaueiros) e histórico conhecido de intervenção. Essas variáveis não entram nos modelos de predição; servem para interpretação e para a análise de associação.

Um preditor útil pode estar funcionando como substituto de outro fator; desempenho preditivo não comprova o mecanismo da tabela.

## 6. Regras ópticas

- **Validade do pixel — Decisão D [fechada em 2026-10-03].** O pixel vale se o SCL da **cena de origem** (a cena Sentinel-2 L2A da data dada pela PROVENANCE) for 4, 5 ou 6 e se B02 ≤ 0,10. Se a cena de origem não for encontrada, o pixel é inválido. A conferência do piloto mostrou que o SCL do cubo diverge da cena de origem em 6% dos pixels aceitos e que o teste B02 pega nuvens, mas não sombras (`docs/piloto/semana-3.md`). A regra só com o SCL do cubo fica como análise de sensibilidade.
- **Composição usada.** Uma composição entra nos descritores se pelo menos 5 dos 9 pixels da janela 3×3 forem válidos; usa-se a mediana dos pixels válidos. O trimestre da composição é o da data de observação do pixel central (PROVENANCE). Exigir 9 de 9, ou o pixel central válido, fica como análise de sensibilidade (bordas de nuvem e sombra podem passar com 5 a 8 pixels).
- **Cobertura mínima.** A série só entra se tiver pelo menos uma composição usada em cada trimestre da janela e pelo menos 10 no total; caso contrário, a propriedade × campanha fica sem descritores temporais e isso é reportado. A mudança recente exige pelo menos 2 composições no último trimestre; com menos, fica vazia.
- **Robustez a lacunas.** Antes da análise confirmatória, séries bem observadas são reduzidas artificialmente (retirando composições ao acaso e por trimestre) para medir quanto os descritores variam com a perda de imagens. Se a amplitude variar mais que a diferença entre propriedades, ela sai do conjunto principal.
- **Escala espacial do pixel.** Mediana da janela 3×3 em volta do ponto de cada gravador (coordenada por gravador, não por propriedade).

## 7. Validação do reconhecedor

- **Filtro de espécies:** a análise principal usa uma lista regional fixa (espécies com ocorrência conhecida no sul da Bahia), igual para todas as propriedades e datas. O filtro do BirdNET por localização e semana usa informação externa de ocorrência e pode introduzir estrutura geográfica e sazonal nas listas que depois serão previstas pelo satélite; ele entra só como comparação.
- **Validação por trecho:** amostra estratificada por espécie, classe de confiança, horário e ruído, mais trechos sem detecção automática (falsos negativos). As probabilidades de seleção de cada estrato são registradas, e as estimativas de precisão e sensibilidade são ponderadas por elas.
- **Validação no nível do indicador:** num subconjunto de propriedades × campanhas, a lista automática é comparada com a lista feita por especialista sobre os mesmos minutos. Reporta-se o erro do indicador final (diferença de Jaccard e de riqueza), não só o erro por trecho.
- O limiar do reconhecedor é fixado nessa validação, com áudios separados dos usados na avaliação dos modelos.

## 8. Protocolo de gravação

- Proposta inicial mantida (1 min a cada 5 min, 3 h após o amanhecer, 7 dias por campanha), a ser validada no piloto de campo.
- O piloto de campo mede curvas de acumulação de espécies, estabilidade do indicador e repetibilidade entre dias, e compara o ganho de acrescentar propriedades, pontos por propriedade, dias e horários, em vez de só acumular minutos.
- Número de pontos por propriedade fixado no piloto, com coordenada de cada gravador.
- **Campanhas definidas por calendário, não por "seca" e "chuva".** O sul da Bahia não tem estação seca bem definida (Oliveira *et al.* 2026). Proposta: duas campanhas com cerca de seis meses de intervalo, nas mesmas datas para todas as propriedades (ou em rodízios curtos balanceados).

## 9. Análise principal e dimensionamento

- **Uma análise principal simples:** regressão linear regularizada com os descritores da seção 5, validação deixando uma propriedade de fora (ou grupos de propriedades vizinhas, se houver dependência espacial entre elas). Random Forest e modelos aditivos entram como análises secundárias, reportadas como tal.
- Nenhuma escolha (índices, escalas, janelas, hiperparâmetros) é feita com as propriedades retidas.
- **A validação corresponde à aplicação:** prever uma propriedade nova da mesma região. Transferência para outra paisagem ou para outro ano não é testada pelo desenho e não será afirmada.
- **Intervalo do ganho** pela reamostragem de propriedades com reajuste (intervalo básico, seção 4), com as réplicas sorteando os mesmos grupos usados na validação.
- **Dimensionamento por simulação, antes da coleta** ([`simulacao-dimensionamento.md`](simulacao-dimensionamento.md)): simula o fluxo completo (heterogeneidade entre propriedades, detecção imperfeita, erro do reconhecedor, lacunas ópticas e validação por propriedade retida) e o método de inferência adotado, e mede a precisão do ganho M3 × M2b em função do número de cabrucas. O critério de dimensionamento é a precisão (largura do intervalo), não a chance de "confirmar" o ganho. O resultado fecha a Decisão C.

## Decisões abertas

| | Decisão | Depende de | Recomendação |
|---|---|---|---|
| A | Comunidade detectada ou ocupação | Escala e esforço possíveis | **Fechada:** A1, comunidade detectada |
| B | Referência independente ou construída no treino | Acesso a matas com o mesmo protocolo | B1, se a parceria permitir |
| C | Número de cabrucas e de matas | Parceria (UESC), recursos, simulação | Com 10–30 cabrucas, H2 é exploratória; ~60 para ver ~20%, 85–95 para ±0,10 (simulação de 2026-10-04). Fechar com o número que a parceria oferecer |
| D | Regra de validade do pixel | Custo da consulta à cena de origem | **Fechada:** SCL da cena de origem + B02 ≤ 0,10 |
| E | Ganho mínimo relevante | Julgamento ecológico | **Fechada:** 10% do MAE do modelo de base de cada comparação; desde 2026-10-04, regra de interpretação do intervalo (seção 4) |
| — | Inferência e estimando de H2 | Simulação | **Fechado em 2026-10-04:** ganho alcançável com o n do estudo; reamostragem de propriedades com reajuste. Aberto: intervalo básico (atual) ou percentil (nunca subcobre com ganho) |

## Referências desta seção

- Baselga A. 2012. The relationship between species replacement, dissimilarity derived from nestedness, and nestedness. *Global Ecology and Biogeography* 21: 1223–1232. https://doi.org/10.1111/j.1466-8238.2011.00756.x
- Oliveira IS, Bandeira EC, Figueiredo MG, Morante-Filho JC. 2026. *Ornithology Research* 34: 13. https://doi.org/10.1007/s43388-026-00275-2
- Bouckaert RR, Frank E. 2004. Evaluating the replicability of significance tests for comparing learning algorithms. *PAKDD 2004*, LNCS 3056: 3–12. https://doi.org/10.1007/978-3-540-24775-3_3
- Nadeau C, Bengio Y. 2003. Inference for the generalization error. *Machine Learning* 52: 239–281. https://doi.org/10.1023/A:1024068626366
- Roberts DR *et al.* 2017. Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography* 40: 913–929. https://doi.org/10.1111/ecog.02881
