# Viabilidade: sucesso de restauração com os dados do REASSEMBLY (Chocó, Equador)

**Data:** 2026-10-03 · **Conclusão:** não recomendado como pivô do satbio; a restauração fica como ideia para um estudo futuro em região menos nublada

## O que seria o estudo

Usar os dados abertos do projeto REASSEMBLY (Zenodo 14616054; Müller *et al.* 2023; Kortmann *et al.* 2025) para perguntar se séries temporais de satélite acrescentam à predição da recuperação da comunidade de aves ao longo de um gradiente de regeneração (pasto, cacau ativo, pasto e cacau em regeneração de 1 a 38 anos, mata primária), usando a mata primária como referência.

## O que os dados oferecem

Detalhes em [`alternativas-a-cabruca.md`](alternativas-a-cabruca.md), verificados no registro:

- 66 parcelas com coordenadas, tratamento e ano de regeneração (34 parcelas), em Canandé; gravações em out–nov/2021 (43 parcelas) e nov/2022 (23).
- 16.532 detecções de aves por especialistas, com data e hora; fração de floresta em 1 km por parcela.
- Licença divergente (CC BY-SA 4.0 no registro, CC BY no artigo); só tabelas, sem áudio.

## Teste de nebulosidade

O Brazil Data Cube não cobre o Equador. Foi usado o catálogo aberto Earth Search (Sentinel-2 L2A, AWS), com 9 pontos numa grade 3×3 cobrindo a área das parcelas, no ano anterior às gravações de 2021 (out/2020 a set/2021), contando as observações com SCL 4, 5 ou 6, uma por ponto e data. Script: `scripts/nebulosidade_reassembly.py`; tabela por cena × ponto e manifesto (IDs dos itens, data de acesso, commit) em `data/processed/reassembly_nuvem/`.

| | Canandé (cenas individuais) | Sul da Bahia (cubo de 16 dias, 2022) |
|---|---|---|
| Nuvem mediana da cena | 90% (294 cenas, tiles 17NPA e 17NQA) | — |
| Observações limpas no ponto | 10% (mediana de 7 por ano; 3 a 11) | — |
| Períodos de 16 dias com alguma observação válida | 5 de 22 (mediana; 3 a 9) | ~12 de 23 (mediana) |

Houve meses sem nenhuma observação limpa nos 9 pontos (dezembro de 2020, maio e agosto de 2021).

**Reprodução (2026-10-04).** O teste original (2026-10-03) foi feito com um script avulso; a versão versionada, rodada em 2026-10-04 (commit `6dc4580`), deu números um pouco diferentes: 10% de observações limpas (antes 8%), mediana de 7 por ponto (antes 6), mínimo de 3 períodos de 16 dias com observação válida (antes 2) e dezembro de 2020 também sem observação limpa. A diferença provável é a grade de pontos e a regra de uma observação por ponto e data, que o script avulso não registrou. A conclusão não muda.

## Avaliação

| Critério | Situação |
|---|---|
| Descritores sazonais (amplitude, mudança recente) | **Inviáveis**: com 2 a 9 períodos válidos por ano, a regra de cobertura do desenho falha em praticamente todas as parcelas |
| Estado médio da vegetação | Possível com mediana de vários anos, mas sem a dimensão temporal que a pergunta testa |
| Trajetória de longo prazo (anos desde o desmatamento) | Possível com compostos anuais do Landsat desde 1985; mas a idade de regeneração já é conhecida pelos metadados, e o satélite estaria redescobrindo a variável explicativa |
| Unidades independentes | 66 parcelas, mas numa área de ~14 km, sem ID de propriedade e com 36 pares a menos de 500 m: o n independente é bem menor que 66 |
| Esforço acústico | 14 arquivos de 2 minutos por parcela (~28 minutos): pouco para estimar a comunidade com precisão |
| Validação do reconhecedor | Impossível: não há áudio aberto |
| Fonte de imagens | Fora do BDC: exigiria outro catálogo, com harmonização e rastreabilidade novas |

## Conclusão

O REASSEMBLY não sustenta a pergunta do satbio. O obstáculo decisivo é a nebulosidade: no Chocó, a série óptica não tem observações suficientes para descrever a dinâmica sazonal da vegetação, que é exatamente o que H2 testa. Os outros problemas (dependência espacial, pouco esforço acústico, ausência de áudio) só agravam.

Duas variações mudariam a pergunta e não foram recomendadas agora: usar radar (Sentinel-1, que atravessa nuvens e é sensível à estrutura do dossel) ou trajetórias anuais do Landsat. Ambas seriam estudos diferentes, não um pivô do satbio.

**A ideia da restauração continua boa** e é a aplicação em que séries temporais fazem mais sentido. Para retomá-la, o caminho é uma área de restauração com histórico conhecido em região menos nublada, de preferência dentro do Brazil Data Cube (por exemplo, projetos de restauração na Mata Atlântica ou no Cerrado com monitoramento acústico), o que ainda precisa ser buscado.
