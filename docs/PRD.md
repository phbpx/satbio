# PRD — satbio

**Projeto:** Predição de indicadores da comunidade de aves em sistemas cabruca por meio de séries temporais de sensoriamento remoto e monitoramento acústico passivo
**Tipo:** Pesquisa independente e voluntária, em ciência aberta · cronograma de referência de 24 meses
**Fonte:** `docs/pre-projeto-bioacustica-inpe.pdf` (pré-projeto de 2 de outubro de 2026)
**Status:** piloto concluído em 2026-10-03 (ver `docs/piloto/semana-4.md`); G1 aprovado de forma condicional: caminho A se a parceria for confirmada até 2026-12-02, senão caminho C

---

## 1. Contexto

Sistemas cabruca mantêm cacau sob árvores de sombra no sul da Bahia e variam em manejo e contexto de paisagem. Duas áreas com cobertura arbórea semelhante podem abrigar comunidades de aves diferentes. A hipótese de trabalho é que o histórico espectral e o contexto da paisagem explicam parte dessa diferença, além do que se vê em uma única imagem. Gravações acústicas validadas fornecem a referência ecológica independente para testar isso.

## 2. Pergunta de pesquisa

> Quanto as séries temporais de vegetação acrescentam à predição de indicadores da comunidade de aves em cabruca, depois de considerar sazonalidade, esforço de gravação e contexto paisagístico?

**Objetivo geral:** avaliar a capacidade preditiva e os limites de séries temporais de sensoriamento remoto distribuídas pelo INPE para indicadores acústicos validados da comunidade de aves em cabruca.

**Objetivos específicos**

1. Construir uma base que vincule local de gravação, período, esforço amostral, detecções e variáveis geoespaciais.
2. Comparar preditores de um período com descritores espectrais temporais e variáveis do entorno.
3. Estimar o erro da identificação automática e sua influência nos indicadores ecológicos.
4. Avaliar a generalização entre áreas independentes e identificar situações de baixa confiabilidade.

## 3. Hipóteses

| ID | Hipótese | Resultado observável |
|---|---|---|
| H1 | Contexto da paisagem | Maior cobertura nativa e menor isolamento associam-se a maior semelhança com comunidades de referência |
| H2 | Informação temporal | Amplitude sazonal e histórico espectral reduzem o erro de predição fora da amostra |
| H3 | Escala espacial | Descritores do entorno acrescentam informação além do ponto de gravação |

Um ganho temporal pequeno ou ausente também é resultado válido: ele delimita o uso do método. Associações entre manejo e aves não serão interpretadas como causais.

## 4. Escopo

**Dentro do escopo**
- Grupo focal: aves vocalizantes.
- Região: sul da Bahia; municípios definidos após confirmar acesso às propriedades.
- Condição ecológica e associações espaciais em um desenho observacional.

**Fora do escopo**
- Medir toda a biodiversidade, abundância de indivíduos ou sucesso de restauração.
- Análise de recuperação ao longo do tempo (exigiria histórico de restauração e observações adicionais).
- Converter índices espectrais diretamente em altura do dossel, biomassa ou biodiversidade.
- Plataforma web ou infraestrutura distribuída.

## 5. Dados

### 5.1 Sensoriamento remoto (INPE)

| Produto | Uso | Limite |
|---|---|---|
| S2-16D-2 (Sentinel-2, Brazil Data Cube) | Fonte principal; 10 m, composição de 16 dias | Bandas com resoluções nativas distintas; verificar cenas válidas por área |
| LANDSAT-16D-1 (Landsat 8/9) | Complementar; 30 m; histórico mais longo | Pixels mistos em áreas pequenas; não unir sensores sem harmonização |
| PRODES Mata Atlântica (TerraBrasilis) | Supressão de vegetação no entorno | Não é medida de biodiversidade nem de manejo |

Acesso pelo catálogo STAC do INPE (`https://data.inpe.br/bdc/stac/v1/`).

**Variáveis candidatas**
- No ponto: NDVI, EVI e um índice de umidade (NIR + SWIR); mediana, amplitude sazonal e variabilidade.
- No entorno: raios de 100, 500 e 1.000 m (fixados antes da avaliação final); cobertura nativa, distância a fragmentos e métricas de borda a partir de um mapa de cobertura validado (não pela inversão do PRODES).

