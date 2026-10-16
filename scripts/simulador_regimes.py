#!/usr/bin/env python3
"""
Simulador de regimes tributários — Simples Nacional × Lucro Presumido × Lucro Real
e projeção da transição da Reforma Tributária do consumo (2026-2033).

Uso:
    python simulador_regimes.py entrada.json            # tabela comparativa (Markdown)
    python simulador_regimes.py entrada.json --json     # saída em JSON
    python simulador_regimes.py entrada.json --projecao # + projeção CBS/IBS/ICMS 2026-2033

Somente biblioteca padrão. Todos os valores são ANUAIS, em R$.
O resultado é uma ESTIMATIVA de ordem de grandeza para comparar regimes; não substitui
a apuração oficial. Parâmetros legais com data marcada devem ser conferidos no texto
vigente (ver references/ da skill).

Convenções da entrada (ver exemplo_entrada.json):
- receita_bruta: vendas de bens/serviços SEM IPI destacado, COM ICMS (como na DRE).
- custos_despesas_operacionais: custos e despesas BRUTOS (valores pagos, inclusive tributos
  recuperáveis embutidos nas compras), EXCLUINDO ICMS/IPI/PIS/COFINS a recolher, IRPJ, CSLL,
  INSS patronal e DAS. Inclui salários, pró-labore, FGTS, CFEM, energia, insumos, fretes,
  depreciação etc. Assim o lucro antes do IR é comparável entre regimes.
- icms_liquido_regime_normal: ICMS a recolher (débitos − créditos − benefícios como
  COMPETE-ES/INVEST-ES) fora do Simples. icms_debitos_saidas: ICMS destacado nas vendas
  (excluído da base de PIS/COFINS — STF Tema 69).
"""

import argparse
import json
import sys

# ---------------------------------------------------------------------------
# Parâmetros legais (conferir vigência — ver references/)
# ---------------------------------------------------------------------------

