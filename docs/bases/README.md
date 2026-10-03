# Inventário de bases — semana 1 do piloto

**Data:** 2026-10-03 · **Status:** auditoria concluída com fontes primárias (metadados e artigos; nenhum áudio baixado)

As auditorias detalhadas estão nos arquivos desta pasta. Este inventário reúne os vereditos e o que eles significam para o portão G1. Os critérios de aceite são os da seção 5.2 do `docs/PRD.md`.

## Resumo

| Base | Grupo | Sítios no Brasil | Sul da Bahia / cabruca | Coordenadas | Data e fuso | Período | Licença | Papel |
|---|---|---|---|---|---|---|---|---|
| [WABAD v4](wabad.md) | Aves, rótulos por espécie | 9 de 72 (MT, PA, MG, RN/PB); ~8 áreas independentes | Não | 1 por sítio (centro), 4–6 casas decimais | Data só no nome do áudio; fuso não declarado | 2012–2023; 8 dos 9 sítios com gravações em 2017+ | Divergente: CC BY 4.0 (campo do Zenodo) × CC BY-NC 4.0 (descrição) | Teste de pipeline e do reconhecedor |
| [Soundscape_CCM1](soundscape-ccm1.md) | Aves, anuros e insetos; presença por grupo | 22–23 paisagens em SP/MG | Não | **Nenhuma** nos arquivos | Data e hora no nome do arquivo; fuso não declarado | out/2016–jan/2017 | GPL-3.0 (repositório); áudios no Google Drive sem licença declarada | Teste da mecânica do pipeline |
| [AnuraSet](anuraset.md) | Anuros | 4 sítios (2 Cerrado, 2 Mata Atlântica) | Não | **Nenhuma** nas fontes (só mapa) | Nome do arquivo; BRT pelo artigo | set/2019–jan/2021 | Divergente: CC BY (Zenodo) × CC0 (artigo) | Teste de leitura de áudio e rótulos |

Nenhuma das três atende aos critérios de base ecológica final: nenhuma tem sítios no sul da Bahia ou em cabruca, e nenhuma tem áreas independentes em número próximo às 24–36 do desenho.

## O que isso significa para o G1

- **Caminho A (cabruca) depende de parceria ou campanha própria.** Não foi encontrada base aberta com gravações de aves em cabruca. A busca por grupos que gravam na região ainda está incompleta (ver `docs/literatura/bases-acusticas-mata-atlantica.md`).
- **Caminho B (dados abertos) está sem candidato.** O registro Zenodo 10556620 (Rosa *et al.*, 2024) foi [auditado](rosa-2024-zenodo-10556620.md): tem listas de aves por especialistas, mas só um parque no interior (PN do Iguaçu), um conjunto costeiro sem estado declarado, nenhuma coordenada por ponto e nenhum áudio. Serve como teste de pipeline e referência de desenho amostral.
- **O caminho A tem um parceiro provável:** o grupo de ecologia de aves da UESC (Morante-Filho, Faria e colaboradores) já amostrou aves com pontos de escuta em 10 a 30 agroflorestas de cacau no sul da Bahia. Detalhes e referências em `docs/literatura/bases-acusticas-mata-atlantica.md`.
- **Caminho C (metodológico) já é viável** com as bases auditadas.

## Consequência para as semanas 2 e 3

O teste de integração STAC da semana 3 precisa de coordenadas e datas posteriores a 2017. Entre as três bases, só o **WABAD** tem coordenadas, e 8 dos seus 9 sítios brasileiros têm gravações de 2017 em diante (FNCA 2022, os seis sítios do RN/PB em 2022–23 e BMT, que tem gravações de 2014 e de 2021). Só PETI (2012) fica de fora. Recomendação:

- **Semana 2:** usar uma pequena seleção de áudios dos sítios brasileiros do WABAD (os zips por sítio têm de 25 MB a 740 MB) para o vínculo entre áudio, data e ponto.
- **Semana 3:** extrair a série do S2-16D-2 nesses mesmos pontos.
- O Soundscape_CCM1 e o AnuraSet só entram no teste STAC se os autores fornecerem as coordenadas.

Duas ressalvas para essa escolha:
- O WABAD não declara o fuso dos horários. As janelas de imagens devem terminar na data da gravação, e uma diferença de fuso só muda o resultado em gravações próximas da meia-noite.
- DUNAS e EMP ficam a cerca de 10 m uma da outra e devem ser tratadas como a mesma área.

## Perguntas abertas para o G1

1. **Licenças:** qual vale para o WABAD (BY ou BY-NC) e para o AnuraSet (BY ou CC0)? Até a resposta dos autores, trate o WABAD como não comercial.
2. **Fuso:** WABAD e Soundscape_CCM1 não declaram fuso. As gravações do CCM1 (out/2016–jan/2017) caem no horário de verão de SP/MG, então podem estar em UTC−2. Isso é inferência, não verificada.
3. **Coordenadas do CCM1 e do AnuraSet:** pedir aos autores, se essas bases forem usadas no teste STAC.
4. **Zenodo 10556620:** coordenadas por gravador e estado do conjunto costeiro (#5) só com os autores; ver as perguntas abertas na auditoria.
5. **Parcerias no sul da Bahia:** os contatos dos sítios brasileiros do WABAD (coluna `Contact` do `Metadata.csv`) e o grupo da UESC têm gravações ou interesse em uma campanha acústica em cabruca? Pontos de escuta e gravação têm vieses diferentes, então dados de pontos de escuta só servem como referência com tratamento explícito.
6. **Seleção dos trechos anotados no WABAD:** os Métodos do artigo não foram obtidos (o texto do Europe PMC veio sem eles).

## Correções a fazer no PRD

- AnuraSet: nenhuma fonte rotula a versão como "v3". O registro 10.5281/zenodo.8342596 é a versão de índice 2 do concept 10.5281/zenodo.8043209, publicada em 2023-06-16.
- WABAD: concept DOI 10.5281/zenodo.14191523. A licença deve ser registrada como divergente, não só como CC BY-NC 4.0.
- Seção 5.2: incluir o Zenodo 10556620 (feito, já auditado).

## Fontes

Os metadados baixados para as auditorias ficaram fora do repositório, no scratchpad da sessão, porque têm licenças próprias. Cada auditoria cita o arquivo de origem de cada afirmação e a data de acesso.
