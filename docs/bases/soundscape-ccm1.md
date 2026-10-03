# Auditoria: Soundscape_CCM1_exp01

Papel proposto: base de teste do pipeline (não base ecológica final).

Método: leitura só de cópias locais das fontes primárias obtidas em 2026-10-03 do repositório GitHub, sem acesso à web nesta rodada. Os áudios não foram abertos. O artigo (Ecological Indicators, DOI 10.1016/j.ecolind.2020.107316) é pago e não foi obtido. Isso é uma limitação: tudo o que depende do artigo está "não verificado".

Os arquivos de origem ficam em `scratchpad/fontes/ccm1/` (fora do git): `repo.json`, `tree.json`, `README.md`, `labels_script.R`, `audio_dataset`, `root_labels.csv`, `birds_species_tags/`.

## Identificação

| Item | Valor | Fonte |
|---|---|---|
| Repositório | https://github.com/LEEClab/soundscape_CCM1_exp01 | `repo.json` |
| Criado / último push | 2021-01-30 / 2021-02-05 (`updated_at` 2025-04-05, sem push de conteúdo) | `repo.json` |
| Branch | `main`; commit/tag/release exatos: não verificado (só a API do repo foi guardada) | `repo.json` |
| DOI do artigo | 10.1016/j.ecolind.2020.107316 | `README.md` |
| DOI do conjunto de dados (Zenodo etc.) | não consta no README; não verificado | `README.md` |
| Data de acesso | 2026-10-03 | tarefa |
| Citação sugerida pelo README | Hilasaca, Gaspar, Ribeiro & Minghim (2021), Soundscape_CCM1_exp01 | `README.md` |

## Origem e desenho (README.md)

- Projeto LTER-CCM (Corredor Ecológico Cantareira-Mantiqueira), transição entre nordeste de SP e sul de MG. Mata Atlântica, mas não o sul da Bahia, e sem cabruca: o README descreve floresta em sucessão, agricultura, eucalipto, brejos, pastos e áreas urbanas.
- Gravadores Song Meter SM3 a 1,5 m em árvores, 44,1 kHz, 16 bits, mono.
- README: 22 paisagens, 3 sítios por paisagem (floresta, pasto, brejo). Cobertura florestal de 16% a 86%.
- Divergência: os nomes dos arquivos de aves têm 23 códigos de paisagem distintos (LEEC02 a LEEC49, com lacunas), não 22. Causa não verificada (talvez erro do README ou código extra).

## Critérios da seção 5.2 do PRD

| Critério | Resultado | Evidência |
|---|---|---|
| Coordenadas | Não há em nenhum arquivo obtido. Nenhum termo de latitude, longitude, UTM ou coordenada em `README.md`, `labels_script.R`, `root_labels.csv`, `audio_dataset`, nem nas tabelas Raven. O repositório tem um mapa (`figure/ajust_map_2021_01_d05_500dpi.png`, 3,5 MB, listado em `tree.json`); não foi aberto. Coordenadas por paisagem ou sítio: não verificado (possivelmente no artigo ou sob pedido aos autores). | greps nos arquivos; `tree.json` |
| Data e horário | Existem no nome do arquivo (ver abaixo). Fuso: não documentado em nenhum arquivo; não verificado. | nomes de arquivo; `README.md` |
| Identidade dos pontos, período, esforço, equipamento | Parcial. Equipamento e taxa de amostragem estão no README. Código de paisagem e data/hora estão no nome. Sufixos `ma/aa/br` e `min_02/10/15` não têm legenda no README (`labels_script.R` só os chama de "ambiente" e extrai os caracteres; ver abaixo). Esforço por ponto (dias gravados, ciclo de gravação): não verificado. | `labels_script.R`, nomes |
| Número de áreas independentes | Ver abaixo: 22 ou 23 paisagens, longe da Bahia. Número bruto alto, mas fora do bioma-alvo do projeto. | README; nomes |
| Rótulos e seleção de arquivos | Presença por grupo; seleção dos minutos não é aleatória nem sistemática por documentação (ver abaixo). Não permite interpretar ausência. | `README.md`, `root_labels.csv` |

## Pontos, datas e horários (decodificados dos 822 nomes de arquivo de aves)

Padrão do nome: `LEECnn__0__AAAAMMDD_HHMMSS_xx_min_NN.Table.1.selections.txt`. A decodificação segue as posições que `labels_script.R` usa (paisagem = caracteres 1-6, data 12-19, hora 21-26, ambiente 28-29). O significado do `__0__` (canal?) e do sufixo `min_NN` não está documentado.

- Os 822 nomes seguem o padrão; 0 exceções.
- Paisagens distintas: 23 (LEEC02 a LEEC49). Arquivos de aves por paisagem: de 11 (LEEC02, LEEC04) a 51 (LEEC33).
- Datas: de 2016-10-19 a 2017-01-28, em 97 dias distintos. 69 dias em 2016 e 28 em 2017. Por mês (dias): out/2016 13, nov 30, dez 26, jan/2017 28.
- Horários de início dos minutos de aves: 05:00 a 08:00, em 5 horários distintos (05:00, 05:45, 06:30, 07:15, 08:00). Ciclo de 45 min.
- Todos os rótulos (aves, anuros, insetos): 2016-10-19 a 2017-01-28. Insetos: 20 datas do conjunto em 2016-10-19 a 2016-12-11 (calculado dos nomes); anuros começam às 18h e vão até 22h.
- Fuso: nenhum arquivo cita fuso (grep de timezone, UTC, GMT, fuso sem resultado). Provavelmente horário local, mas isso é inferência não verificada. Horário de verão no Brasil em 2016-17: não verificado para esta base.
- Período 2017+: só parcial. 28 dias de aves (jan/2017) estão em 2017; a maior parte (69 dias) é de 2016. Para o teste STAC da semana 3, usar apenas as datas de 2017 reduz a amostra a janeiro. A disponibilidade das coleções do BDC antes de 2017 não foi verificada nesta rodada; as janelas de imagem devem terminar na data do áudio, por regra do projeto.