# LC 123/2006, Anexos I a V (redação da LC 155/2016). Faixas: (limite superior RBT12,
# alíquota nominal, parcela a deduzir, partilha por tributo na faixa).
SIMPLES = {
    "I": [  # Comércio
        (180_000.00, 0.040, 0.00, {"IRPJ": .055, "CSLL": .035, "COFINS": .1274, "PIS": .0276, "CPP": .415, "ICMS": .34}),
        (360_000.00, 0.073, 5_940.00, {"IRPJ": .055, "CSLL": .035, "COFINS": .1274, "PIS": .0276, "CPP": .415, "ICMS": .34}),
        (720_000.00, 0.095, 13_860.00, {"IRPJ": .055, "CSLL": .035, "COFINS": .1274, "PIS": .0276, "CPP": .42, "ICMS": .335}),
        (1_800_000.00, 0.107, 22_500.00, {"IRPJ": .055, "CSLL": .035, "COFINS": .1274, "PIS": .0276, "CPP": .42, "ICMS": .335}),
        (3_600_000.00, 0.143, 87_300.00, {"IRPJ": .055, "CSLL": .035, "COFINS": .1274, "PIS": .0276, "CPP": .42, "ICMS": .335}),
        (4_800_000.00, 0.190, 378_000.00, {"IRPJ": .135, "CSLL": .10, "COFINS": .2827, "PIS": .0613, "CPP": .421, "ICMS": 0.0}),
    ],
    "II": [  # Indústria
        (180_000.00, 0.045, 0.00, {"IRPJ": .055, "CSLL": .035, "COFINS": .1151, "PIS": .0249, "CPP": .375, "IPI": .075, "ICMS": .32}),
        (360_000.00, 0.078, 5_940.00, {"IRPJ": .055, "CSLL": .035, "COFINS": .1151, "PIS": .0249, "CPP": .375, "IPI": .075, "ICMS": .32}),
        (720_000.00, 0.100, 13_860.00, {"IRPJ": .055, "CSLL": .035, "COFINS": .1151, "PIS": .0249, "CPP": .375, "IPI": .075, "ICMS": .32}),
        (1_800_000.00, 0.112, 22_500.00, {"IRPJ": .055, "CSLL": .035, "COFINS": .1151, "PIS": .0249, "CPP": .375, "IPI": .075, "ICMS": .32}),
        (3_600_000.00, 0.147, 85_500.00, {"IRPJ": .055, "CSLL": .035, "COFINS": .1151, "PIS": .0249, "CPP": .375, "IPI": .075, "ICMS": .32}),
        (4_800_000.00, 0.300, 720_000.00, {"IRPJ": .085, "CSLL": .075, "COFINS": .2096, "PIS": .0454, "CPP": .235, "IPI": .35, "ICMS": 0.0}),
    ],
    "III": [  # Serviços (inclui Fator R >= 28% para atividades do Anexo V)
        (180_000.00, 0.060, 0.00, {"IRPJ": .04, "CSLL": .035, "COFINS": .1282, "PIS": .0278, "CPP": .434, "ISS": .335}),
        (360_000.00, 0.112, 9_360.00, {"IRPJ": .04, "CSLL": .035, "COFINS": .1405, "PIS": .0305, "CPP": .434, "ISS": .32}),
        (720_000.00, 0.135, 17_640.00, {"IRPJ": .04, "CSLL": .035, "COFINS": .1364, "PIS": .0296, "CPP": .434, "ISS": .325}),
        (1_800_000.00, 0.160, 35_640.00, {"IRPJ": .04, "CSLL": .035, "COFINS": .1364, "PIS": .0296, "CPP": .434, "ISS": .325}),
        (3_600_000.00, 0.210, 125_640.00, {"IRPJ": .04, "CSLL": .035, "COFINS": .1282, "PIS": .0278, "CPP": .434, "ISS": .335}),
        (4_800_000.00, 0.330, 648_000.00, {"IRPJ": .35, "CSLL": .15, "COFINS": .1603, "PIS": .0347, "CPP": .305, "ISS": 0.0}),
    ],
    "IV": [  # Serviços com CPP fora do DAS
        (180_000.00, 0.045, 0.00, {"IRPJ": .188, "CSLL": .152, "COFINS": .1767, "PIS": .0383, "ISS": .445}),
        (360_000.00, 0.090, 8_100.00, {"IRPJ": .198, "CSLL": .152, "COFINS": .2055, "PIS": .0445, "ISS": .40}),
        (720_000.00, 0.102, 12_420.00, {"IRPJ": .208, "CSLL": .152, "COFINS": .1973, "PIS": .0427, "ISS": .40}),
        (1_800_000.00, 0.140, 39_780.00, {"IRPJ": .178, "CSLL": .192, "COFINS": .189, "PIS": .041, "ISS": .40}),
        (3_600_000.00, 0.220, 183_780.00, {"IRPJ": .188, "CSLL": .192, "COFINS": .1808, "PIS": .0392, "ISS": .40}),
        (4_800_000.00, 0.330, 828_000.00, {"IRPJ": .535, "CSLL": .215, "COFINS": .2055, "PIS": .0445, "ISS": 0.0}),
    ],
    "V": [  # Serviços intelectuais com Fator R < 28%
        (180_000.00, 0.155, 0.00, {"IRPJ": .25, "CSLL": .15, "COFINS": .141, "PIS": .0305, "CPP": .2885, "ISS": .14}),
        (360_000.00, 0.180, 4_500.00, {"IRPJ": .23, "CSLL": .15, "COFINS": .141, "PIS": .0305, "CPP": .2785, "ISS": .17}),
        (720_000.00, 0.195, 9_900.00, {"IRPJ": .24, "CSLL": .15, "COFINS": .1492, "PIS": .0323, "CPP": .2385, "ISS": .19}),
        (1_800_000.00, 0.205, 17_100.00, {"IRPJ": .21, "CSLL": .15, "COFINS": .1574, "PIS": .0341, "CPP": .2385, "ISS": .21}),
        (3_600_000.00, 0.230, 62_100.00, {"IRPJ": .23, "CSLL": .125, "COFINS": .141, "PIS": .0305, "CPP": .2385, "ISS": .235}),
        (4_800_000.00, 0.305, 540_000.00, {"IRPJ": .35, "CSLL": .155, "COFINS": .1644, "PIS": .0356, "CPP": .295, "ISS": 0.0}),
    ],
}
SIMPLES_LIMITE = 4_800_000.00
SIMPLES_SUBLIMITE_ICMS_ISS = 3_600_000.00
FATOR_R_MINIMO = 0.28

