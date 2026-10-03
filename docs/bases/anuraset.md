# Auditoria: AnuraSet

Data da auditoria: 2026-10-03. Fontes primárias lidas em cópia local, obtidas em 2026-10-03 (diretório de trabalho da sessão, `fontes/anuraset/`). Nenhuma consulta web nesta rodada. Os áudios (`raw_data.zip` ~7,2 GB, `anuraset.zip` ~11,4 GB) não foram baixados.

Siglas de fonte: ZJ = `zenodo.json` (API do Zenodo); ZD = `zenodo_descricao.txt`; WL = `weak_labels.csv`; SP = `species.csv`; SL = `strong_labels/`; ART = `artigo.txt` (Sci Data, 10.1038/s41597-023-02666-2). "Calculado" significa contagem feita por mim sobre os arquivos de SL ou WL.

## Identificação

| Item | Valor | Fonte |
|---|---|---|
| DOI do registro | 10.5281/zenodo.8342596 | ZJ |
| Concept DOI (todas as versões) | 10.5281/zenodo.8043209 | ZJ |
| Publicação | 2023-06-16 (registro criado 2023-09-13, atualizado 2023-09-16) | ZJ |
| Versão | Registro é a versão de índice 2 (`is_last: True`) do concept; `revision` = 4; campo `version` vazio | ZJ |
| "v3" citado no PRD | Não confirmado. Nenhuma fonte rotula "v3". Ver pergunta 1 | ZJ, ART |
| Artigo | Sci Data 10, 771; recebido 2023-06-20, aceito 2023-10-19, publicado 2023-11-06 | ART |
| Arquivos | species.csv (1,6 kB), weak_labels.csv (187 kB), strong_labels.zip (584 kB), raw_data.zip (7,21 GB), anuraset.zip (11,36 GB) | ZJ |
| Título | AnuraSet: A dataset for benchmarking neotropical anuran calls identification in passive acoustic monitoring | ZJ |
| Data de acesso | 2026-10-03 | Pedido |

Observação: o tipo de recurso no Zenodo está como "Peer review / publication" (ZJ), aparentemente erro de cadastro, sem efeito prático.

## Licença

- Zenodo: campo de licença `cc-by` (CC BY 4.0), `access_right: open` (ZJ). O campo `rights` está vazio.
- Artigo: dados "under the CC0 license" / "Public Domain Dedication license (CC0)", e código sob MIT (ART, seções Background e Data Records/Code availability).
- **Divergência confirmada: Zenodo diz CC BY, artigo diz CC0.** Tratar o registro do Zenodo como o termo vigente do depósito até esclarecer; no caso mais restritivo, exige-se atribuição. Para um teste de pipeline não muda o uso, mas registrar a atribuição: Cañas et al. 2023.
- Licença do repositório GitHub (MIT segundo o artigo): não verificado, repositório não consultado nesta rodada.

## Critérios da seção 5.2 do PRD

### 1. Coordenadas, datas, horários e fuso

- **Coordenadas: não verificado.** Nenhuma coordenada aparece no texto do artigo, nem em ZJ, WL ou SP. O artigo remete à Fig. 2a (mapa) sem coordenadas numéricas (ART). O README de `anuraset.zip` e o repositório GitHub podem conter, mas não foram lidos. Tampouco consta estado ou município: só o bioma (ART).
- **Biomas (ART):** Cerrado (INCT17, INCT41) e Mata Atlântica (INCT20955, INCT4). Estados: não verificado.
- **Fuso:** BRT (UTC-3), pelo exemplo do artigo ("INCT20955_20190830_231500.wav ... 30 August 2019 at 23:15 (BRT time zone)"), ART. Se houver horário de verão em algum sítio, não consta: não verificado.
- **Formato do nome:** `{site}_{AAAAMMDD}_{HHMMSS}` (ZD, ART). Todas as 1.612 correspondem entre SL e WL (calculado).
- **Faixa de datas por sítio** (calculado a partir dos nomes em SL; WL dá as mesmas faixas):

| Sítio | Minutos anotados | Primeira data | Última data | Dias distintos | Meses com dados |
|---|---|---|---|---|---|
| INCT4 (INCT04 em WL) | 420 | 2019-10-05 | 2021-01-05 | 80 | 2019-10 a 12 (poucos dias), 2020-01 a 03, 2020-10 a 12, 2021-01 |
| INCT17 | 354 | 2019-11-13 | 2020-11-29 | 73 | 2019-11 a 2020-03, 2020-11 |
| INCT20955 | 472 | 2019-09-04 | 2020-04-27 | 111 | 2019-09 a 2020-04, contínuo |
| INCT41 | 366 | 2020-01-26 | 2021-01-17 | 61 | 2020-01, 2020-02, 2020-10 a 12, 2021-01 |

