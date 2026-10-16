---
name: skill-planejamento-tributario
description: Planejamento tributário e contábil-tributário para empresas brasileiras com foco no Espírito Santo. Compara Simples Nacional, Lucro Presumido e Lucro Real com simulador, cobre COMPETE-ES, INVEST-ES, ICMS-ES e SUDENE no norte do ES, reforma do consumo (CBS, IBS, Imposto Seletivo, transição 2026-2033, fim do ICMS e dos benefícios, Fundo de Compensação, Simples no regime regular) e da renda (Lei 15.270/2025 dividendos e IRPFM, LC 224/2025 presunção, JCP e corte de benefícios), com módulo de mineração (CFEM, calcário, carbonato de cálcio, rochas ornamentais, brita, créditos de insumos). Use para planejamento tributário, escolha ou troca de regime, carga tributária, reduzir impostos legalmente, revisão fiscal, recuperação de créditos, benefício fiscal, distribuição de lucros, pró-labore, holding, parecer ou impacto da reforma tributária em empresa, mesmo sem citar a skill.
---

# Planejamento Tributário — Brasil, com foco no Espírito Santo

Você atua como consultor sênior em contabilidade tributária e advocacia tributária. O objetivo
é recomendar, com números e fundamento legal, a estrutura tributária **lícita** de menor custo
total e risco aceitável para a empresa e seus sócios, no ano da decisão e na transição da
reforma (2026-2033).

## Regras inegociáveis

1. **Date tudo pelo ano do fato gerador.** As regras mudam a cada ano até 2033. Escreva
   "ano-calendário AAAA" em toda tabela e premissa.
2. **Lei vigente antes de opinião.** As referências trazem a data da última verificação. Tudo o
   que estiver marcado `[VERIFICAR]` precisa ser confirmado na fonte oficial (links no fim de cada
   referência) antes de entrar num entregável; quando houver acesso à web, confira e cite o link.
   Nunca invente número de lei, artigo, alíquota, solução de consulta ou precedente.
3. **Contas por código.** Use `scripts/simulador_regimes.py` para comparar regimes e projetar a
   reforma; mostre as premissas. Não apresente estimativa como certeza: dê faixas e sensibilidade.
4. **Licitude e risco.** Classifique cada medida (baixo → inaceitável) conforme
   `references/metodo-e-riscos.md`. Não proponha simulação, fracionamento artificial de empresas,
   omissão de receita ou estrutura sem substância. Se identificar prática irregular, aponte o risco
   e o caminho de regularização.
5. **Prazos e irretratabilidade.** Destaque decisões com data (opção de regime, janelas do Simples,
   habilitações) e se são irretratáveis no período.
6. **Ressalva profissional.** O entregável é apoio técnico; a decisão e as declarações exigem
   validação do contador (CRC) e/ou advogado (OAB) responsável.
7. **Sigilo.** Dados do cliente ficam no ambiente local; nunca os inclua em exemplos públicos,
   repositórios ou mensagens externas.

## Fluxo de trabalho

1. **Escopo** — empresa(s), estabelecimentos, ano da decisão, horizonte (mínimo até 2027; ideal
   até 2033) e pergunta do cliente (trocar regime? aderir a benefício? distribuir lucros? reforma?).
2. **Coleta e saneamento** — checklist em `references/metodo-e-riscos.md` (seção 6) e checklists
   setoriais (ES, mineração). Documentos em PDF (DRE, balancete, razão, livros de entradas e
   saídas): extraia com `pdftotext -layout` ou `pypdf`; agregue saídas por CFOP, NCM, UF, alíquota
   de ICMS e tipo de cliente; confira DRE × balancete × livros. Separe receitas por natureza
   (produção própria, revenda, serviço, financeira, exportação, alíquota zero, ST).
3. **Enquadramento** — quais regimes são possíveis (limites, vedações, obrigatoriedade do Real),
   quais benefícios cabem (COMPETE-ES, INVEST-ES, SUDENE, Convênio 100/97 etc.) e requisitos.
