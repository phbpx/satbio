# Piloto — semana 2: áudios do WABAD vinculados a datas e pontos

**Data:** 2026-10-03 · **Status:** executado

## O que foi feito

Uma pequena seleção do WABAD v4 (DOI 10.5281/zenodo.20513304) foi baixada e transformada em tabelas que ligam cada gravação ao seu ponto, à sua data e hora e às suas anotações. Os quatro sítios escolhidos ficam na Mata Atlântica do Nordeste (RN/PB) e foram gravados em 2022–2023, período coberto pelo Sentinel-2. DUNAS e EMP ficaram de fora porque são o mesmo ponto; FNCA e PETI, por terem zips grandes.

Para reproduzir:

```
uv sync
uv run python scripts/semana2_wabad.py          # RBA, RGU, RME, RFP
uv run python scripts/semana2_wabad.py FNCA     # outro sítio
```

Os dados brutos vão para `data/raw/wabad/` e as tabelas (`pontos`, `campanhas`, `gravacoes`, `deteccoes`, `controle_qualidade`) para `data/processed/wabad/`. Os dois ficam fora do git por volume e licença. Cada download é conferido contra o md5 publicado pelo Zenodo e tem a data registrada ao lado do arquivo. O `manifesto.json` registra DOI, licença, commit do código, versões das bibliotecas, parâmetros do controle de qualidade, checksums das entradas e sha256 das tabelas de saída.

O código passou pelo `revisor-metodologico` antes do commit; as correções que ele pediu (campanhas, fuso, unidade de validação, fonte das anotações, controle de qualidade e manifesto) estão incorporadas.

## Resultado

| Sítio | Área | Gravador | Gravações | Período (relógio do gravador) | Anotações | Espécies |
|---|---|---|---|---|---|---|
| RBA | Mata Rio Baldum | AudioMoth | 15 | out/2022–jan/2023 | 363 | 28 |
| RFP | RPPN Fazenda Pacatuba | Song Meter SM2 | 31 | dez/2022–jan/2023 | 684 | 41 |
| RGU | RPPN REBIO Guaribas | Song Meter SM2 | 13 | dez/2022–jan/2023 | 125 | 14 |
| RME | RPPN Mata Estrela | Song Meter SM2 | 13 | nov/2022–jan/2023 | 175 | 21 |

- 72 gravações de 60 s, todas em 48 kHz e mono; 1.347 anotações de vocalizações de 61 espécies. Cada anotação é uma vocalização, então contar linhas mede atividade vocal, não presença.
- O controle de qualidade confere áudios, anotações e o vínculo com o `Metadata.csv`. O único problema encontrado é o ano declarado (ver abaixo). Todo áudio tem anotação e vice-versa, nenhuma anotação passa do fim do arquivo, não há duplicatas nem horários repetidos no mesmo sítio, e taxa de amostragem e número de minutos batem com o metadado.
- A maioria das gravações começa entre 4 h e 8 h, mas há minutos noturnos (21 h–3 h).

## Achados que importam para as próximas semanas

- **Ano declarado incompleto.** O `Metadata.csv` informa 2022 para os quatro sítios, mas parte dos arquivos é de janeiro de 2023 (`ano_fora_do_declarado` no controle de qualidade). As datas usadas no projeto vêm dos nomes dos arquivos; a coluna do metadado se chama `ano_declarado_metadata` para não ser usada como data.
- **Campanhas longas.** Cada sítio tem uma campanha (`campanhas.csv`) de 1 a 3,5 meses (RBA: out/2022 a jan/2023). Usar o fim da campanha como data de corte das imagens traria informação posterior às primeiras gravações.
- **Fuso desconhecido.** As horas ficam em `inicio_relogio`, o relógio do gravador, com `fuso = "desconhecido"`. O AudioMoth (RBA) costuma nomear arquivos em UTC se o fuso não for configurado, e os SM2 usam o relógio definido pelo operador, então o erro pode ter sinais diferentes entre sítios. Isso muda a data em gravações perto da meia-noite.
- **Gravador confundido com área.** RBA usa AudioMoth e os outros três Song Meter SM2. Qualquer diferença entre RBA e os demais pode vir do equipamento, como o PRD alerta.
- **Esforço pequeno e desigual.** São 13 a 31 minutos anotados por sítio, escolhidos pelos autores com critério não documentado; se foram escolhidos por atividade, nem a não detecção nesses minutos é informativa. A tabela serve para testar o pipeline, não para comparar comunidades.
- **Unidade independente.** O n independente aqui é 4 sítios, no máximo, não 72 gravações. `pontos.csv` tem `grupo_validacao` provisório (o próprio sítio), e `gravacoes.csv` tem `ponto_id = "desconhecido (centro do sítio)"`, porque o WABAD só dá uma coordenada por sítio.
- **Codificação do `Metadata.csv`.** O arquivo mistura codificações e tem bytes corrompidos em nomes de área (ex.: "Caraj\x98s"). IDs e coordenadas não são afetados.

## Próximo passo (semana 3)

Consultar o catálogo STAC do INPE para os quatro pontos e extrair uma série curta do S2-16D-2, com máscara de qualidade. Cada série termina na véspera da primeira gravação do sítio (`campanhas.csv`), regra registrada na seção 6.3 do PRD.