# Lucro Presumido — percentuais de presunção (Lei 9.249/1995, arts. 15 e 20).
PRESUNCAO = {
    "comercio": (0.08, 0.12),
    "industria": (0.08, 0.12),
    "mineracao": (0.08, 0.12),
    "transporte_cargas": (0.08, 0.12),
    "servicos_hospitalares": (0.08, 0.12),
    "revenda_combustiveis": (0.016, 0.12),
    "transporte_passageiros": (0.16, 0.12),
    "servicos": (0.32, 0.32),
}

IRPJ_ALIQ = 0.15
IRPJ_ADICIONAL = 0.10
IRPJ_LIMITE_ADICIONAL_ANUAL = 240_000.00  # R$ 20 mil/mês; R$ 60 mil/trimestre
CSLL_ALIQ = 0.09
PIS_CUMULATIVO, COFINS_CUMULATIVO = 0.0065, 0.03
PIS_NAO_CUMULATIVO, COFINS_NAO_CUMULATIVO = 0.0165, 0.076
PIS_COFINS_RECEITA_FINANCEIRA = 0.0065 + 0.04  # Decreto 8.426/2015 (Lucro Real)
TRAVA_COMPENSACAO = 0.30

# Transição do consumo (EC 132/2023, LC 214/2025). Fração do ICMS/ISS mantida por ano;
# o IBS "cheio" entra na fração complementar a partir de 2029. 2026-2028: IBS teste 0,1%.
FATOR_ICMS = {2026: 1.0, 2027: 1.0, 2028: 1.0, 2029: 0.9, 2030: 0.8, 2031: 0.7, 2032: 0.6, 2033: 0.0}


def parametros_por_ano(ano, entrada):
    """Parâmetros que dependem do ano-calendário (sobrescrevíveis pela entrada)."""
    p = {
        # LC 224/2025: acréscimo de 10% nos percentuais de presunção sobre a parcela da
        # receita bruta que exceder R$ 5 milhões no ano (conferir references/lucro-presumido.md).
        # Limite proporcional por trimestre (R$ 1,25 mi) com ajuste no 4º trimestre — aqui em base anual.
        "lc224_ativo": ano >= 2026,
        "lc224_limite_anual": 5_000_000.00,
        "lc224_acrescimo": 0.10,
        # CSLL: acréscimo só a partir de 01/04/2026 (noventena) — em 2026 vale para 3/4 do ano,
        # com limite de R$ 3,75 mi. Supõe receita distribuída uniformemente no ano.
        "lc224_csll_fracao_ano": 0.75 if ano == 2026 else 1.0,
        # Alíquota zero de PIS/COFINS alcançada pelo corte (ex.: Lei 10.925/2004, art. 1º) passa a
        # 10% da alíquota padrão a partir de 01/04/2026 (LC 224/2025, art. 4º, § 4º).
        "lc224_aliquota_zero_fracao_ano": 0.75 if ano == 2026 else (1.0 if ano > 2026 else 0.0),
        # IRRF sobre JCP: 15% até 2025; 17,5% a partir de 2026 (LC 224/2025, art. 8º).
        "irrf_jcp": 0.175 if ano >= 2026 else 0.15,
        # SUDENE: 75% (projetos com condição onerosa aprovados até 31/12/2025); projetos novos
        # sujeitos ao corte de 10% da LC 224 (≈ 67,5%) — conferir laudo.
        "reducao_sudene": 0.75,
    }
    p.update(entrada.get("parametros", {}))
    return p


def v(entrada, chave, padrao=0.0):
    valor = entrada.get(chave, padrao)
    return float(valor) if valor is not None else float(padrao)


def irpj(base):
    base = max(base, 0.0)
    return base * IRPJ_ALIQ + max(base - IRPJ_LIMITE_ADICIONAL_ANUAL, 0.0) * IRPJ_ADICIONAL


def encargos_patronais(entrada):
    """INSS patronal fora do Simples: salários × (20% + RAT×FAP + terceiros) + pró-labore × 20%."""
    salarios = v(entrada, "folha_salarios")
    pro_labore = v(entrada, "pro_labore")
    perc = v(entrada, "encargos_patronais_percentual", 0.278)
    return salarios * perc + pro_labore * 0.20


