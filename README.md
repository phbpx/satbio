# satbio

**Sensoriamento remoto e bioacústica em cabruca** — projeto de pesquisa independente e voluntário, em ciência aberta, usando dados públicos do INPE.

## Sobre

Sistemas cabruca cultivam cacau sob árvores de sombra no sul da Bahia. Áreas com cobertura arbórea parecida podem abrigar comunidades de aves bem diferentes. Este projeto investiga se o histórico espectral da vegetação e o contexto da paisagem ajudam a explicar essas diferenças.

> Quanto as séries temporais de vegetação acrescentam à predição de indicadores da comunidade de aves em cabruca, depois de considerar sazonalidade, esforço de gravação e contexto paisagístico?

A abordagem combina:

- **Sensoriamento remoto:** séries temporais Sentinel-2 (S2-16D-2) e Landsat (LANDSAT-16D-1) do Brazil Data Cube/INPE, além do PRODES Mata Atlântica para o contexto de supressão no entorno.
- **Monitoramento acústico passivo:** gravações convertidas em detecções por espécie com um reconhecedor existente (BirdNET ou equivalente) e validadas por especialista.
- **Modelagem:** modelos incrementais (referência → um período → paisagem → séries temporais), avaliados fora da amostra com validação por propriedade ou blocos espaciais.

O resultado esperado é quantificar o ganho das séries temporais e os limites de generalização do método. Um ganho pequeno ou nulo também é um resultado válido.

## Status

Piloto técnico em andamento, com dados abertos. Até agora:

- **Semana 1:** auditoria das bases acústicas abertas. Nenhuma tem gravações em cabruca ou no sul da Bahia, então a pergunta principal depende de parceria ([`docs/bases/`](docs/bases/README.md)).
- **Semana 2:** 72 gravações de 4 sítios do WABAD (Mata Atlântica do Nordeste) vinculadas a pontos, datas e anotações ([`docs/piloto/semana-2.md`](docs/piloto/semana-2.md)).
- **Semana 3:** série Sentinel-2 do Brazil Data Cube nesses pontos, terminando na véspera das gravações ([`docs/piloto/semana-3.md`](docs/piloto/semana-3.md)).

O piloto testa o fluxo técnico; ele não mede desempenho de reconhecedor nem capacidade preditiva, e os sítios não são cabrucas. O desenho analítico (resposta ecológica, referência, validação) está sendo revisado antes de qualquer coleta definitiva.

## Documentação

| Documento | Conteúdo |
|---|---|
| [`docs/pre-projeto-bioacustica-inpe.pdf`](docs/pre-projeto-bioacustica-inpe.pdf) | Pré-projeto completo (também em `.docx`) |
| [`docs/PRD.md`](docs/PRD.md) | Requisitos, roadmap de 24 meses, portões de decisão e riscos |
| [`CLAUDE.md`](CLAUDE.md) | Orientações para o Claude Code neste repositório |

## Tecnologia

Python para consulta STAC, rasters, áudio e modelos; R para estatística ecológica quando necessário.

## Dados e licenças

Áudios, rasters e coordenadas de propriedades não são versionados neste repositório. Código e metadados serão publicados quando permitido, respeitando as licenças das bases e os acordos de parceria.
