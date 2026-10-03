# Auditoria: WABAD v4

Auditoria da semana 1 do piloto, refeita a partir de fontes primárias baixadas em 2026-10-03 (data de acesso). Substitui a versão anterior, que era parcial e baseada em resultados de busca. Os áudios (zips por sítio) não foram baixados; tudo abaixo vem dos arquivos de metadados, do registro do Zenodo e do texto do artigo. Onde a fonte não responde, está escrito "não verificado".

Siglas de origem: ZJ = `zenodo.json` (API do Zenodo); ZD = `zenodo_descricao.txt`; RD = `README.txt` do registro; MD = `Metadata.csv`; PA = `Pooled_annotations.csv`; ART = `artigo.txt`.

## Identificação

| Item | Valor | Origem |
|---|---|---|
| Título | WABAD: A World Annotated Bird Acoustic Dataset for Passive Acoustic Monitoring | ZJ |
| DOI da versão | 10.5281/zenodo.20513304 | ZJ |
| DOI conceito | 10.5281/zenodo.14191523 | ZJ. A versão anterior deste documento citava ...14191524, vinda de resumo de busca: está errada, vale o ZJ |
| Rótulo de versão | O campo `version` do ZJ é nulo; "v4" vem apenas do pedido/PRD. Não verificado no registro | ZJ |
| Publicação / modificação | 2026-06-02 (publication_date; created e modified 2026-06-02) | ZJ |
| Acesso | `open` | ZJ |
| Artigo | Pérez-Granados et al., Ecology 107(2): e70317, 2026, DOI 10.1002/ecy.70317 (PMC12881925) | ART |
| DOI de dados citado no artigo | 10.5281/zenodo.17293588 (declaração de disponibilidade), diferente do DOI da v4 e do conceito. Relação com a v4 não verificada | ART |
| Arquivos | 1 zip por sítio, `Metadata.csv`, `Pooled annotations.csv`, `Species list.pdf`, `README.txt`, com md5 no ZJ. Observação: no registro o arquivo se chama "Pooled annotations.csv" (espaço); o baixado é `Pooled_annotations.csv` | ZJ |
| md5 do Metadata.csv / das anotações | e2b7d4f52a955ee5d6e2c6b7e8444ee6 / b9e5d87885ee87b10fd93bee70fab534 | ZJ |

Para citar: use o DOI da versão (...20513304) mais a data de acesso 2026-10-03.

## Licença (divergência entre as fontes)

| Fonte | O que diz |
|---|---|
| Campo de licença do Zenodo (ZJ, ZD) | `cc-by-4.0` (CC BY 4.0); campo de direitos vazio (None) |
| Texto da descrição do registro (ZD, e `description` em ZJ) | "published under a Creative Commons Attribution Non Commercial 4.0 International copyright" (CC BY-NC) |
| Resumo do artigo (ART) | "published under a Creative Commons Attribution 4.0 International license" (CC BY) |
| Licença do artigo em si (ART) | CC BY-NC-ND 4.0 (do texto, não dos dados) |

Há divergência real: o campo formal e o resumo do artigo dizem CC BY 4.0; a descrição do registro diz CC BY-NC 4.0. O artigo ainda traz CC BY-NC-ND para o próprio texto, o que pode ser a origem da confusão, mas isso é hipótese, não verificado. Postura conservadora até esclarecimento: tratar como CC BY-NC (uso não comercial, atribuição). Não há problema para pesquisa voluntária e sem fins lucrativos, mas isso limita a redistribuição derivada e deve ser confirmado com os autores antes de publicar derivados. As licenças dos dados de cada sítio contribuinte não aparecem no MD: não verificado.

## Cobertura global (MD, ART)

- MD tem 72 linhas (sítios), 29 valores distintos em "Recording location" e soma de "Minutes Annotated" = 5.047. Confere com o artigo (72 sítios, 29 locais, 5.047 min; ART, ZD).
- Biomas: o artigo diz 13; o MD tem 14 grafias distintas em "Biome", com variantes de grafia (Wetland/Wetlands; Boreal forest/Taiga e Boreal Forests/Taiga; Coniferous/coniferous). Não reconciliado.
- 91.931 vocalizações e 1.192 espécies (ART, ZD). Não conferi essas somas contra o PA.

## Sítios no Brasil (MD, colunas "Recording location" = Brazil, "Study area", "Biome", "Latitude", "Longitude", "Recording date", "Minutes Annotated")

São 9 sítios dos 72. Nenhum em cabruca e nenhum na Bahia (MD: nenhum "Study area" cita a Bahia). Nenhum na Mata Atlântica do sul da Bahia.