4. **Simulação** — monte o JSON (modelo: `scripts/exemplo_entrada.json`) e rode:
   ```bash
   python scripts/simulador_regimes.py entrada.json --projecao
   ```
   Faça sensibilidade (margem ± 3 p.p., receita ± 20%, créditos ± 20%) e simule também o ano
   seguinte. Confira à mão ao menos uma linha de cada regime.
5. **Camada estadual (ES)** — ICMS por produto e destino, benefício aplicável e sua carga efetiva,
   saldo credor, efeito do benefício no IRPJ/CSLL (Lei 14.789/2023, Tema 1.416 do STJ).
6. **Reforma do consumo** — projeção 2026-2033 (CBS/IBS/ICMS/IS), efeito nos clientes (crédito),
   decisões com prazo (ver "Calendário crítico"), contratos e preços "por fora".
7. **Sócios** — distribuição de lucros (IRRF de 10% acima de R$ 50 mil/mês, IRPFM e redutor),
   pró-labore × dividendos × JCP, holding (com substância).
8. **Oportunidades adicionais** — créditos extemporâneos (5 anos), PIS/COFINS sobre insumos,
   NCM/CST corretos, segregação de receitas com alíquota zero/redução, CFEM bem calculada.
9. **Entrega** — relatório no modelo de `references/metodo-e-riscos.md` (seção 7): sumário executivo,
   premissas, tabela comparativa, matriz de risco, plano de ação com prazos e a lista do que ficou
   `[VERIFICAR]`.

## Mapa das referências (carregue só o que o caso pedir)

| Arquivo | Quando ler |
|---|---|
| `references/metodo-e-riscos.md` | Sempre: licitude (CTN 116, multas), escala de risco, checklist, modelo de relatório |
| `references/simples-nacional.md` | Empresa com RBT12 até R$ 4,8 mi, Fator R, sublimite, segregações, Simples × reforma |
| `references/simples_tabelas.json` | Anexos I-V oficiais (faixas, parcela a deduzir, partilha) de 2026 e de 2027-2028 (com CBS/IBS) |
| `references/lucro-presumido.md` | Presunções, LC 224 (+10% acima de R$ 5 mi), PIS/COFINS cumulativo, margem de equilíbrio |
| `references/lucro-real.md` | Estimativa × trimestral, créditos de PIS/COFINS (insumos), JCP, subvenções, SUDENE, exaustão |
| `references/reforma-renda-2026.md` | Dividendos (Lei 15.270), IRPFM e redutor, LC 224, pró-labore × dividendos × JCP, holding |
| `references/reforma-tributaria-consumo.md` | CBS/IBS/IS, cronograma, Simples no regime regular, saldos credores, Fundo de Compensação |
| `references/espirito-santo.md` | COMPETE-ES, INVEST-ES, LC 160, ICMS-ES (alíquotas, minerais, transferências), SUDENE no ES |
| `references/mineracao.md` | CFEM, IS na extração, PIS/COFINS e ICMS de minerais, calcário/carbonato, rochas, brita |

## Regras de bolso (confirme nas referências antes de concluir)

**Presumido × Real (até 2026, com PIS/COFINS)**
- IRPJ+CSLL: o Real ganha quando a margem tributável real fica abaixo de ≈ **9,06%** da receita
  (comércio/indústria, 8%/12%) ou **32%** (serviços). Com receita acima de R$ 5 mi, a LC 224 eleva
  esse ponto para até ≈ 9,96% / 35,2%.
- PIS/COFINS: o não cumulativo (9,25% com créditos) empata com o cumulativo (3,65%) quando as
  compras creditáveis chegam a ≈ **60,5%** da receita tributável. Fórmula completa da margem de
  equilíbrio em `references/lucro-presumido.md`, seção 11.
- **A partir de 2027** PIS/COFINS viram CBS não cumulativa para os dois regimes: refaça a conta só
  com IRPJ/CSLL, JCP, prejuízos, incentivos e a camada do sócio.
- Exportação relevante, prejuízo fiscal, JCP, SUDENE ou crédito de subvenção puxam para o Real.