def base_pis_cofins(entrada):
    """Receita tributável por PIS/COFINS (exclui exportação, alíquota zero e ICMS destacado)."""
    return max(
        v(entrada, "receita_bruta")
        - v(entrada, "receitas_exportacao")
        - v(entrada, "receitas_pis_cofins_aliquota_zero")
        - v(entrada, "receitas_aliquota_zero_lc224")
        - v(entrada, "icms_debitos_saidas"),
        0.0,
    )


def pis_cofins_aliquota_zero_lc224(entrada, p, aliquota_padrao):
    """Receita com alíquota zero alcançada pela LC 224/2025: 10% da alíquota padrão do regime."""
    return v(entrada, "receitas_aliquota_zero_lc224") * 0.10 * aliquota_padrao * p["lc224_aliquota_zero_fracao_ano"]


# ---------------------------------------------------------------------------
# Simples Nacional
# ---------------------------------------------------------------------------

def simples(entrada, avisos):
    receita = v(entrada, "receita_bruta")
    rbt12 = v(entrada, "rbt12", receita)
    anexo = str(entrada.get("anexo_simples", "II")).upper()
    salarios = v(entrada, "folha_salarios")
    pro_labore = v(entrada, "pro_labore")
    folha_fator_r = salarios + pro_labore + salarios * 0.08  # + FGTS
    fator_r = folha_fator_r / rbt12 if rbt12 else 0.0

    if anexo == "AUTO_FATOR_R":
        anexo = "III" if fator_r >= FATOR_R_MINIMO else "V"
    if anexo not in SIMPLES:
        raise ValueError(f"anexo_simples inválido: {anexo}")

    if rbt12 > SIMPLES_LIMITE:
        return {"elegivel": False, "motivo": f"RBT12 de {brl(rbt12)} acima do limite de R$ 4,8 mi"}
    if entrada.get("vedado_simples"):
        return {"elegivel": False, "motivo": str(entrada.get("vedado_simples"))}

    faixa_idx = next(i for i, f in enumerate(SIMPLES[anexo]) if rbt12 <= f[0])
    limite, nominal, deduzir, partilha = SIMPLES[anexo][faixa_idx]
    efetiva = (rbt12 * nominal - deduzir) / rbt12 if rbt12 else nominal

    acima_sublimite = rbt12 > SIMPLES_SUBLIMITE_ICMS_ISS
    excluir_global = {"ICMS", "ISS"} if acima_sublimite else set()

    # Parcelas de receita com tributos segregados (exportação, ICMS-ST, monofásico etc.).
    segregacoes = list(entrada.get("segregacoes_simples", []))
    exportacao = v(entrada, "receitas_exportacao")
    if exportacao:
        segregacoes.append({"valor": exportacao, "excluir": ["PIS", "COFINS", "ICMS", "IPI", "ISS"]})

    def aliquota_sem(excluir):
        return efetiva * (1 - sum(p for t, p in partilha.items() if t in excluir))

    das = 0.0
    receita_restante = receita
    for s in segregacoes:
        valor = float(s["valor"])
        receita_restante -= valor
        das += valor * aliquota_sem(excluir_global | set(s.get("excluir", [])))
    das += max(receita_restante, 0.0) * aliquota_sem(excluir_global)

    fora_das = {}
    if acima_sublimite:
        fora_das["ICMS (fora do DAS, acima do sublimite)"] = v(entrada, "icms_liquido_regime_normal")
        avisos.append("Simples: RBT12 acima do sublimite de R$ 3,6 mi — ICMS/ISS recolhidos fora do DAS.")
    if anexo == "IV":
        fora_das["CPP Anexo IV (fora do DAS)"] = salarios * (0.20 + v(entrada, "rat_fap", 0.03)) + pro_labore * 0.20
    if anexo == "II":
        avisos.append(
            "Simples: Anexo II só para industrialização com produto tributado pelo IPI (inclusive alíquota zero); "
            "extração de mineral com notação NT na TIPI vai no Anexo I (SC Cosit 424/2017, 63/2024). "
            "A partir de 2027, industrializados sem IPI mantido passam ao Anexo I (LC 214, art. 517)."
        )
    if int(entrada.get("ano_calendario", 2026)) >= 2027:
        avisos.append(
            "Simples: o simulador usa as tabelas de 2026; em 2027-2028 a partilha troca PIS/COFINS por CBS/IBS e a "
            "6ª faixa muda levemente (references/simples_tabelas.json, bloco anexos_2027_2028)."
        )

    tributos = {"DAS": das, **fora_das}
    return {
        "elegivel": True,
        "anexo": anexo,
        "faixa": faixa_idx + 1,
        "aliquota_nominal": nominal,
        "aliquota_efetiva": efetiva,
        "fator_r": fator_r,
        "tributos": tributos,
    }


