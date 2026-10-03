# Bases e estudos de acústica passiva com aves na Mata Atlântica (além de WABAD, Soundscape_CCM1_exp01 e AnuraSet)

Data da busca: 2026-10-03 (semana 1 do piloto). Status: **busca incompleta, nada foi aberto na fonte**.

## Verificação posterior (2026-10-03, sessão principal)

Dois itens foram abertos na fonte depois desta busca:

- **1.1 Zenodo 10556620 — confirmado.** Registro "Data from: Acoustic monitoring of anurans and birds in Tropical biomes", publicado em 2024-01-23, licença CC BY 4.0 (campo do Zenodo), primeiros autores Rosa G. L. M., Albuquerque P., Alquezar R. D., Anjos L. dos *et al.* A descrição confirma listas de espécies feitas por especialistas em 14.044 gravações de 1 min e lista os conjuntos: Caatinga (#1, #2), Mata Atlântica do interior (#3, #4), Mata Atlântica costeira (#5), Cerrado (#6) e anfíbios (#8, #9). Os arquivos são CSVs (`data_03_PNI_43`, `data_04_PNI_PAM`, `data_05_DadosSC`, `data_06_PNB_12pontos` etc.); o download deles retornou HTTP 403, então colunas, coordenadas e datas continuam **não verificadas**. Não há áudio no registro, só listas. É o candidato mais promissor para o caminho B e deve passar pelo `auditor-de-bases`.
- **1.2 arXiv 2605.20578 — descartado.** É o PteroSet (Ruiz D. *et al.*, 2026): gravações em Puerto Asís (Putumayo) e Pivijay (Magdalena), Colômbia, 2023–2025. Fora da região do projeto.

O preprint da Authorea (2.1) retornou HTTP 403 e continua não verificado.

## Aviso sobre verificação

Nesta sessão o `WebFetch` foi bloqueado por um hook (que redireciona para ferramentas `ctx_fetch_and_index`) e essas ferramentas não estavam disponíveis. Só consegui usar `WebSearch`, que devolve títulos, URLs e trechos resumidos. Portanto **nenhuma referência abaixo foi aberta ou conferida na fonte**: todas são "menção indireta". Autores, DOI, licença, número de sítios e períodos precisam ser conferidos abrindo a página antes de qualquer uso no PRD. Onde não vi a informação, escrevo "não verificado" e não preencho.

## 1. Dados abertos (possíveis, a conferir)

### 1.1 "Data from: Acoustic monitoring of anurans and birds in Tropical biomes" (Zenodo)
- URL vista no resultado de busca: https://zenodo.org/records/10556620 (não aberta).
- Artigo associado (URL vista, não aberta): De Araújo et al., 2024, *Biotropica*, https://onlinelibrary.wiley.com/doi/10.1111/btp.13307. A autoria completa e o DOI do registro Zenodo não foram conferidos.
- O que o trecho de busca diz (não confirmado): listas de espécies feitas por especialistas por inspeção direta de 14.044 gravações de 1 min; gravadores AudioMoth, nov/2018 a mar/2019; inclui Mata Atlântica costeira e interior (um dos conjuntos: 48 pontos em 21 fragmentos de Mata Atlântica submontana secundária tardia, pontos a ≥100 m da borda e ≥200 m entre si); avalia como o esforço temporal e espacial afeta estimativas de diversidade de aves e anuros.
- Não verificado: áudio incluído ou só listas; coordenadas e datas por ponto; licença; localização exata (o dado de bioma "costeira" não diz se é a Bahia).
- Contato: autores do artigo (provável vínculo com o LEEC/UNESP Rio Claro, como o AnuraSet; **suposição minha, não verificada**).
- Relevância possível para o satbio: se tiver listas por espécie de aves por gravação, coordenadas e datas, seria uma base aberta para o caminho B (várias áreas independentes, rótulos por espécie feitos por especialistas, o que falta ao CCM1). Limite: provavelmente não é cabruca nem Bahia. Qualquer resultado obtido aqui precisa de teste antes de ser transferido para cabruca.

### 1.2 "A strongly annotated passive acoustic dataset for tropical bird monitoring" (arXiv 2605.20578)
- URL: https://arxiv.org/abs/2605.20578 (aparece nos resultados; não aberta). Não sei se inclui o Brasil ou a Mata Atlântica; o título diz apenas "tropical". Região, sítios, licença: não verificados.
- Ação: abrir e checar se há sítios brasileiros. Se não houver, descartar.

### 1.3 Descartado por região (só registro)
- SEABAD (arXiv 2605.20853), sudeste asiático, e o conjunto de leste da América do Norte (Zenodo 18041381): fora da região. Títulos vistos em busca; não abertos.

## 2. Possíveis via parceria

### 2.1 Preprint "Acoustic bird community composition (but not richness) responds to natural coverages in a tropical agro-cultural landscape" (Authorea)
- URL vista: https://www.authorea.com/doi/full/10.22541/au.176369414.44388497/v1 (não aberta); também a página https://www.authorea.com/users/1002249/articles/1362693-... .
- Do trecho de busca: tema é composição acústica de aves versus cobertura natural em paisagem agrícola tropical, com menção a corredores com árvores e bambu. **Não sei onde foi feito (Brasil ou não), quantos sítios, nem quem são os autores.** Pode não ter relação com a Mata Atlântica. Abrir antes de qualquer conclusão.

### 2.2 Grupos de cabruca/UESC
- Duas buscas direcionadas (cabruca, Ilhéus, UESC, AudioMoth) **não retornaram nenhum estudo de acústica passiva em cabruca**. Isso não prova que não existe: a busca web geral é fraca para literatura em português e para repositórios institucionais.
- Menção indireta, sem link aberto: um trecho dizia que cacauais têm diversidade alta de aves e abrigam espécies florestais. Origem do trecho não identificada; não usar como citação.

## 3. Lacunas

1. Nenhum conjunto aberto com áudio de aves em cabruca foi encontrado nesta busca.
2. Nenhuma referência pôde ser verificada na fonte (bloqueio de ferramenta), então a tabela de campos pedida (sítios, período, licença, acessibilidade) está quase toda "não verificado".
3. Não foram pesquisados: GBIF/Xeno-canto (contexto), Dryad, Figshare, SciELO, Google Scholar em português, Plataforma Lattes (UESC, UFSB, CEPLAC, Instituto Arapyaú/IESB, Projeto Mata Atlântica do Sul da Bahia), Wildlife Insights/ARBIMON, Sound Archive Fonoteca Neotropical Jacques Vielliard (UNICAMP).
4. Pesquisadores de aves em cabruca que fazem levantamentos por pontos de escuta (não acústica passiva) seriam possíveis parceiros de especialista, mas não foram buscados.

## 4. Implicações para o projeto

- Para o G1, hoje não há evidência de base aberta em cabruca; o caminho A depende de parceria ou campanha própria, e o B depende de a base 1.1 trazer sítios brasileiros com coordenadas e datas.
- Próximo passo mínimo: abrir o registro Zenodo 10556620 e o artigo de 2024 (metadados: coordenadas, datas, licença, o que é publicado), abrir o arXiv 2605.20578, e repetir a busca em Lattes/SciELO/Google Scholar com termos em português (cabruca, monitoramento acústico passivo, avifauna). Rodar isso em uma sessão com acesso a `WebFetch` ou às ferramentas ctx.
