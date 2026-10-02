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

Pré-projeto. Nenhum experimento foi realizado ainda. O primeiro passo é um piloto de 30 dias com bases acústicas abertas (WABAD, Soundscape_CCM1) para testar o processamento e a integração com o catálogo STAC do INPE.

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