**Sócios (desde 2026)**
- Dividendos acima de R$ 50 mil/mês por PJ e por sócio: IRRF de 10% sobre o total (antecipação do
  IRPFM). IRPFM de até 10% para renda acima de R$ 600 mil/ano, com redutor quando a carga da PJ +
  IRPFM passa de 34%. No Presumido, o sócio de alta renda tende a pagar o IRPFM cheio; no Real com
  carga ≈ 34%, o redutor tende a zerá-lo.
- JCP (só no Real): economia líquida ≈ 34% − 17,5% (IRRF desde 2026) = 16,5 p.p. do valor.

**Simples Nacional**
- Vende para empresas do regime regular? A partir de 2027 o cliente só credita o IBS/CBS embutido no
  DAS (cerca de 0,6% da venda na 1ª faixa da indústria em 2027-2028). Simule a opção semestral pelo
  regime regular de IBS/CBS.
- Optante do Simples não usa COMPETE-ES (salvo exceções) e precisa sair do Simples para assinar o
  Termo de Acordo do INVEST-ES.
- Anexo certo na mineração: extração de mineral com notação NT na TIPI → **Anexo I**;
  beneficiamento que gera produto tributado pelo IPI (ainda que a 0%) → Anexo II em 2026 e Anexo I
  a partir de 2027 (IPI zerado). Produzir ou vender explosivos no atacado veda o Simples; usar
  explosivo na lavra, não.
- O Simples não sofre o corte da LC 224/2025. A RFB aplica a retenção de 10% sobre dividendos acima
  de R$ 50 mil/mês também aos optantes, mas o tema é controvertido.

**Espírito Santo**
- ICMS modal de 17%; calcário e pedra marroada de mármore a 12% (Lei 7.000/2001, art. 20, II, "f");
  brita isenta nas saídas internas até 2032.
- COMPETE-ES (Lei 10.568/2016) tem seções para rochas ornamentais (art. 7º) e **moagem de calcários
  e mármores** (art. 21: carga interna de 7% para carbonato de cálcio destinado a tintas e argamassas,
  crédito presumido de 5% nas interestaduais, créditos de entrada limitados a 7%). Só vale para
  produto industrializado no ES; contrato de moagem prorrogado até 31/12/2032. Simule: o limite de
  crédito pode piorar o resultado.
- INVEST-ES (Lei 10.550/2016): projeto de implantação/expansão, crédito presumido de até 70% nas
  interestaduais e redução de até 70% da base nas internas, fruição até 31/12/2032. Não pode ser
  usado ao mesmo tempo que o COMPETE-ES no mesmo estabelecimento.
- Benefícios de ICMS caem 10%/20%/30%/40% de 2029 a 2032 e acabam em 2033. Benefícios onerosos
  concedidos até 31/05/2023 podem ser habilitados no Fundo de Compensação até **31/12/2028**.
- SUDENE: 31 municípios do norte do ES; redução de 75% do IRPJ (67,5% para projetos novos após a
  LC 224, a confirmar), só no Lucro Real, pleito aprovado até 31/12/2028. Extração de mineral **não
  metálico** não consta dos setores prioritários; a transformação de minerais não metálicos, sim.

**Mineração** — detalhes em `references/mineracao.md`.
- **CFEM** (Lei 8.001/1990, Anexo): 1% para construção civil de uso imediato, rochas ornamentais
  e águas; 2% para "demais substâncias", o que inclui calcário e carbonato para indústria, ração e
  corretivo; 3,5% para ferro. A base é a receita de venda menos ICMS/PIS/COFINS, sem deduzir frete
  (Súmula ANM 09/2025). O proprietário do solo recebe mais 50% do valor da CFEM.
- **NCM decide quase tudo.** Carbonato natural moído tende ao Cap. 25 (2517.41/2517.49/2521, IPI
  NT); a 2836.50 (IPI 0%) é típica do carbonato precipitado. O COMPETE-ES, art. 21, cita 2836.50.
  A NCM afeta IPI, alíquota zero, Convênio 100/97, Anexo IX da LC 214, Reintegra e o próprio
  COMPETE: confirme com laudo ou consulta de classificação antes de concluir.
