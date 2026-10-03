# Dicionário de dados

Gerado por `scripts/semana4_integracao.py` a partir dos cabeçalhos das tabelas em `data/processed/` (fora do git). Não edite à mão: mude `src/satbio/dicionario.py`.


## `pontos`

`data/processed/wabad/pontos.csv` — Um sítio do WABAD por linha, com a coordenada declarada pela fonte.

| Coluna | Descrição |
|---|---|
| `sitio` | código do sítio no WABAD |
| `grupo_validacao` | grupo da validação cruzada (provisório: o próprio sítio) |
| `area_estudo` | nome da área declarado no Metadata.csv |
| `pais` | país declarado no Metadata.csv |
| `bioma_olson` | bioma na classificação ampla de Olson, como declarado |
| `latitude` | latitude WGS84 do centro do sítio |
| `longitude` | longitude WGS84 do centro do sítio |
| `precisao_coord` | o que a coordenada representa |
| `gravador` | gravador e microfone declarados |
| `taxa_declarada_hz` | taxa de amostragem declarada (Hz) |
| `ano_declarado_metadata` | ano de gravação declarado pela fonte; não usar como data |
| `minutos_anotados` | minutos anotados declarados pela fonte |

## `campanhas`

`data/processed/wabad/campanhas.csv` — Uma campanha por sítio, delimitada pelas próprias gravações.

| Coluna | Descrição |
|---|---|
| `sitio` | código do sítio no WABAD |
| `campanha_id` | identificador da campanha (sítio-número) |
| `inicio_relogio` | primeira gravação (relógio do gravador, sem fuso) |
| `fim_relogio` | última gravação (relógio do gravador, sem fuso) |
| `n_gravacoes` | número de arquivos de áudio válidos |
| `esforco_min` | minutos de áudio válidos |

## `gravacoes`

`data/processed/wabad/gravacoes.csv` — Um arquivo de áudio (minuto) por linha; subamostra do sítio × campanha.

| Coluna | Descrição |
|---|---|
| `arquivo` | nome do arquivo de áudio (SITIO_AAAAMMDD_HHMMSS.wav) |
| `sitio` | código do sítio no WABAD |
| `sitio_origem` | sítio da pasta de onde o arquivo foi extraído |
| `inicio_relogio` | primeira gravação (relógio do gravador, sem fuso) |
| `duracao_s` | duração do áudio (s) |
| `taxa_hz` | taxa de amostragem lida do cabeçalho (Hz) |
| `canais` | número de canais |
| `sha256` | hash do arquivo de áudio |
| `erro` | erro de leitura do nome ou do cabeçalho; vazio se ok |
| `fuso` | fuso do relógio do gravador ('desconhecido' quando a fonte não declara) |
| `ponto_id` | identificador do gravador ('desconhecido (centro do sítio)' no WABAD) |

## `deteccoes`

`data/processed/wabad/deteccoes.csv` — Uma vocalização anotada por linha; a mesma espécie pode repetir no minuto.

| Coluna | Descrição |
|---|---|
| `sitio` | código do sítio no WABAD |
| `arquivo` | nome do arquivo de áudio (SITIO_AAAAMMDD_HHMMSS.wav) |
| `especie` | nome científico anotado |
| `inicio_s` | início da vocalização no arquivo (s) |
| `fim_s` | fim da vocalização no arquivo (s) |
| `freq_min_hz` | frequência mínima da caixa anotada (Hz) |
| `freq_max_hz` | frequência máxima da caixa anotada (Hz) |
| `fonte` | origem da anotação (especialista do WABAD ou reconhecedor) |

## `controle_qualidade`

`data/processed/wabad/controle_qualidade.csv` — Um problema de qualidade por linha.

| Coluna | Descrição |
|---|---|
| `tipo` | tipo de problema |
| `arquivo` | nome do arquivo de áudio (SITIO_AAAAMMDD_HHMMSS.wav) |
| `detalhe` | descrição do problema |

## `serie_s2`

`data/processed/stac/serie_s2.csv` — Uma composição de 16 dias do S2-16D-2 por sítio × campanha.

