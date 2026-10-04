# Sentinel-1 como descritor de estrutura em dossel fechado

**Data:** 2026-10-04 · **Status:** nota de avaliação, sem código; recomenda o Sentinel-1 só como análise secundária

## Por que avaliar

No piloto, o NDVI mediano ficou entre 0,83 e 0,87 nos quatro sítios: o índice óptico está perto da saturação em dossel fechado, e a cabruca tem dossel fechado por definição. O descritor de dinâmica, além disso, depende de composições sem nuvem, e no sul da Bahia o trimestre mais nublado tem só 39% de composições válidas ([nebulosidade](nebulosidade-sul-bahia.md)). O radar de banda C do Sentinel-1 atravessa nuvens e responde à estrutura do dossel, e por isso é o candidato natural para as duas fraquezas.

## Disponibilidade no sul da Bahia

Conferido nos catálogos STAC em 2026-10-04, no ponto −39,1; −15,2:

| Catálogo | Coleção | Produto | No ponto | Acesso |
|---|---|---|---|---|
| BDC/INPE | `sentinel-1-rtc-1` | γ⁰ VH e VV com correção de terreno, máscara de sombra e sobreposição, ângulo de incidência local | 22 itens, só de 2025–2026 | Aberto, mesmo catálogo do S2-16D-2 |
| BDC/INPE | `sentinel-1-grd-bundle-1` | GRD (nível 1, sem correção radiométrica de terreno) | ~50–60 cenas por ano desde 2021 | Aberto; exige processamento próprio até γ⁰ |
| Microsoft Planetary Computer | `sentinel-1-rtc` | γ⁰ RTC (HH, HV, VH, VV) | 28–31 itens por ano de 2017 a 2025 (uma órbita, ~12 dias) | Busca aberta; leitura exige URL assinada (token gratuito); licença CC BY 4.0 |
| Copernicus Data Space | GRD, SLC, mosaicos | — | Não conferido | Produto CARD-BS citado no fórum oficial; cobertura não verificada |

O RTC do BDC é o caminho mais coerente com o restante do projeto, mas começa em 2025: serve a uma campanha nova a partir de 2026, não a dados retrospectivos (caminho A-retro). Para anos anteriores, o RTC do Planetary Computer é a opção pronta; processar o GRD do BDC exigiria uma cadeia própria (calibração, correção de terreno, filtragem de *speckle*), com custo e pontos de decisão novos.

## Descritores candidatos e hipóteses

| Descritor | Hipótese ecológica | O que pesa contra |
|---|---|---|
| Mediana anual de γ⁰ VH | Retroespalhamento de volume: mais biomassa e estrutura no estrato de sombra | A banda C satura bem antes da banda L em vegetação densa (Huang *et al.* 2018); parte da "saturação" vem de propriedades estruturais que se compensam (Joshi *et al.* 2017) |
| Razão VH/VV | Proporção entre espalhamento de volume e de superfície: dossel mais aberto (sombra raleada) deixa mais sinal do solo e dos cacaueiros | Sensível a umidade do solo e ao ângulo de incidência |
| Textura (GLCM) de VV e VH na janela | Heterogeneidade do dossel, clareiras | Em Camarões, o Sentinel-1 explicou ~30% da variância da abertura do dossel medida por fotos hemisféricas (Numbisi & Van Coillie 2020) e, com textura multissazonal, separou cacau de floresta de transição com 88,8% de acurácia (Numbisi *et al.* 2019) |
| Amplitude sazonal de VH (P90 − P10) | Variação sazonal de folhagem das árvores de sombra | Clima e estrutura juntos explicam ~72% da variabilidade temporal de γ⁰ em florestas úmidas (Doblas *et al.* 2020); a amplitude mistura chuva, umidade do solo e do dossel e fenologia. Tratar como descritor empírico, não como medida de estrutura |
| Anomalia de VH em relação ao mesmo período de anos anteriores | Perturbação estrutural recente (raleamento, retirada de sombra), visível através das nuvens | Exige série de vários anos na mesma órbita |

Nenhum estudo com Sentinel-1 em cabruca foi encontrado; os resultados em cacau vêm de Camarões e da Costa do Marfim e precisam de teste antes de serem transferidos. Não foi encontrado em fonte aberta um limiar de saturação da banda C em floresta tropical.

## Harmonização e rastreabilidade