# ---------------------------------------------------------------------------
# Lucro Presumido
# ---------------------------------------------------------------------------

def presumido(entrada, p, avisos):
    receita = v(entrada, "receita_bruta")
    outras = v(entrada, "outras_receitas")  # financeiras, ganhos de capital: 100% na base
    if receita + outras > 78_000_000.00:
        return {"elegivel": False, "motivo": "receita total acima de R$ 78 mi no ano anterior"}
    if entrada.get("obrigada_lucro_real"):
        return {"elegivel": False, "motivo": str(entrada.get("obrigada_lucro_real"))}

    atividade = entrada.get("atividade", "industria")
    p_irpj, p_csll = PRESUNCAO.get(atividade, PRESUNCAO["industria"])
    p_irpj = v(entrada, "presuncao_irpj", p_irpj)
    p_csll = v(entrada, "presuncao_csll", p_csll)

    def base_presumida(perc, fracao_ano=1.0):
        """Receitas fora do período alcançado ficam no percentual normal; no período alcançado,
        o percentual acrescido incide sobre o que exceder o limite proporcional."""
        if not p["lc224_ativo"]:
            return receita * perc
        alcancada = receita * fracao_ano
        limite = p["lc224_limite_anual"] * fracao_ano
        ate = min(alcancada, limite)
        excesso = max(alcancada - limite, 0.0)
        return receita * (1 - fracao_ano) * perc + ate * perc + excesso * perc * (1 + p["lc224_acrescimo"])

    base_ir = base_presumida(p_irpj) + outras
    base_cs = base_presumida(p_csll, p["lc224_csll_fracao_ano"]) + outras
    if p["lc224_ativo"] and receita > p["lc224_limite_anual"] * min(1.0, p["lc224_csll_fracao_ano"]):
        avisos.append(
            "Presumido: acréscimo de 10% na presunção sobre a receita acima de R$ 5 mi/ano (LC 224/2025; "
            "CSLL só desde 01/04/2026, limite de R$ 3,75 mi em 2026) calculado em base anual — a apuração "
            "é trimestral (R$ 1,25 mi/trimestre, com ajuste no 4º trimestre)."
        )

    base_pc = base_pis_cofins(entrada)
    pc_lc224 = pis_cofins_aliquota_zero_lc224(entrada, p, PIS_CUMULATIVO + COFINS_CUMULATIVO)
    tributos = {
        "IRPJ": irpj(base_ir),
        "CSLL": base_cs * CSLL_ALIQ,
        "PIS (cumulativo)": base_pc * PIS_CUMULATIVO + pc_lc224 * PIS_CUMULATIVO / (PIS_CUMULATIVO + COFINS_CUMULATIVO),
        "COFINS (cumulativo)": base_pc * COFINS_CUMULATIVO + pc_lc224 * COFINS_CUMULATIVO / (PIS_CUMULATIVO + COFINS_CUMULATIVO),
        "INSS patronal": encargos_patronais(entrada),
        "ICMS": v(entrada, "icms_liquido_regime_normal"),
        "IPI": v(entrada, "ipi_liquido_regime_normal"),
    }
    return {"elegivel": True, "base_irpj": base_ir, "base_csll": base_cs, "tributos": tributos}


# ---------------------------------------------------------------------------
# Lucro Real
# ---------------------------------------------------------------------------