- **Horários:** minutos sempre em :00, :15, :30 e :45 (calculado), coerente com "um minuto a cada 15 min" (ART). Só noite, de 17h a 05h (calculado), coerente com a amostragem "de 1 h antes do pôr do sol até 1 h antes do nascer" (ART). Nenhuma gravação diurna. Anomalia: INCT17 tem horários terminando em :0001 no segundo campo (ex.: HH0001), isto é, minuto "00" com segundo "01", e não é múltiplo de 15 min; não investigado.
- **Cobertura temporal para Sentinel-2:** todas as datas são de 2019 a 2021, ou seja, posteriores a 2017 e dentro da era Sentinel-2 (calculado). Se o cubo S2-16D-2 cobre os tiles dos sítios: **não verificado** (sem coordenadas, sem consulta STAC). Notar que cada sítio tem meses descontínuos, e a janela de imagens deve terminar na data de cada campanha.

### 2. Identidade dos pontos, períodos, esforço e equipamento

- Pontos: quatro, identificados por código INCT (ART). Um gravador por sítio, na margem de um corpo d'água, a ~1,5 m do solo (ART).
- Equipamento: Wildlife Acoustics SM4, microfone omnidirecional, 22.050 Hz, 16 bits, estéreo, ganhos de 10 e 16 dB nos dois canais (ART).
- Esforço de gravação: 1 min a cada 15 min, 24 h por dia, ou 1,6 h/dia (ART). Esforço efetivo por sítio (dias de gravação totais, falhas): não verificado. O que existe nas fontes é só o subconjunto anotado.
- Inconsistência de identificadores: a coluna `MONITORING_SITE` de WL usa "INCT04", mas os nomes de arquivo, as pastas de SL e `AUDIO_FILE_ID` usam "INCT4" (calculado). O artigo usa as duas grafias (INCT4 na Data Collection, INCT04 na Step 2). Cuidado em junções.
- Não há tabela de metadados de sítio (coordenadas, instalação, proprietário) entre os arquivos de ZJ (ZJ).

### 3. Áreas independentes, número e distribuição

- **Sítios no Brasil: 4** (ART, calculado). O artigo diz "country-wide collaborative PAM program across Brazil".
- Biomas: 2 sítios no Cerrado e 2 na Mata Atlântica (ART). Se algum sítio da Mata Atlântica está no sul da Bahia ou em cabruca: **não verificado**; sem estado nem coordenadas nas fontes lidas. Nada nas fontes sugere cabruca; os sítios são margens de corpos d'água (ART).
- Os 1.612 minutos são subamostras de 4 unidades. Pela regra do projeto, a unidade independente é o sítio, logo n = 4 para validação espacial. Isso não é suficiente para estimar generalização espacial, qualquer que seja o número de segmentos (93.378 amostras de 3 s em `anuraset.zip`, ZD).

### 4. Rótulos e seleção de arquivos