| Coluna | Descrição |
|---|---|
| `sitio` | código do sítio no WABAD |
| `campanha_id` | identificador da campanha (sítio-número) |
| `corte` | fim da janela de imagens: véspera da 1ª gravação |
| `item_id` | ID do item STAC do S2-16D-2 |
| `item_atualizado` | data de atualização do item no catálogo |
| `tile` | tile do cubo (grade BDC_SM_V2) |
| `inicio_composicao` | início do período de 16 dias |
| `fim_composicao` | fim do período de 16 dias |
| `nuvem_item_pct` | cobertura de nuvem do item inteiro (%) |
| `x_cubo` | coordenada x do ponto no CRS do cubo (m) |
| `y_cubo` | coordenada y do ponto no CRS do cubo (m) |
| `pixel_linha` | linha do pixel lido no tile |
| `pixel_coluna` | coluna do pixel lido no tile |
| `B02` | azul; reflectância de superfície (escala física 0–1) no pixel do ponto |
| `B04` | vermelho; reflectância de superfície (escala física 0–1) no pixel do ponto |
| `B08` | infravermelho próximo (10 m); reflectância de superfície (escala física 0–1) no pixel do ponto |
| `B8A` | infravermelho próximo estreito (20 m nativo); reflectância de superfície (escala física 0–1) no pixel do ponto |
| `B11` | infravermelho de ondas curtas (20 m nativo); reflectância de superfície (escala física 0–1) no pixel do ponto |
| `NDVI` | NDVI do cubo, (B8A − B04)/(B8A + B04) |
| `EVI` | EVI do cubo |
| `SCL` | classe da Scene Classification Layer no cubo |
| `CLEAROB` | observações limpas no período (cubo) |
| `TOTALOB` | observações totais no período (cubo) |
| `PROVENANCE` | dia do ano da observação de origem do pixel |
| `NDMI` | (B8A − B11)/(B8A + B11), índice de umidade |
| `SCL_origem` | classe SCL na cena Sentinel-2 de origem (regra de validade principal) |
| `cena_origem` | ID da cena S2_L2A-1 usada para o pixel do ponto |
| `n_cenas_origem` | cenas do dia que cobrem o ponto |
| `conflito_scl_origem` | cenas do dia discordam e nenhuma reproduz o cubo |
| `dif_b04_origem` | |B04 da cena de origem − B04 do cubo| (reflectância) |
| `cenas_origem_janela` | cenas de origem de todos os pixels da janela 3×3 (separadas por ';') |
| `data_observacao` | data da observação de origem do pixel (via PROVENANCE) |
| `valido` | pixel válido pela regra principal (PRD 6.3, decisão D) |
| `motivo_invalido` | motivos de invalidez; vazio se válido |
| `valido_scl_cubo_b02` | variante de sensibilidade: SCL do cubo + B02 |
| `valido_somente_scl_cubo` | variante de sensibilidade: só SCL do cubo |
| `viz_n_pixels` | pixels na janela em volta do ponto (9) |
| `viz_n_validos` | pixels válidos na janela |
| `viz_NDVI_mediana` | mediana do NDVI nos pixels válidos da janela |
| `viz_NDVI_dp` | desvio-padrão do NDVI nos pixels válidos da janela |
| `viz_EVI_mediana` | mediana do EVI nos pixels válidos da janela |
| `viz_EVI_dp` | desvio-padrão do EVI nos pixels válidos da janela |
| `viz_NDMI_mediana` | mediana do NDMI nos pixels válidos da janela |
| `viz_NDMI_dp` | desvio-padrão do NDMI nos pixels válidos da janela |

## `tabela_piloto`

`data/processed/integracao/tabela_piloto.csv` — Uma linha por sítio × campanha: acústica e descritores ópticos.

| Coluna | Descrição |
|---|---|
| `sitio` | código do sítio no WABAD |
| `grupo_validacao` | grupo da validação cruzada (provisório: o próprio sítio) |
| `latitude` | latitude WGS84 do centro do sítio |
| `longitude` | longitude WGS84 do centro do sítio |
| `gravador` | gravador e microfone declarados |
| `campanha_id` | identificador da campanha (sítio-número) |
| `minutos_validos` | minutos de áudio válidos na campanha |
| `especies_detectadas` | espécies detectadas em todos os minutos (não é riqueza real) |
| `esforco_padrao_min` | esforço comum usado na rarefação (minutos) |
| `riqueza_rarefeita` | riqueza detectada média em subconjuntos aleatórios de `esforco_padrao_min` minutos (data e horário não padronizados) |
| `especies` | espécies detectadas em todos os minutos (';'); sem esforço padronizado, não usar direto no Jaccard |
| `corte` | fim da janela de imagens: véspera da 1ª gravação |
| `composicoes` | composições na janela de 12 meses |
| `composicoes_usadas` | composições com maioria da janela 3×3 válida |
| `trimestres_cobertos` | trimestres da janela com ao menos uma composição usada (pela data de observação) |
| `n_ultimo_trimestre` | composições usadas no último trimestre antes do corte |
| `cobertura_ok` | série atende à cobertura mínima (desenho analítico, seção 6) |
| `ndvi_mediana` | mediana anual do NDVI (estado médio do dossel) |
| `ndmi_mediana` | mediana anual do NDMI (umidade e estrutura do dossel) |
| `ndvi_amplitude_p90_p10` | P90 − P10 do NDVI (variação sazonal) |
| `ndmi_mudanca_recente` | mediana do NDMI no último trimestre − mediana anual; vazio com menos de 2 composições no trimestre; mistura fase sazonal e perturbação |