### 5.2 Acústica

| Base | Papel | Observação |
|---|---|---|
| WABAD v4 (Zenodo) | Teste de pipeline e do reconhecedor (auditado) | 9 de 72 sítios no Brasil, nenhum na Bahia; coordenadas por sítio; fuso não declarado; licença divergente (CC BY × CC BY-NC) |
| Soundscape_CCM1_exp01 | Teste do pipeline (auditado) | SP/MG, 2016–2017; rótulos por grupo; sem coordenadas nos arquivos; GPL-3.0 no repositório |
| AnuraSet | Teste de leitura de áudio e rótulos (auditado) | 4 sítios de anuros, 2019–2021; sem coordenadas nas fontes; licença divergente (CC BY × CC0); mudaria o grupo focal |
| Rosa *et al.* 2024 (Zenodo 10556620) | Teste de pipeline e referência de desenho amostral (auditado) | Listas espécie × minuto de aves; PN do Iguaçu (1 parque) e um conjunto costeiro sem estado declarado; sem coordenadas por ponto; sem áudio; CC BY 4.0 |
| Campanha própria ou de parceria em cabruca | Base ecológica final | Depende de acesso, especialista e tamanho amostral |

**Critérios para aceitar uma base ecológica**
- Coordenadas com precisão compatível com a escala; datas com horário e fuso.
- Identidade dos pontos, períodos, esforço e equipamento recuperáveis.
- Áreas independentes em número e distribuição suficientes, com variação ambiental útil.
- Rótulos e seleção de arquivos que permitam interpretar detecções, ausências e vieses.

### 5.3 Desenho amostral em cabruca (proposta inicial)

- 24 a 36 áreas independentes (cabrucas em gradiente de manejo + fragmentos de mata de referência); tamanho final definido por piloto e simulação de poder.
- Unidade independente: propriedade ou fragmento. Pontos na mesma área são subamostras.
- Protocolo: 1 min a cada 5 min, 3 h a partir do amanhecer, 7 dias, 2 campanhas sazonais → 504 min por ponto.
- Estimativa para 30 pontos: ~252 h de áudio, ~80 GB (WAV mono, 44,1 kHz, 16 bits), sem contar cópias e processamento.

## 6. Requisitos do fluxo de processamento

### 6.1 Funcionais

| ID | Requisito |
|---|---|
| RF1 | Consultar o STAC do INPE por área e período e baixar bandas e máscaras de qualidade |
| RF2 | Calcular índices espectrais e descritores temporais por ponto e por raio de entorno |
| RF3 | Ler áudios, aplicar controle de qualidade e rodar um reconhecedor existente (BirdNET ou equivalente) |
| RF4 | Gerenciar amostras de validação manual separadas das usadas para calibrar limiares |
| RF5 | Calcular indicadores ecológicos (principal: distância de Jaccard até a comunidade de referência; secundários: riqueza detectada, especialistas florestais) |
| RF6 | Montar a base analítica por área × campanha e ajustar os modelos M0–M3 |
| RF7 | Validar por grupos de propriedade / blocos espaciais e reportar MAE, RMSE e ganho sobre M0 com incerteza por reamostragem de áreas |
| RF8 | Rodar análises de sensibilidade (limiares, esforço, máscaras de nuvem, escalas) |

### 6.2 Modelo de dados

Tabelas com chaves explícitas e dicionário de dados: `areas`, `pontos`, `campanhas`, `gravacoes`, `deteccoes`, `validacoes`, `variaveis_opticas`, `variaveis_paisagem`.

### 6.3 Reprodutibilidade e rigor (não negociáveis)