| Sítio | Área de estudo | Bioma (MD) | Lat, Lon | Ano | Min. | Registros PA | Espécies PA |
|---|---|---|---|---|---|---|---|
| BMT | Pantanal Baia das Pedras (MT) | Wetland | -16,5139, -56,3936 | 2014 e 2021 | 60 | 2.730 | 94 |
| DUNAS | Parque Estadual Dunas de Natal (RN) | Floresta úmida tropical | -5,8118, -35,1917 | 2023 | 60 | 1.718 | 25 |
| EMP | Mata do Jiqui, EMPARN (RN) | Floresta úmida tropical | -5,8117, -35,1918 | 2022 | 14 | 198 | 18 |
| FNCA | Floresta Nacional de Carajás (PA) | Floresta úmida tropical | -6,1792, -50,1568 | 2022 | 190 | 2.573 | 111 |
| PETI | Estação Ambiental de Peti (MG) | Floresta úmida tropical | -19,8992, -43,3686 | 2012 | 60 | 1.006 | 30 |
| RBA | Mata Rio Baldum (RN) | Floresta úmida tropical | -6,2020, -35,2276 | 2022 | 15 | 363 | 28 |
| RFP | RPPN Fazenda Pacatuba (PB) | Floresta úmida tropical | -7,0407, -35,1541 | 2022 | 31 | 684 | 41 |
| RGU | RPPN REBIO Guaribas (PB) | Floresta úmida tropical | -6,7178, -35,1818 | 2022 | 13 | 125 | 14 |
| RME | RPPN Mata Estrela (RN) | Floresta úmida tropical | -6,3961, -35,0094 | 2022 | 13 | 175 | 21 |

Total: 9 sítios, 456 min anotados, 9.572 anotações, 251 espécies distintas (contagem de PA filtrada por "Site"). Os estados (MT, RN, PB, PA, MG) são minha dedução pelos nomes e coordenadas; o MD não tem coluna de estado. O bioma do MD é a classificação ampla de Olson et al. (RD), não o bioma brasileiro: "Tropical and Subtropical Moist Broadleaf Forest" cobre Mata Atlântica e Amazônia sem distingui-las.

Independência espacial:
- DUNAS e EMP têm coordenadas praticamente idênticas (diferença de ~10-15 m) com nomes de área diferentes: parecem a mesma área amostrada duas vezes, não duas áreas independentes. Isso é inferência a partir das coordenadas; não verificado com os contribuintes.
- RBA, RGU, RME, RFP e DUNAS/EMP ficam todos no Nordeste oriental (RN/PB), em raio de poucas centenas de km, com mesmo ano de gravação (2022) e mesma equipe (UFRN, afiliações 45, 69, 70 em ART): risco de autocorrelação espacial e de efeito de equipamento (AudioMoth vs. SM2).
- Mata Atlântica provável: PETI (MG) e os 5 a 6 do RN/PB. Amazônia: FNCA. Pantanal: BMT. Nenhum é cacau, agrofloresta ou sistema sombreado (nenhuma menção no MD).
- Número efetivo de áreas independentes de Mata Atlântica: cerca de 5 a 6, longe do alvo de 24 a 36 do PRD 5.3, e todas no Nordeste e Sudeste, não no sul da Bahia.

## Coordenadas, datas e fuso

- Coordenadas: uma por sítio, "centro do sítio de gravação", em graus decimais (RD, colunas Latitude/Longitude). Não há coordenada por gravador nem por gravação no MD ou no PA. Precisão: 4 casas decimais (~10 m) na maioria, 6 em FNCA; a precisão real do GPS e a dispersão dos pontos dentro do sítio: não verificado. Para o PRD 5.2, serve a escala de pixel de 10 m de forma grosseira, mas "centro do sítio" pode agregar vários gravadores.
- Data: o MD traz só o ano ("Year when the recordings were done", RD), em alguns casos dois anos (BMT: "2014 & 2021").
- Data e hora por gravação: aparecem apenas no nome do arquivo, por exemplo `FNCA_20221004_030000.wav`, `BMT_20140704_055801.wav` (PA, coluna "Recording"). O padrão sítio_AAAAMMDD_hhmmss é uma leitura minha dos nomes. Fuso (local ou UTC) não declarado em nenhuma fonte: não verificado. Isso falha o critério "datas com horário e fuso" do PRD 5.2 até que os autores respondam; os nomes dão a data de calendário e a hora provável, e o fuso do Brasil pode ser inferido mas não é garantido.
- Em PA, gravações de 2012 a 2023 nos sítios brasileiros (datas lidas dos nomes): PETI 2012-10 a 2013-02; BMT 2014-07 a 2014-09 e 2021-07; FNCA 2022-10; RN/PB 2022-09 a 2023-11; DUNAS 2022-10 a 2023-11 (24 datas distintas).

Compatibilidade com Sentinel-2 (BDC S2-16D, a partir de 2017): PETI (2012) e BMT 2014 ficam antes (só Landsat; PRD 5.1 diz para não misturar sensores sem harmonização). BMT 2021, FNCA 2022 e os sítios do RN/PB 2022-2023 ficam dentro da janela. A observação válida da composição por data não foi verificada (precisa de consulta STAC; é a tarefa da semana 3).

## Seleção dos trechos e nível dos rótulos