- **Não misturar com o óptico.** Os descritores de radar entram como um conjunto separado, não fundidos com índices do Sentinel-2 numa mesma variável; a regra de sensores do projeto vale também aqui.
- **Uma órbita (trilho relativo) por propriedade.** Ângulo de incidência e direção de passagem mudam o γ⁰; misturar órbitas cria variação que não é do dossel. Registrar a órbita relativa, a direção (ascendente ou descendente) e o ângulo de incidência local de cada item.
- **Máscara de sombra e sobreposição** do próprio produto RTC; pixels mascarados contam como inválidos, como no óptico.
- **Speckle.** Usar a mediana de vários pixels (a janela 3×3 do óptico tem 30 m; o radar pede janela maior ou média temporal) e registrar o filtro.
- **Corte temporal igual ao óptico:** véspera da primeira gravação de cada sítio × campanha.
- **Rastreio:** catálogo, coleção e versão, IDs dos itens, data de acesso, e, no Planetary Computer, a data do token (as URLs assinadas expiram e não identificam o dado; o ID do item sim).
- **Custo:** o RTC do BDC entra pela mesma leitura STAC/COG que já existe (`src/satbio/stac.py`), com outra coleção e outras bandas. O Planetary Computer exige assinar URLs (o pacote `planetary-computer` é uma dependência nova, ou uma chamada HTTP ao serviço de token). O GRD exigiria uma cadeia SAR inteira, fora da escala do projeto.

## Alternativas fora da banda C

Banda L penetra mais no dossel: os mosaicos anuais do ALOS-2 PALSAR-2 (25 m, 2015–2025, JAXA) e os dados do NISAR, públicos desde julho de 2026 segundo o ASF (cobertura da Bahia não conferida). O GEDI mede estrutura vertical por laser, mas em pegadas esparsas; em agroflorestas da Costa do Marfim teve erro grande (Kanmegne Tamga *et al.* 2022). Ficam registrados como possibilidades, sem avaliação.

## Conclusão

Vale como **análise secundária**, não como substituto do óptico na análise principal:

- A vantagem que se pode esperar com segurança é a **ausência de lacunas por nuvem**, não uma sensibilidade maior à estrutura: a evidência em cacau é de sensibilidade fraca a moderada, e a banda C também satura.
- A pergunta do satbio é sobre séries do INPE; o RTC do BDC só cobre 2025 em diante. Para uma campanha nova (caminho A) ele serve; para o A-retro seria preciso o Planetary Computer.
- No [desenho analítico](../desenho-analitico.md) entra como M3-S1 (seção 9), fixado antes dos dados e reportado como secundário.
- Na [simulação de dimensionamento](../simulacao-dimensionamento.md) entrou como cenário no mundo pessimista: um descritor de dinâmica sem lacunas e com ruído 0,4, contra o óptico com ruído 0,7 e as lacunas observadas. O ganho de população passa de 5% para 10%; com 60 cabrucas, a permutação detecta o ganho em 86% das repetições (58% com o óptico). A largura do intervalo quase não muda (0,38 com 30 cabrucas). O ruído do radar é suposição, e a simulação supõe que o radar veja a mesma dinâmica que o óptico, o que não está demonstrado.

## Referências

Metadados conferidos no OpenAlex; foram lidos os resumos, não os textos completos.

- Doblas J, Carneiro A, Shimabukuro Y *et al.* 2020. *ISPRS Annals* V-3-2020: 89–96. https://doi.org/10.5194/isprs-annals-v-3-2020-89-2020
- Huang W, Ziniti B, Torbick N *et al.* 2018. *Remote Sensing* 10: 1424. https://doi.org/10.3390/rs10091424
- Joshi N, Mitchard ETA, Brolly M *et al.* 2017. *Scientific Reports* 7: 3505. https://doi.org/10.1038/s41598-017-03469-3
- Kanmegne Tamga D, Latifi H, Ullmann T *et al.* 2022. *Sensors* 23: 349. https://doi.org/10.3390/s23010349
- Numbisi FN, Van Coillie F, De Wulf R. 2019. *ISPRS International Journal of Geo-Information* 8: 179. https://doi.org/10.3390/ijgi8040179
- Numbisi FN, Van Coillie F. 2020. *Remote Sensing* 12: 4163. https://doi.org/10.3390/rs12244163
- Planetary Computer, coleção `sentinel-1-rtc`: https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-1-rtc
- BDC/INPE, coleções `sentinel-1-rtc-1` e `sentinel-1-grd-bundle-1`: https://data.inpe.br/bdc/stac/v1
- JAXA EORC, mosaicos PALSAR-2: https://www.eorc.jaxa.jp/ALOS/en/dataset/fnf_e.htm
- ASF, aviso de dados NISAR públicos (só pela busca, não aberto): https://asf.alaska.edu/notices/nisar-l-band-data-now-publicly-available/