- Registrar versão das coleções, data de acesso, IDs de itens STAC, parâmetros de qualidade e decisões de anotação.
- Janelas ópticas terminam na véspera da primeira gravação de cada sítio × campanha (sem informação futura). A véspera, e não o próprio dia, absorve o fuso desconhecido dos relógios dos gravadores; o fim da campanha nunca é usado como corte. Decidido em 2026-10-03.
- Pixel óptico válido: SCL 4, 5 ou 6 na **cena Sentinel-2 de origem** (data dada pela PROVENANCE), todas as bandas presentes, PROVENANCE dentro do período da composição e B02 ≤ 0,10. O SCL do cubo divergiu da cena de origem em 6% dos pixels no piloto e deixa passar nuvem e sombra; a regra só com o SCL do cubo fica como variante de sensibilidade. Decidido em 2026-10-03 (`docs/desenho-analitico.md`, decisão D; evidência em `docs/piloto/semana-3.md`).
- Registrar datas de origem e número de observações válidas da composição.
- Normalização, seleção de variáveis e construção da referência ecológica apenas dentro do treino.
- Áreas e campanhas da mesma propriedade sempre no mesmo grupo de validação.
- Conjunto de teste nunca usado para escolher modelo ou escala.
- Pontuação do reconhecedor não é probabilidade calibrada; não detecção não é ausência.
- Minutos e segmentos não são réplicas espaciais independentes.

### 6.4 Modelos

> **Em revisão.** Esta seção e a definição da resposta (5.3, 6.1 RF5) estão sendo substituídas por [`docs/desenho-analitico.md`](desenho-analitico.md), que fixa resposta, referência, papel das matas, comparações (incluindo o controle M2b) e regras de validação. As decisões abertas de lá precisam ser fechadas antes da coleta definitiva.

| Modelo | Preditores | Mede |
|---|---|---|
| M0 Referência | Época, esforço, controles ambientais | Erro de base sem óptica |
| M1 Um período | M0 + espectrais de uma janela recente | Ganho local |
| M2 Paisagem | M1 + cobertura e configuração do entorno | Ganho espacial (H1, H3) |
| M3 Séries temporais | M2 + amplitude, variabilidade, histórico | Ganho temporal (H2) |

Famílias: regressão regularizada ou aditiva vs. Random Forest; família estatística compatível com a resposta (sem gaussiana automática para contagens).

### 6.5 Tecnologia

Python para STAC, rasters e modelos; R para estatística ecológica quando útil. Sem plataforma web.

## 7. Roadmap

### Fase 0 — Piloto de 30 dias

| Semana | Entrega |
|---|---|
| 1 | ✅ Auditoria do WABAD e dos metadados das bases brasileiras (`docs/bases/`) |
| 2 | ✅ Pequena seleção de áudios processada e vinculada a datas e pontos (`docs/piloto/semana-2.md`) |
| 3 | ✅ Consulta STAC para locais elegíveis; série curta extraída com máscara de qualidade (`docs/piloto/semana-3.md`) |
| 4 | ✅ Inventário de dados, exemplo reprodutível da integração e **decisão sobre a base final** (`docs/piloto/semana-4.md`) |

### Fases do projeto

| Fase | Meses | Entregas | Portão de decisão |
|---|---|---|---|
| 1. Fundação | 1–3 | Revisão bibliográfica, auditoria de metadados, primeira extração óptica, parceria definida | **G1:** base final escolhida (cabruca com parceria / campanha própria / alternativa aberta) |
| 2. Piloto | 4–6 | Piloto de gravação ou amostra existente; validação do reconhecedor; simulação de poder | **G2:** número de áreas e esforço confirmados |
| 3. Coleta | 7–12 | Campanhas sazonais ou consolidação de dados existentes; QC e documentação | **G3:** dados suficientes para as duas campanhas |
| 4. Indicadores | 13–16 | Anotações finais, indicadores ecológicos, séries temporais extraídas | **G4:** incerteza da anotação aceitável para os indicadores |
| 5. Modelagem | 17–20 | Modelos M0–M3, validação espacial, sensibilidade | **G5:** resultados avaliados como confirmatórios ou exploratórios |
| 6. Escrita | 21–24 | Relatório técnico, artigo, publicação de código e metadados permitidos | Publicação |

### Caminhos alternativos (decididos em G1)