- **Nível:** espécie, mas de **anuros**, não de aves (ART, SP). 42 espécies, 12 gêneros, 5 famílias (ART; SP tem 41 linhas de dados mais cabeçalho, 42 linhas no total, conferir). 42 colunas de espécie em WL, todas com ao menos uma detecção (calculado).
- **Rótulos fracos (WL):** 1 linha por minuto, 1 coluna por espécie, valor 0 = ausência, 1 = baixa, 2 = moderada, 3 = alta atividade, segundo o Amphibian Calling Index (ZD, ART). Contagem de células (calculado): 0 = 63.967; 1 = 2.373; 2 = 1.014; 3 = 350.
- **Rótulos fortes (SL):** 1 arquivo .txt por minuto; linha com início (s), fim (s) e `ESPÉCIE_QUALIDADE` (H, M ou L) separados por tab (ZD, ART, calculado). 16.069 linhas no total; o artigo diz ~16.000 "time boxes". 3 linhas fogem do padrão de 3 colunas (2 com 4 campos, 1 com 1 campo), não investigadas. `strong_labels.zip` extrai para `strong_labels/strong_labels/<sítio>/`, aninhado.
- **Seleção dos minutos:** amostra estratificada por sítio e por período (ART, Step 1): meses da estação reprodutiva informados pelos investigadores principais (3 a 6 meses) e noite (de 1 h antes do pôr do sol a 1 h antes do nascer); dentro dos estratos, 300 a 600 arquivos sorteados aleatoriamente por sítio. Resultado: 420, 354, 472 e 366 (ART, calculado, confere). Os meses são definidos pelo investigador local, não é amostragem de todo o ano. Total: 1.612 minutos, 26,87 h (ART).
- **Ausências:** WL registra 0 explicitamente. 393 minutos têm todas as espécies em 0 (24,4%), e 406 arquivos de SL estão vazios (calculado); os 393 minutos sem detecção estão entre os 406 vazios, ficando 13 arquivos vazios em SL com algum valor não zero em WL (calculado, não investigado). Ausência é ausência de chamado de anuro anotado por especialistas, sob amostragem noturna na estação reprodutiva, em um ponto à beira d'água: não é ausência da espécie no sítio. A fração de minutos com detecção varia por sítio: INCT17 98%, INCT20955 93%, INCT41 66%, INCT04 46% (calculado). Não há categoria "incerto" em WL; a qualidade L/M/H existe só nos rótulos fortes (ART).
- Anotadores: rótulos fracos por herpetólogos e especialistas locais; rótulos fortes por uma única herpetóloga (MPTG) (ART). Concordância entre anotadores: não verificado.
- **Pré-processamento (`anuraset.zip`, não baixado):** janelas de 3 s com passo de 1 s, rótulo multi-rótulo se qualquer trecho de chamado cai na janela, filtro Butterworth de ordem 5 (ART).

## Cobertura Sentinel-2 / S2-16D-2 (teste de integração STAC)

- Datas de 2019-09 a 2021-01 (calculado em SL e WL): dentro do período Sentinel-2.
- Coordenadas ausentes das fontes lidas: não dá para escolher o tile nem consultar o STAC. **Não verificado.**
- Os locais ficam em duas janelas de ~4 a 6 meses por sítio e poucas campanhas, o que serve para testar janela até a data da campanha e rastreabilidade, não para modelar.

## Veredito

- **Base ecológica final: não.** Falha o critério do grupo focal (anfíbios, não aves) e o critério 3 (4 sítios, 2 por bioma, sem evidência de Mata Atlântica do sul da Bahia nem de cabruca). Os 1.612 minutos e 93.378 amostras não compensam n = 4 áreas independentes.
- **Teste de pipeline: sim, com ressalvas.** Serve para testar leitura de nomes de arquivo, decodificação de data, hora e fuso (BRT), junção de rótulos fracos e fortes, e o desenho de janelas sem vazamento temporal. Só serve para o passo STAC/cubo depois de obter as coordenadas (README de `anuraset.zip` ou GitHub, ainda não lidos). Não usar para estimar o ganho do sensoriamento remoto: n = 4 sítios.
- Papel sugerido: teste de pipeline (pré-processamento de áudio e rótulos, junção temporal), condicionado às coordenadas.

## Perguntas abertas (alimentam o portão G1)

1. A versão citada no PRD ("v3") não bate com o Zenodo: o registro é a versão de índice 2 do concept, `revision` 4, sem campo de versão. Houve versões 1 e 3? Qual é a mais recente do concept 10.5281/zenodo.8043209 e o que mudou? O PRD (referência 7) precisa ser corrigido para "versão de índice 2 do registro 8342596" ou equivalente.
2. Coordenadas, estados e propriedade dos 4 sítios: constam no README de `anuraset.zip`, no GitHub (soundclim/anuraset) ou na Fig. 2a? Algum está na Mata Atlântica do sul da Bahia? Há restrição de divulgação?
3. Licença: CC BY (Zenodo) ou CC0 (artigo)? Vale perguntar aos autores ou conferir o histórico do registro; a licença do GitHub também não foi vista.
4. Os 13 arquivos de rótulos fortes vazios com valor não zero em WL, as 3 linhas fora do padrão em SL e o horário ":0001" de INCT17 são erro de dado ou convenção?
5. Horário de verão ou outro fuso além de BRT em algum sítio? O artigo só dá um exemplo.
6. Os tiles dos sítios têm cenas válidas no S2-16D-2 nos períodos de gravação (2019-09 a 2021-01)?
7. Esforço total de gravação por sítio (dias com gravador ativo): só existe o subconjunto anotado nas fontes lidas.
