# skill-planejamento-tributario

Skill para Claude (Claude Code, Claude Desktop/Cowork e claude.ai) que atua como **consultor de
planejamento tributário** para empresas brasileiras, com foco no **Espírito Santo**.

> ⚠️ Material técnico de apoio. Não substitui o contador (CRC) nem o advogado (OAB) responsável.
> A legislação muda com frequência. Cada referência traz a data da última verificação, e os
> itens marcados `[VERIFICAR]` precisam ser confirmados na fonte oficial antes do uso.

## O que a skill cobre

- **Escolha de regime:** Simples Nacional × Lucro Presumido × Lucro Real, com simulador em Python
  (Anexos do Simples, Fator R, sublimite, presunções da LC 224/2025, PIS/COFINS cumulativo e não
  cumulativo, JCP, compensação de prejuízos, SUDENE).
- **Espírito Santo:**
  - COMPETE-ES (seções de rochas ornamentais e de moagem de calcários e mármores, entre outras) e
    INVEST-ES;
  - LC 160/2017;
  - ICMS-ES (alíquotas, minerais, transferências, crédito acumulado);
  - SUDENE nos 31 municípios do norte do ES;
  - FUNDAP.
- **Reforma tributária do consumo:**
  - EC 132/2023, LC 214/2025, LC 227/2026 e regulamentos de 2026;
  - transição 2026-2033 e alíquotas estimadas;
  - Simples no regime regular de IBS/CBS;
  - saldos credores;
  - Imposto Seletivo;
  - Fundo de Compensação de benefícios de ICMS.
- **Reforma da renda:** Lei 15.270/2025 (IRRF de 10% sobre dividendos, IRPFM, redutor) e LC
  224/2025 (presunção +10%, JCP a 17,5%, corte de benefícios federais).
- **Mineração:**
  - CFEM;
  - créditos de insumos;
  - calcário, carbonato de cálcio e corretivos de solo;
  - rochas ornamentais e brita;
  - IS na extração.
- **Método:** limites do planejamento lícito, escala de risco, checklist de dados e modelo de
  relatório.

## Estrutura

```
SKILL.md                      # instruções principais (fluxo, regras, calendário crítico)
references/                   # base de conhecimento carregada sob demanda
  metodo-e-riscos.md
  simples-nacional.md
  simples_tabelas.json        # Anexos I-V oficiais (2026 e 2027-2028 com CBS/IBS)
  lucro-presumido.md
  lucro-real.md
  reforma-renda-2026.md
  reforma-tributaria-consumo.md
  espirito-santo.md
  mineracao.md
scripts/
  simulador_regimes.py        # comparativo de regimes + projeção 2026-2033 (só biblioteca padrão)
  exemplo_entrada.json        # exemplo fictício
```

## Instalação

**Claude Code (pessoal):**

```bash
git clone https://github.com/FabiospSanches/skill-planejamento-tributario ~/.claude/skills/skill-planejamento-tributario
```

**Claude Code (só em um projeto):** clone em `.claude/skills/skill-planejamento-tributario` dentro
do projeto.

**Via CLI skills.sh:**

```bash
npx skills add FabiospSanches/skill-planejamento-tributario
```

**claude.ai / Claude Desktop:**

1. Baixe o ZIP do repositório (Code → Download ZIP).
2. Envie em Configurações → Capacidades → Skills.

## Como usar

Peça normalmente. A skill é acionada por temas como "planejamento tributário", "qual o melhor
regime", "COMPETE-ES", "impacto da reforma tributária", "distribuição de lucros" etc. Exemplos:

- "Compare Simples, Presumido e Real para esta empresa com base na DRE e nos livros de saída."
- "A empresa mói calcário no ES e vende carbonato de cálcio para fábricas de tinta. Vale aderir ao
  COMPETE-ES?"
- "Monte o calendário de decisões da reforma tributária para 2026-2027."
- "Quanto o sócio vai pagar de IRPFM se distribuirmos R$ 1,2 milhão em 2026?"

Para rodar o simulador direto:

```bash
python scripts/simulador_regimes.py scripts/exemplo_entrada.json --projecao
```

As convenções de cada campo estão no topo do script. O resultado é uma estimativa de ordem de
grandeza: base anual (a apuração real do Presumido é trimestral), ICMS informado pelo usuário e
transição do Simples aproximada.

## Fontes

Legislação no Planalto, Receita Federal, CGIBS, CONFAZ, SEFAZ-ES, SEDES-ES, ALES, SUDENE, ANM,
STF e STJ. Os links estão no fim de cada arquivo de `references/`.

## Contribuições

Correções de legislação são bem-vindas via issue ou pull request. Sempre indique a fonte oficial e
a data.

## Licença

MIT. Veja [LICENSE](LICENSE).
