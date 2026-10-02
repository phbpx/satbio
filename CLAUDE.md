# satbio

Projeto de mestrado em Sensoriamento Remoto (INPE). Avalia quanto séries temporais Sentinel-2/Landsat do Brazil Data Cube acrescentam à predição de indicadores da comunidade de aves, medidos por monitoramento acústico passivo, em sistemas cabruca no sul da Bahia.

- Pré-projeto: `docs/pre-projeto-bioacustica-inpe.pdf` (o `.docx` tem o mesmo conteúdo).
- Roadmap, requisitos e portões de decisão: `docs/PRD.md`. Ao concluir uma entrega ou tomar uma decisão de portão, atualize o PRD.

O projeto está no início: ainda não há código nem dados. Pergunte antes de criar uma estrutura de diretórios grande ou escolher bibliotecas; prefira algo pequeno que responda à próxima entrega do roadmap.

## Stack

Python para consulta STAC, rasters, processamento de áudio e modelos; R apenas quando a estatística ecológica pedir. Sem plataforma web ou infraestrutura distribuída — o objetivo é um fluxo reproduzível para a dissertação, não um produto.

## Regras metodológicas que o código precisa respeitar

Estas regras vêm do pré-projeto e protegem a validade dos resultados, por isso valem para qualquer script de análise:

- **Sem vazamento temporal:** janelas de imagens terminam na data da campanha acústica.
- **Sem vazamento espacial:** áreas e campanhas da mesma propriedade ficam no mesmo grupo de validação; normalização, seleção de variáveis e comunidade de referência são calculadas só no treino; o teste nunca escolhe modelo ou escala.
- **Unidade independente é a propriedade/fragmento.** Minutos, segmentos e pontos dentro de uma área são subamostras.
- **Reconhecedor:** a pontuação do BirdNET (ou equivalente) não é probabilidade calibrada, e não detecção não é ausência.
- **Rastreabilidade:** registre versão da coleção, data de acesso, IDs de itens STAC, máscaras e parâmetros de qualidade usados em cada extração.
- **Sensores:** não misture Sentinel-2 e Landsat sem harmonização; reamostragem não cria detalhe.

## Dados

Áudio é volumoso (~80 GB estimados para a campanha) e pode ter restrições de licença ou de parceria: não versione áudios, rasters ou coordenadas de propriedades no git. Mantenha a licença de cada base registrada junto ao dado.

## Escrita

Documentos e comentários em português. Ao descrever resultados, distinga o que foi executado do que é proposta e deixe claros os limites de amostragem e extrapolação.