def real(entrada, p, avisos):
    receita = v(entrada, "receita_bruta")
    outras = v(entrada, "outras_receitas")
    financeiras = v(entrada, "receitas_financeiras", outras)

    base_pc = base_pis_cofins(entrada)
    creditos_base = v(entrada, "compras_creditaveis_pis_cofins")
    debito_pc = base_pc * (PIS_NAO_CUMULATIVO + COFINS_NAO_CUMULATIVO)
    credito_pc = creditos_base * (PIS_NAO_CUMULATIVO + COFINS_NAO_CUMULATIVO)
    debito_pc += pis_cofins_aliquota_zero_lc224(entrada, p, PIS_NAO_CUMULATIVO + COFINS_NAO_CUMULATIVO)
    pis_cofins = max(debito_pc - credito_pc, 0.0) + financeiras * PIS_COFINS_RECEITA_FINANCEIRA
    if credito_pc > debito_pc:
        avisos.append(
            f"Real: créditos de PIS/COFINS excedem débitos em {brl(credito_pc - debito_pc)} — "
            "saldo credor (verificar possibilidade de compensação/ressarcimento, ex.: exportação/alíquota zero)."
        )

    inss = encargos_patronais(entrada)
    icms = v(entrada, "icms_liquido_regime_normal")
    ipi = v(entrada, "ipi_liquido_regime_normal")
    custos = v(entrada, "custos_despesas_operacionais")

    lucro_contabil = receita + outras - icms - ipi - pis_cofins - inss - custos
    jcp = v(entrada, "jcp")
    if jcp and jcp > 0.5 * max(lucro_contabil, 0.0):
        avisos.append(
            "Real: JCP acima de 50% do lucro do período — a dedução exige lucros do período ou lucros "
            "acumulados e reservas de lucros iguais a 2× os juros (Lei 9.249/1995, art. 9º, § 1º)."
        )
    ajustado = lucro_contabil - jcp + v(entrada, "adicoes_lalur") - v(entrada, "exclusoes_lalur")

    def compensar(base, saldo):
        if base <= 0:
            return base, 0.0
        uso = min(saldo, base * TRAVA_COMPENSACAO)
        return base - uso, uso

    lucro_real, uso_pf = compensar(ajustado, v(entrada, "prejuizo_fiscal_acumulado"))
    base_cs, uso_bn = compensar(ajustado, v(entrada, "base_negativa_csll_acumulada"))

    ir = irpj(lucro_real)
    if entrada.get("incentivo_sudene"):
        # Redução do IRPJ + adicional sobre o lucro da exploração (aprox.: todo o lucro real).
        reducao = p["reducao_sudene"] * ir * v(entrada, "proporcao_lucro_exploracao", 1.0)
        ir -= reducao
        if reducao > 0:
            avisos.append(
                f"Real: redução SUDENE de {brl(reducao)} aplicada (aproximação) — valor deve ir para "
                "reserva de incentivos fiscais e não pode ser distribuído."
            )

    tributos = {
        "IRPJ": ir,
        "CSLL": max(base_cs, 0.0) * CSLL_ALIQ,
        "PIS/COFINS (não cumulativo, líquido)": pis_cofins,
        "INSS patronal": inss,
        "ICMS": icms,
        "IPI": ipi,
    }
    if jcp:
        tributos["IRRF sobre JCP (ônus do sócio)"] = jcp * p["irrf_jcp"]
    return {
        "elegivel": True,
        "lucro_antes_ir": lucro_contabil,
        "lucro_real": max(lucro_real, 0.0),
        "compensacao_prejuizo": uso_pf,
        "compensacao_base_negativa": uso_bn,
        "tributos": tributos,
    }


# ---------------------------------------------------------------------------
# Comparação e projeção
# ---------------------------------------------------------------------------