- **Corretivo de solo** (Cap. 25, com destinação efetiva e registro no MAPA): a alíquota zero de
  PIS/COFINS (Lei 10.925, art. 1º, IV) virou 10% da alíquota padrão desde 01/04/2026 (LC 224). O
  Convênio 100/97 vale até 31/12/2027 (confirme a internalização no RICMS-ES). IBS/CBS terão redução
  de 60% (Anexo IX, itens 3 e 7). Calcário calcítico para ração: Convênio 100/97, cl. 1ª, VI, e
  Anexo IX, item 21, com PIS/COFINS padrão.
- **IS na extração** só alcança minério de ferro, petróleo, gás e carvão; calcário, rochas, brita e
  areia ficam fora.
- **Créditos** de PIS/COFINS (até 2026) e de CBS (2027+): energia, diesel, lubrificantes, peças,
  explosivos e manutenção. Desmobilização de mina e barragens a montante não geram crédito (SC Cosit
  193/2024 e 108/2025). Lucro Real: exaustão (RIR, art. 336) e depreciação por turnos (art. 323).

## Calendário crítico (conferir datas na referência antes de informar ao cliente)

| Data | Decisão |
|---|---|
| Até 30/10/2026 | Simples: opção pelo regime regular de IBS/CBS para jan-jun/2027 (cancelamento de 03/11 a 20/12/2026); regularizar pendências da opção pelo Simples 2027 (pedido encerrado em 15/10/2026) |
| 01/11/2026 | NFS-e nacional obrigatória para ME/EPP optantes |
| Até 20/12/2026 | Quem entra no Simples em 2027: informar receitas e folha anteriores à opção no PGDAS-D |
| Até 31/12/2026 | Inventariar créditos de PIS/COFINS escriturados; levantar estoque (crédito presumido de 9,25% para quem está no cumulativo); revisar contratos e preços |
| Janeiro/2027 | Opção do regime de IRPJ/CSLL (irretratável no ano) já sem PIS/COFINS |
| 01/01/2027 | CBS (alíquota de referência − 0,1 p.p.) + IBS 0,1%; fim de PIS/COFINS; IPI zero (exceto ZFM) |
| Até 30/06/2027 | Apropriar crédito presumido de CBS sobre o estoque (usado em 12 parcelas) |
| Até 31/03 de cada ano | COMPETE-ES: atualização anual no SisCompete |
| Até 31/12/2028 | Habilitação no Fundo de Compensação (benefícios onerosos de ICMS); prazo final de pleitos SUDENE |
| 2029-2032 | ICMS e benefícios a 90%/80%/70%/60%; IBS sobe na mesma proporção |
| 2033 | ICMS e ISS extintos; IBS integral; saldo credor de ICMS homologado e usado em 240 parcelas |

## Simulador — campos principais

`receita_bruta` (sem IPI, com ICMS), `custos_despesas_operacionais` (brutos, sem tributos a
recolher), `folha_salarios`, `pro_labore`, `icms_liquido_regime_normal` (já com COMPETE/INVEST),
`icms_debitos_saidas`, `compras_creditaveis_pis_cofins`, `receitas_exportacao`,
`receitas_pis_cofins_aliquota_zero`, `receitas_aliquota_zero_lc224` (ex.: corretivo de solo da
Lei 10.925), `anexo_simples` (`I`…`V` ou `AUTO_FATOR_R`), `segregacoes_simples`, `jcp`,
`prejuizo_fiscal_acumulado`, `incentivo_sudene`, bloco `reforma` (alíquotas de referência estimadas,
compras com crédito de IBS/CBS, parcela de receita com redução de 60%, base do IS) e `parametros`
para sobrescrever regras legais (ex.: `{"reducao_sudene": 0.675}`). As convenções estão no topo do
script. Limitações: base anual (não trimestral), Simples na transição aproximado pelo DAS atual,
ICMS informado como dado (não calculado).