## Rótulos

- Nível: grupo. `root_labels.csv` tem 2.277 linhas com os rótulos `frogs`, `birds`, `insectos` (615, 822, 840), nos nomes de pasta `frogs/`, `birds/`, `insects/`. Confere com o README.
- Regra (README): para aves e anuros, todo minuto com presença de sinal acústico foi rotulado como ocorrência. Para insetos, só minutos com predomínio de vocalização de inseto. Ou seja, o conjunto foi montado de minutos com presença, em três classes; não há classe "ausência" nem minutos negativos.
- Método de seleção dos minutos (por que 05:00-08:00, por que esses dias): não documentado nos arquivos; possivelmente no artigo. Não verificado.
- Rotulagem em Raven Pro 1.5 (README).
- Aves, nível de espécie parcial: as 822 tabelas Raven têm coluna `species` com códigos de 8 letras (por exemplo `vire_chiv`, `zono_cape`, `basi_culi`, `tang_saya`). Contagem: 3.952 seleções, 232 valores distintos, incluindo `ni`, `ni1`, `na`, `biof_inseto`, `biof_ave_gallus_gallus` (ruído biofônico, não ave silvestre). O README não explica os códigos nem a taxonomia; códigos de espécie não são o rótulo oficial do repositório (`root_labels.csv` é por grupo). Tratar como tags, não como lista validada de espécies. Concordância com um especialista: não verificado.
- Os 822 nomes do `root_labels.csv` para aves correspondem um a um às 822 tabelas (822/822).
- Avaliação de qualidade (revisão por mais de um observador, taxa de erro): não verificado.
- Não há caixas por vocalização usáveis como verdade-terreno sem checagem: as tabelas guardam seleções com tempo e frequência, sem confiança.

## Licença

- Repositório: GPL-3.0 (`repo.json`, campo `license`; arquivo `LICENSE` de 35.149 bytes em `tree.json`).
- Áudios: `audio_dataset` (e `audio_raw/audio_dataset` no repo, 77 bytes) só aponta uma URL de pasta do Google Drive (`https://drive.google.com/drive/u/1/folders/1g5ySgNlztdOWOypTPMoksGgk3qEKZzHb`). A pasta não foi aberta. Nenhuma licença ou termo de uso próprio foi encontrado no repositório. Licença do Drive: não verificado.
- GPL-3.0 é licença de software; aplicá-la a áudio e rótulos é ambíguo. Licença no artigo: não verificado (pago). Para redistribuir, pedir confirmação aos autores.
- Dependência frágil: os áudios estão num Drive pessoal, sem DOI nem checksum; o link pode quebrar.

## Estrutura do repositório (tree.json)

`LICENSE`, `README.md`, `audio_raw/audio_dataset`, `figure/` (mapa), `r_script/Rscript_labels_standardization_2021_02_d05.R`, `root_labels_group/` (CSV de rótulos raiz, `anurans_species_tags.zip`, `birds_species_tags.zip`, `insect_group_tags.zip`). Os nomes diferem dos arquivos locais (`root_labels.csv`, `labels_script.R`, `birds_species_tags/`): a correspondência exata com o CSV/zip do repositório não foi checada byte a byte. Conferir antes de citar.

## Veredito

Papel sugerido: base de teste do pipeline (ingestão de áudio, nomes com data/hora, janelas temporais, validação agrupada por paisagem). Não serve como base ecológica final: fica fora do sul da Bahia, não tem cabruca, rótulos são de presença por grupo e sem ausência, seleção de minutos não documentada, coordenadas e fuso ausentes nas fontes obtidas.

Uso para o teste STAC da semana 3: limitado. Sem coordenadas não há como extrair séries de imagem; só se os autores fornecerem localização ou se o mapa puder ser georreferenciado de forma defensável (não recomendado como ponto exato). Para testar só a mecânica (consulta STAC, janelas, máscaras) bastam coordenadas aproximadas de uma paisagem, com a ressalva de que o resultado não validaria nada ecológico.

Para a validação agrupada, a unidade independente é a paisagem (22/23), não o sítio nem o minuto (regra do projeto).

## Perguntas abertas (para o portão G1)

1. Quais são as coordenadas das paisagens ou sítios e com que precisão? Estão no artigo ou só com os autores?
2. Qual o fuso dos horários dos nomes (local, UTC-3 ou UTC) e houve horário de verão?
3. Por que 22 paisagens no README e 23 códigos nos arquivos de aves?
4. O que significam `ma`, `aa`, `br` e `min_02/10/15`? A associação com floresta/pasto/brejo não está escrita.
5. Como os minutos foram escolhidos (amostragem, filtro de qualidade, janelas 05-08 h para aves)? Há minutos sem ave descartados?
6. Qual a licença dos áudios e rótulos? O Drive tem termos próprios? GPL-3.0 vale para os dados?
7. Os códigos de espécie das tabelas Raven são confiáveis e há tabela de códigos?
8. Os áudios do Drive estão acessíveis e completos? Existe cópia com DOI?
9. As coleções do BDC cobrem o período de 2016? Se não, só janeiro de 2017 serve ao teste da semana 3.
10. O artigo diz algo sobre esforço (dias gravados por sítio) que mude esta avaliação? Não obtido.