- Rótulos: por espécie, com início, fim, frequência baixa e alta de cada vocalização (colunas de PA: Species, Site, Recording, Begin_Time_(s), End_Time_(s), Low_Freq_(Hz), High_Freq_(Hz); ART, ZD diz "annotated to species-level by local experts"). Isso é o ideal para o BirdNET e para a comunidade.
- Critério de seleção dos trechos: o texto do artigo baixado está incompleto (só cabeçalho, resumo e declarações de disponibilidade; não tem Métodos). Não encontrei em nenhuma fonte baixada como os trechos de 1 min foram escolhidos (aleatório, estratificado por hora, escolhido por haver vocalização, etc.). Não verificado. Único indício em PA: a duração dos trechos varia (fim máximo de anotação em PA: 59,98 s em FNCA e DUNAS, 68 s em BMT, 119 s em PETI), então "minuto" não é uma unidade fixa.
- Consequência: sem o critério de seleção, não dá para interpretar ausências nem estimar riqueza por sítio; 13 a 190 min por sítio é esforço mínimo e provavelmente enviesado em direção a trechos com canto. As "ausências" no PA não são ausências verdadeiras (regra do PRD 6.3).
- Também não verificado: se as anotações cobrem todas as espécies audíveis ou apenas as identificáveis pelo anotador, e a taxa de falsos negativos dos anotadores.

## Avaliação contra os critérios do PRD 5.2

| Critério | Resultado | Evidência |
|---|---|---|
| Coordenadas compatíveis com a escala | Parcial: uma coordenada por sítio, ~10 m, "centro" | MD, RD |
| Data com horário e fuso | Falha parcial: ano no MD; data e hora só no nome do arquivo; fuso não declarado | MD, RD, PA |
| Identidade de pontos, períodos, esforço e equipamento recuperáveis | Parcial: gravador, taxa de amostragem, ano, minutos por sítio estão no MD; ponto individual dentro do sítio e protocolo de gravação não | MD |
| Áreas independentes suficientes e com variação ambiental útil | Falha para o alvo: 9 sítios no Brasil, ~8 independentes, nenhum em cabruca ou no sul da Bahia; ~5 a 6 em Mata Atlântica do NE | MD |
| Rótulos e seleção que permitam interpretar detecções, ausências e vieses | Parcial: rótulos por espécie (bom); seleção dos trechos não verificada | PA, ART |

## Veredito

WABAD v4 não serve como base ecológica final do projeto. Os motivos: poucas áreas brasileiras (9 sítios, 2 deles praticamente coincidentes), nenhuma em cabruca nem no sul da Bahia, esforço de 13 a 190 min por sítio, ano sem fuso, e critério de seleção dos trechos desconhecido. Um número grande de anotações (9.572 só no Brasil) não compensa o número pequeno de sítios independentes.

Papel sugerido: teste de pipeline e de reconhecedor (caminho C do PRD 7). Os rótulos por espécie, com tempo e frequência, permitem estimar precisão e sensibilidade do BirdNET contra anotação de especialista (RF3, RF4, objetivo específico 3), em particular nos sítios de Mata Atlântica (PETI, RN/PB) e FNCA. Para o teste de integração óptico-acústica da semana 3, os sítios de 2022-2023 (FNCA, RN/PB) têm datas dentro do período do Sentinel-2. Não usar para estimar o ganho de séries temporais sobre a baseline (M0 a M3) com validação por grupo: não há sítios suficientes. Resultados desse uso seriam exploratórios.

## Perguntas abertas (alimentam G1)

1. Qual é a licença efetiva dos dados: CC BY 4.0 (campo e resumo do artigo) ou CC BY-NC 4.0 (descrição do registro)? Perguntar aos autores e, se possível, pedir correção do registro.
2. Como foram selecionados os trechos anotados (aleatório, por hora, por presença de vocalização)? Falta o texto de Métodos do artigo (ART está incompleto); buscar o artigo completo ou o Metadata S1.
3. Qual é o fuso das horas nos nomes dos arquivos (local ou UTC)? Confirmar por sítio brasileiro.
4. DUNAS e EMP são o mesmo ponto físico? Há mais de um gravador por sítio? Qual a precisão das coordenadas (centro do sítio)?
5. Qual a relação entre o DOI 10.5281/zenodo.17293588 (citado no artigo), o conceito ...14191523 e a v4 ...20513304? O que mudou entre as versões (a descrição do registro não traz notas de versão)? O rótulo "v4" não está no registro.
6. Os contribuintes brasileiros (UFRN/ConservaSom, PUC Minas, UFMT, UEL) têm gravações adicionais não anotadas, ou mais sítios no sul da Bahia, que poderiam virar parceria? Isso pertence ao caminho A.
7. Os 14 valores de bioma no MD vs. 13 no artigo: qual lista é a correta (impacto baixo)?
8. Quantas observações válidas de Sentinel-2 existem por sítio e data? Resolver na semana 3 pela consulta STAC.
9. Somas de vocalizações e espécies (91.931 e 1.192) não conferidas no PA; conferir se o WABAD for usado além do teste de pipeline.

As fontes foram baixadas do registro Zenodo e do Europe PMC em 2026-10-03 e não são versionadas neste repositório.
