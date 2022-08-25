""""Funções auxiliares para classificão dos acidentes por consequencia"""
import pandas as pd


def obito(s: pd.Series):
    if s['indcatobito'] == 'S':
        return 'Óbito'
    else:
        return None


def internacao(s: pd.Series):
    if s['indinternacao'] == 'S':
        return 'Internação do trabalhador'
    else:
        return None

# Todo não está funcionando
def amputacao_exceto_dedo(s: pd.Series):
    condicao1 = (s['dsclesao'] == 'S'
                 & ~s['codparteating'].isin(['755070000', '757070000']) )

    condicao2 = (s['codcidCategoria'].isin(['S08', 'S18', 'S48', 'S58', 'S68', 'S78', 'S88', 'S98', 'T05'])
                 & ~s['codcid'].isin( ['S680', 'S681', 'S981', 'S982']) )

    if (condicao1 | condicao2):
        return 'Amputação (exceto dedo)'
    else:
        return None


def amputacao(s: pd.Series):
    if s['indinternacao'] == 'S':
        return 'Amputação (inclusive dedo)'
    else:
        return None


def fratura_exceto_dedo(s: pd.Series):
    if s['indinternacao'] == 'S':
        return 'Fratura (exceto dedo)'
    else:
        return None


def fratura(s: pd.Series):
    if s['indinternacao'] == 'S':
        return 'Fratura (inclusive dedo)'
    else:
        return None


def perda_visao(s: pd.Series):
    if s['indinternacao'] == 'S':
        return 'Perda de visão'
    else:
        return None


def perda_audicao(s: pd.Series):
    if s['indinternacao'] == 'S':
        return 'Perda de audição'
    else:
        return None


def tratamento_15(s: pd.Series):
    if s['durtrat'] > 15:
        return 'Duração estimada do tratamento superior a 15 dias'
    else:
        return None


def tratamento_30(s: pd.Series):
    if s['durtrat'] > 30:
        return 'Duração estimada do tratamento superior a 30 dias'
    else:
        return None
