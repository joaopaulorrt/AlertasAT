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


def amputacao_exceto_dedo(s: pd.Series):
    cond_dsclesao = s['dsclesao'] == '702070000'
    cond_codparteating_not = s['codparteating'] not in ['755070000', '757070000']
    cond_codcidCategoria = s['codcidCategoria'] in ['S08', 'S18', 'S48', 'S58', 'S68', 'S78', 'S88', 'S98', 'T05']
    cond_codcid_not = s['codcid'] not in ['S680', 'S681', 'S682', 'S981', 'S982']

    if (cond_dsclesao and cond_codparteating_not) or (cond_codcidCategoria and cond_codcid_not):
        return 'Amputação (exceto dedo)'
    else:
        return None


def amputacao_dedo(s: pd.Series):
    cond_dsclesao = s['dsclesao'] == '702070000'
    cond_codparteating = s['codparteating'] in ['755070000', '757070000']
    cond_codcid = s['codcid'] in ['S680', 'S681', 'S682', 'S981', 'S982']

    if (cond_dsclesao and cond_codparteating) or cond_codcid:
        return 'Amputação (dedo)'
    else:
        return None


def fratura_exceto_dedo(s: pd.Series):
    cond_dsclesao = s['dsclesao'] == '702035000'
    cond_codparteating_not = s['codparteating'] not in ['755070000', '757070000']
    cond_codcidCategoria = s['codcidCategoria'] in ['S02', 'S04', 'S05', 'S06', 'S07', 'S09', 'S12', 'S14', 'S15',
                                                    'S16', 'S17', 'S19', 'S22', 'S24', 'S25', 'S26', 'S27', 'S28',
                                                    'S29', 'S32', 'S34', 'S35', 'S36', 'S37', 'S38', 'S39', 'S42',
                                                    'S44', 'S45', 'S46', 'S47', 'S49', 'S52', 'S54', 'S55', 'S56',
                                                    'S57', 'S59', 'S62', 'S64', 'S65', 'S66', 'S67', 'S69', 'S72',
                                                    'S74', 'S75', 'S76', 'S77', 'S79', 'S82', 'S84', 'S85', 'S86',
                                                    'S87', 'S89', 'S92', 'S94', 'S95', 'S96', 'S97', 'S99', 'T02',
                                                    'T04', 'T06', 'T07', 'T08', 'T09', 'T10', 'T11', 'T12', 'T13',
                                                    'T14']
    cond_codcid_not = s['codcid'] not in ['S625', 'S626', 'S627',
                                          'S643', 'S644',
                                          'S654', 'S655',
                                          'S661', 'S663', 'S665',
                                          'S670', ]

    if (cond_dsclesao and cond_codparteating_not) or (cond_codcidCategoria and cond_codcid_not):
        return 'Fratura (exceto dedo)'
    else:
        return None


def fratura_dedo(s: pd.Series):
    cond_dsclesao = s['dsclesao'] == '702035000'
    cond_codparteating = s['codparteating'] in ['755070000', '757070000']
    cond_codcid = s['codcid'] in ['S625', 'S626', 'S627',
                                  'S643', 'S644',
                                  'S654', 'S655',
                                  'S661', 'S663', 'S665',
                                  'S670', ]

    if (cond_dsclesao and cond_codparteating) or cond_codcid:
        return 'Fratura (dedo)'
    else:
        return None


def perda_visao(s: pd.Series):
    cond_codcid = s['codcid'] in ['H540', 'H544']

    if cond_codcid:
        return 'Perda de visão'
    else:
        return None


def perda_audicao(s: pd.Series):
    cond_codcid = s['codcid'] in ['H833', 'H900', 'H901', 'H902', 'H903', 'H904', 'H905', 'H906',
                                  'H907', 'H908', 'H910', 'H911', 'H912', 'H913', 'H918', 'H919']

    if cond_codcid:
        return 'Perda de audição'
    else:
        return None


def tratamento_15(s: pd.Series):
    if 15 < s['durtrat'] <= 30:
        return 'Duração estimada do tratamento entre 16 e 30 dias'
    else:
        return None


def tratamento_30(s: pd.Series):
    if s['durtrat'] > 30:
        return 'Duração estimada do tratamento superior a 30 dias'
    else:
        return None
