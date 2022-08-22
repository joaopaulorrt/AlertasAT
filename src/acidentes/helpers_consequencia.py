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