> **Decisão do G1 (2026-10-03):** B descartado, porque nenhuma base aberta auditada tem gravações de aves em cabruca ou no sul da Bahia. A é o caminho principal, condicional à confirmação de parceria (UESC ou equivalente) até **2026-12-02**; sem parceria até lá, o projeto segue pelo caminho C. Evidência em `docs/piloto/semana-4.md` e `docs/bases/README.md`.

- **A — Cabruca (principal):** gravações de parceria ou campanha padronizada.
- **B — Integralmente aberto:** se uma base brasileira aberta tiver datas, coordenadas e áreas independentes suficientes; título ajustado ao ecossistema amostrado.
- **C — Metodológico:** se só houver bases com poucos sítios ou rótulos por grupo; estudo de integração e reconhecimento, sem afirmar predição validada de biodiversidade em cabruca.

## 8. Critérios de sucesso

- Base integrada documentada e reproduzível de ponta a ponta.
- Erro do reconhecedor estimado (precisão e sensibilidade, incluindo falsos negativos).
- Ganho de M1, M2 e M3 sobre M0 quantificado fora da amostra, com incerteza.
- Limites de extrapolação documentados; mapas apenas dentro do domínio de treinamento, com incerteza.
- Relatório técnico público e manuscrito submetido.

## 9. Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| Sem acesso a propriedades ou parceria | Inviabiliza o caminho A | Caminhos B ou C decididos em G1 |
| Poucas áreas independentes | Validação fraca | Simulação de poder; reportar como exploratório |
| Nuvens e observações escassas | Séries incompletas | Máscaras de qualidade, registro de observações válidas, Landsat complementar |
| Erro do reconhecedor | Indicadores enviesados | Validação por especialista, limiares calibrados fora do teste |
| Confusão entre manejo, distância da mata e equipamento | Associações espúrias | Seleção balanceada de áreas, equipamento padronizado |
| Licenças e restrições das bases | Limita publicação | Registrar licença por versão; publicar só o permitido |
| Falta de especialista em aves | Validação taxonômica comprometida | Colaboração voluntária com pesquisador(a) ou grupo de ecologia de aves |

## 10. Questões em aberto

- Colaboradores: apoio em sensoriamento remoto e em ecologia de aves (amostragem e validação taxonômica).
- Municípios e propriedades com acesso confirmado.
- Licença efetiva do WABAD (CC BY ou CC BY-NC) e do AnuraSet (CC BY ou CC0); fuso dos horários do WABAD e do Soundscape_CCM1.
- Parceria com o grupo de ecologia de aves da UESC, que já amostrou agroflorestas de cacau no sul da Bahia com pontos de escuta (ver `docs/literatura/bases-acusticas-mata-atlantica.md`).
- Mapa de cobertura validado para as métricas de paisagem (externo ou classificação própria).
- Orçamento (equipamentos, deslocamento, horas de anotação, armazenamento) — não há preços cotados.
- Fontes de apoio para a coleta em campo (equipamentos emprestados, parcerias, pequenos financiamentos).

## 11. Referências

1. Müller J et al. *Nature Communications* 14, 6191, 2023. https://doi.org/10.1038/s41467-023-41693-w
2. INPE. Brazil Data Cube. https://data.inpe.br/bdc/en/data-cube/
3. INPE. STAC S2-16D-2. https://data.inpe.br/bdc/stac/v1/collections/S2-16D-2
4. INPE. TerraBrasilis — PRODES Mata Atlântica. https://www.terrabrasilis.dpi.inpe.br/downloads/
5. Pérez-Granados C et al. WABAD v4. https://doi.org/10.5281/zenodo.20513304 (concept DOI 10.5281/zenodo.14191523)
6. Hilasaca LH et al. Soundscape_CCM1_exp01. https://github.com/LEEClab/soundscape_CCM1_exp01
7. Cañas JS et al. AnuraSet. https://doi.org/10.5281/zenodo.8342596 (concept DOI 10.5281/zenodo.8043209)
8. Cañas JS et al. *Scientific Data*, 2023. https://doi.org/10.1038/s41597-023-02666-2
9. Rosa GLM et al. Data from: Acoustic monitoring of anurans and birds in Tropical biomes. Zenodo, 2024. https://doi.org/10.5281/zenodo.10556620