def comparar(entrada):
    ano = int(entrada.get("ano_calendario", 2026))
    p = parametros_por_ano(ano, entrada)
    avisos = []
    if ano >= 2027:
        avisos.append(
            "A partir de 2027 o PIS/COFINS é substituído pela CBS (não cumulativa para Presumido e Real): "
            "o comparativo abaixo ainda mostra PIS/COFINS — use --projecao para a camada do consumo."
        )
    resultados = {
        "Simples Nacional": simples(entrada, avisos),
        "Lucro Presumido": presumido(entrada, p, avisos),
        "Lucro Real": real(entrada, p, avisos),
    }
    receita = v(entrada, "receita_bruta")
    custos = v(entrada, "custos_despesas_operacionais")
    outras = v(entrada, "outras_receitas")
    for r in resultados.values():
        if r.get("elegivel"):
            total = sum(r["tributos"].values())
            r["total_tributos"] = total
            r["carga_sobre_receita"] = total / receita if receita else 0.0
            onus_socio = r["tributos"].get("IRRF sobre JCP (ônus do sócio)", 0.0)
            r["resultado_apos_tributos"] = receita + outras - custos - (total - onus_socio)
    elegiveis = {k: r for k, r in resultados.items() if r.get("elegivel")}
    melhor = min(elegiveis, key=lambda k: elegiveis[k]["total_tributos"]) if elegiveis else None
    return {"ano_calendario": ano, "resultados": resultados, "menor_carga": melhor, "avisos": avisos}


def projecao_consumo(entrada):
    """Tributos sobre consumo no regime regular (Presumido/Real), 2026-2033 — ordem de grandeza.

    Premissas (sobrescreva em entrada["reforma"]): alíquotas de referência CBS e IBS;
    crédito amplo sobre compras_creditaveis_ibs_cbs; ICMS cai pelo FATOR_ICMS; IPI zera em 2027
    (fora da ZFM); IS na extração mineral sobre valor_extracao_is a partir de 2027.
    """
    r = entrada.get("reforma", {})
    cbs_ref = float(r.get("aliquota_cbs_referencia", 0.092))
    ibs_ref = float(r.get("aliquota_ibs_referencia", 0.187))
    reducao = float(r.get("reducao_aliquota", 0.0))  # ex.: 0.6 para redução de 60%
    parcela_reduzida = float(r.get("parcela_receita_com_reducao", 0.0))
    compras = float(r.get("compras_creditaveis_ibs_cbs", v(entrada, "compras_creditaveis_pis_cofins")))
    is_base = float(r.get("valor_extracao_is", 0.0))
    is_aliq = float(r.get("aliquota_is_extracao", 0.0025))

    receita_trib = max(v(entrada, "receita_bruta") - v(entrada, "receitas_exportacao") - v(entrada, "icms_debitos_saidas"), 0.0)
    fator_receita = (1 - parcela_reduzida) + parcela_reduzida * (1 - reducao)
    icms_atual = v(entrada, "icms_liquido_regime_normal")
    ipi_atual = v(entrada, "ipi_liquido_regime_normal")
    pis_cofins_real = real(entrada, parametros_por_ano(2026, entrada), [])["tributos"]["PIS/COFINS (não cumulativo, líquido)"]

    linhas = []
    for ano in range(2026, 2034):
        if ano == 2026:
            cbs = ibs = 0.0  # teste 0,9%/0,1% compensável com PIS/COFINS
            pis_cofins = pis_cofins_real
        else:
            pis_cofins = 0.0
            if ano <= 2028:
                cbs_aliq, ibs_aliq = cbs_ref - 0.001, 0.001
            else:
                cbs_aliq, ibs_aliq = cbs_ref, ibs_ref * (1 - FATOR_ICMS[ano])
            cbs = max(receita_trib * fator_receita * cbs_aliq - compras * cbs_aliq, 0.0)
            ibs = max(receita_trib * fator_receita * ibs_aliq - compras * ibs_aliq, 0.0)
        icms = icms_atual * FATOR_ICMS[ano]
        ipi = ipi_atual if ano == 2026 else 0.0
        is_ = is_base * is_aliq if ano >= 2027 else 0.0
        linhas.append({
            "ano": ano, "PIS/COFINS": pis_cofins, "CBS": cbs, "IBS": ibs, "ICMS": icms,
            "IPI": ipi, "IS": is_, "total_consumo": pis_cofins + cbs + ibs + icms + ipi + is_,
        })
    return {
        "premissas": {
            "aliquota_cbs_referencia": cbs_ref, "aliquota_ibs_referencia": ibs_ref,
            "compras_creditaveis_ibs_cbs": compras, "aliquota_is_extracao": is_aliq,
            "observacao": "Regime regular (Presumido e Real têm o mesmo tratamento de CBS/IBS). "
                          "Benefícios de ICMS (COMPETE/INVEST-ES) caem junto com o ICMS. Estimativa.",
        },
        "anos": linhas,
    }


