# satbio

Projeto de pesquisa independente e voluntário, em ciência aberta, sem vínculo com programa de pós-graduação. Avalia quanto séries temporais Sentinel-2/Landsat do Brazil Data Cube acrescentam à predição de indicadores da comunidade de aves, medidos por monitoramento acústico passivo, em sistemas cabruca no sul da Bahia.

- Pré-projeto: `docs/pre-projeto-bioacustica-inpe.pdf` (o `.docx` tem o mesmo conteúdo).
- Roadmap, requisitos e portões de decisão: `docs/PRD.md`. Ao concluir uma entrega ou tomar uma decisão de portão, atualize o PRD.
- Desenho analítico (resposta, modelos, inferência, decisões A–E): `docs/desenho-analitico.md`. Ele substitui a seção 6.4 do PRD.

O piloto técnico foi executado em 2026-10-02 e 03 com dados abertos (WABAD e S2-16D-2), fora de cabruca. O projeto aguarda o portão G1 (parceria até 2026-12-02). Pergunte antes de acrescentar dependências ou criar estruturas de diretório novas; prefira algo pequeno que responda à próxima fase do roadmap.

## Estrutura

- `src/satbio/`: biblioteca. `wabad.py` e `acustica.py` (áudio, anotações, rarefação), `stac.py` (séries do cubo S2-16D-2 e conferência do SCL na cena de origem), `integracao.py` (tabela analítica), `dicionario.py` (dicionário de dados a partir dos cabeçalhos), `simulacao.py` (dimensionamento e métodos de inferência), `rastreio.py` (estado do código para os manifestos).
- `scripts/`: uma etapa por arquivo. `reproduzir_piloto.py` roda o piloto inteiro (`semana2_wabad.py`, `semana3_stac.py`, `semana4_integracao.py`, `figuras_piloto.py`); `simulacao_dimensionamento.py`, `nebulosidade_sul_bahia.py` e `nebulosidade_reassembly.py` sustentam as notas de `docs/`.
- `tests/`: pytest, sem rede.
- `data/` (fora do git): `raw/` (downloads) e `processed/<etapa>/` (tabelas e `manifesto.json` de cada etapa).
- `docs/`: PRD, desenho analítico, relatórios do piloto (`piloto/`), auditorias de bases (`bases/`), notas de literatura (`literatura/`), dicionário de dados e figuras.

## Como reproduzir

```
uv sync
uv run python -m pytest
uv run python scripts/reproduzir_piloto.py          # ~10 min, precisa de internet (Zenodo e STAC do INPE)
uv run python scripts/simulacao_dimensionamento.py  # ~15 min em 10 núcleos, sem rede
uv run python scripts/nebulosidade_sul_bahia.py      # ~40 min, STAC do INPE (um ponto por vez)
uv run python scripts/nebulosidade_reassembly.py     # ~2 min, Earth Search
```

Cada etapa recusa rodar com código não commitado em `src/`, `scripts/`, `tests/`, `pyproject.toml` ou `uv.lock` (ou salva o diff, com `--permitir-sujo`) e grava em `data/processed/<etapa>/manifesto.json` o commit, as versões, as regras, os IDs de itens STAC e os hashes das entradas e saídas. Por isso: commite o código antes de rodar a etapa e commite os documentos que citam o resultado depois.

## Regras metodológicas que o código precisa respeitar

Estas regras vêm do pré-projeto e do desenho analítico e protegem a validade dos resultados, por isso valem para qualquer script de análise:

- **Sem vazamento temporal:** a janela de imagens de cada sítio × campanha termina na **véspera da primeira gravação** desse sítio × campanha (decisão de 2026-10-03). A véspera absorve o fuso desconhecido dos relógios dos gravadores; o fim da campanha nunca é usado como corte, e só entram composições cujo período inteiro termina até o corte.
- **Pixel óptico válido (decisão D):** SCL 4, 5 ou 6 na **cena Sentinel-2 de origem** (a data vem da PROVENANCE do cubo), todas as bandas presentes, PROVENANCE dentro do período da composição e B02 ≤ 0,10. Sem cena de origem, o pixel é inválido. A regra só com o SCL do cubo é variante de sensibilidade, nunca a principal.
- **Sem vazamento espacial:** áreas e campanhas da mesma propriedade (e propriedades vizinhas dependentes) ficam no mesmo grupo de validação; normalização, seleção de variáveis e comunidade de referência são calculadas só no treino; o teste nunca escolhe modelo ou escala.
- **Unidade independente é a propriedade/fragmento.** Minutos, segmentos e pontos dentro de uma área são subamostras; reamostragens sorteiam propriedades, não linhas.
- **Reconhecedor:** a pontuação do BirdNET (ou equivalente) não é probabilidade calibrada, e não detecção não é ausência.
- **Inferência de H2:** o ganho é estimado com intervalo (reamostragem de propriedades com reajuste, intervalo básico); a decisão E é regra de leitura, não teste.
- **Rastreabilidade:** registre versão da coleção, data de acesso, IDs de itens STAC, máscaras e parâmetros de qualidade usados em cada extração.
- **Sensores:** não misture Sentinel-2, Landsat ou Sentinel-1 numa mesma variável sem harmonização; reamostragem não cria detalhe.

## Agentes

Em `.claude/agents/` há três subagentes, todos mantidos após o piloto (avaliação em 2026-10-04):

- `auditor-de-bases`: as auditorias de `docs/bases/`, que sustentaram o G1, seguem o formato dele (veredito por critério da seção 5.2). Próximo uso: conferir dados de parceria (A ou A-retro) contra os critérios da seção 5.2 do PRD.
- `revisor-metodologico`: só leitura; use antes de commitar extração, indicador, divisão treino/teste, modelo ou simulação. Na revisão dos métodos de inferência apontou viés do bootstrap percentil, a variância ignorada do denominador e a falta de erro de Monte Carlo, todos corrigidos.
- `pesquisador-bibliografico`: notas de `docs/literatura/` com DOI conferido no OpenAlex ou Crossref (em 2026-10-04, o levantamento do Sentinel-1). Ele costuma ler resumos, não textos completos; volume, página e números citados fora do relatório dele precisam ser conferidos no Crossref antes de entrar num documento.

## Dados

Áudio é volumoso (~80 GB estimados para a campanha) e pode ter restrições de licença ou de parceria: não versione áudios, rasters ou coordenadas de propriedades no git. Mantenha a licença de cada base registrada junto ao dado.

## Escrita

Documentos e comentários em português. Ao descrever resultados, distinga o que foi executado do que é proposta e deixe claros os limites de amostragem e extrapolação.