# ---------------------------------------------------------------------------
# Saída
# ---------------------------------------------------------------------------

def brl(x):
    return ("R$ " + f"{x:,.2f}").replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x):
    return f"{x * 100:.2f}%".replace(".", ",")


def markdown(res, proj=None):
    out = [f"## Comparativo de regimes — ano-calendário {res['ano_calendario']}", ""]
    nomes = list(res["resultados"])
    tributos = []
    for r in res["resultados"].values():
        for t in r.get("tributos", {}):
            if t not in tributos:
                tributos.append(t)
    out.append("| Tributo | " + " | ".join(nomes) + " |")
    out.append("|---|" + "---:|" * len(nomes))
    for t in tributos:
        linha = [t]
        for n in nomes:
            r = res["resultados"][n]
            linha.append(brl(r["tributos"][t]) if r.get("elegivel") and t in r["tributos"] else "—")
        out.append("| " + " | ".join(linha) + " |")
    for rotulo, chave, fmt in (("**Total**", "total_tributos", brl), ("**Carga / receita**", "carga_sobre_receita", pct),
                               ("Resultado após tributos", "resultado_apos_tributos", brl)):
        linha = [rotulo]
        for n in nomes:
            r = res["resultados"][n]
            linha.append(fmt(r[chave]) if r.get("elegivel") else "inelegível")
        out.append("| " + " | ".join(linha) + " |")
    out.append("")
    for n, r in res["resultados"].items():
        if not r.get("elegivel"):
            out.append(f"- **{n}:** inelegível — {r['motivo']}")
    s = res["resultados"]["Simples Nacional"]
    if s.get("elegivel"):
        out.append(f"- **Simples:** Anexo {s['anexo']}, faixa {s['faixa']}, alíquota efetiva {pct(s['aliquota_efetiva'])}, Fator R {pct(s['fator_r'])}.")
    rl = res["resultados"]["Lucro Real"]
    out.append(f"- **Real:** lucro antes do IR {brl(rl['lucro_antes_ir'])}; lucro real {brl(rl['lucro_real'])}.")
    if res["menor_carga"]:
        out.append(f"- **Menor carga estimada:** {res['menor_carga']}.")
    for a in res["avisos"]:
        out.append(f"- ⚠️ {a}")
    if proj:
        out += ["", "## Projeção dos tributos sobre consumo — regime regular (2026-2033)", "",
                "| Ano | PIS/COFINS | CBS | IBS | ICMS | IPI | IS | Total |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for l in proj["anos"]:
            out.append("| {ano} | {a} | {b} | {c} | {d} | {e} | {f} | {g} |".format(
                ano=l["ano"], a=brl(l["PIS/COFINS"]), b=brl(l["CBS"]), c=brl(l["IBS"]), d=brl(l["ICMS"]),
                e=brl(l["IPI"]), f=brl(l["IS"]), g=brl(l["total_consumo"])))
        pr = proj["premissas"]
        out.append("")
        out.append(f"Premissas: CBS {pct(pr['aliquota_cbs_referencia'])}, IBS {pct(pr['aliquota_ibs_referencia'])} (referência), "
                   f"IS extração {pct(pr['aliquota_is_extracao'])}. {pr['observacao']}")
    out += ["", "_Estimativa para comparação de regimes. Confirme parâmetros legais vigentes e a apuração oficial._"]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Simulador Simples × Presumido × Real + projeção da reforma")
    ap.add_argument("entrada", help="arquivo JSON de entrada")
    ap.add_argument("--json", action="store_true", help="saída em JSON")
    ap.add_argument("--projecao", action="store_true", help="inclui projeção CBS/IBS/ICMS 2026-2033")
    args = ap.parse_args()
    with open(args.entrada, encoding="utf-8") as f:
        entrada = json.load(f)
    res = comparar(entrada)
    proj = projecao_consumo(entrada) if args.projecao else None
    if args.json:
        json.dump({"comparativo": res, "projecao": proj}, sys.stdout, ensure_ascii=False, indent=2)
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(markdown(res, proj))


if __name__ == "__main__":
    main()
