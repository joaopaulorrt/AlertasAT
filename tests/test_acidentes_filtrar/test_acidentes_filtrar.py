import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
import acidentes_filtrar


def test_uf():
    df_usuarios = pd.Series({'UF': 'MG'})

    cats = pd.DataFrame([{'cat': '001', 'sguf_local_acidente': 'SP'},
                         {'cat': '002', 'sguf_local_acidente': 'MG'},
                         {'cat': '003', 'sguf_local_acidente': 'RJ'}
                         ])

    esperado = pd.DataFrame([{'cat': '002', 'sguf_local_acidente': 'MG'}])

    resultado = acidentes_filtrar.uf(cats, df_usuarios).reset_index(drop=True)

    assert_frame_equal(esperado, resultado)


def test_uf_nan():
    df_usuarios = pd.Series({'UF': np.NAN})

    cats = pd.DataFrame([{'cat': '001', 'sguf_local_acidente': 'SP'},
                         {'cat': '002', 'sguf_local_acidente': 'MG'},
                         {'cat': '003', 'sguf_local_acidente': 'RJ'}
                         ])

    esperado = pd.DataFrame([{'cat': '001', 'sguf_local_acidente': 'SP'},
                             {'cat': '002', 'sguf_local_acidente': 'MG'},
                             {'cat': '003', 'sguf_local_acidente': 'RJ'}
                             ])

    resultado = acidentes_filtrar.uf(cats, df_usuarios).reset_index(drop=True)

    assert_frame_equal(esperado, resultado)


def test_uorg():
    df_usuarios = pd.Series({'UORG': '123456789'})

    cats = pd.DataFrame([{'cat': '001', 'uorg_local_acidente': '000000000'},
                         {'cat': '002', 'uorg_local_acidente': '111111111'},
                         {'cat': '003', 'uorg_local_acidente': '123456789'}
                         ])

    esperado = pd.DataFrame([{'cat': '003', 'uorg_local_acidente': '123456789'}])

    resultado = acidentes_filtrar.uorg(cats, df_usuarios).reset_index(drop=True)

    assert_frame_equal(esperado, resultado)


def test_uorg_nan():
    df_usuarios = pd.Series({'UORG': np.NAN})

    cats = pd.DataFrame([{'cat': '001', 'uorg_local_acidente': '000000000'},
                         {'cat': '002', 'uorg_local_acidente': '111111111'},
                         {'cat': '003', 'uorg_local_acidente': '123456789'}
                         ])

    esperado = pd.DataFrame([{'cat': '001', 'uorg_local_acidente': '000000000'},
                             {'cat': '002', 'uorg_local_acidente': '111111111'},
                             {'cat': '003', 'uorg_local_acidente': '123456789'}
                             ])

    resultado = acidentes_filtrar.uorg(cats, df_usuarios).reset_index(drop=True)

    assert_frame_equal(esperado, resultado)


def test_tpacid():
    df_usuarios = pd.Series({'Tipo de acidente': 'Acidentes típicos'})

    cats = pd.DataFrame([{'cat': '001', 'tpacid': 1},
                         {'cat': '002', 'tpacid': 2},
                         {'cat': '003', 'tpacid': 3}
                         ])

    esperado = pd.DataFrame([{'cat': '001', 'tpacid': 1}])

    resultado = acidentes_filtrar.tpacid(cats, df_usuarios).reset_index(drop=True)

    assert_frame_equal(esperado, resultado)


def test_consequencias():
    df_usuarios = pd.Series({'Consequência do acidente': 'Óbito, Amputação (exceto dedo)'})

    cats = pd.DataFrame([{'cat': '001', 'Consequencia': ['Óbito']},
                         {'cat': '002', 'Consequencia': ['Amputação (exceto dedo)']},
                         {'cat': '003', 'Consequencia': ['Óbito', 'Internação do trabalhador']},
                         {'cat': '004', 'Consequencia': ['Internação do trabalhador']},
                         {'cat': '005', 'Consequencia': []}
                         ])

    esperado = pd.DataFrame([{'cat': '001', 'Consequencia': ['Óbito']},
                             {'cat': '002', 'Consequencia': ['Amputação (exceto dedo)']},
                             {'cat': '003', 'Consequencia': ['Óbito', 'Internação do trabalhador']},
                             ])

    resultado = acidentes_filtrar.consequencias(cats, df_usuarios).reset_index(drop=True)

    assert_frame_equal(esperado, resultado)


def test_consequencias_todos():
    df_usuarios = pd.Series({'Consequência do acidente': 'Óbito, Todos (incluindo acidentes que não geraram incapacidade temporária ou permanente)'})

    cats = pd.DataFrame([{'cat': '001', 'Consequencia': ['Óbito']},
                         {'cat': '002', 'Consequencia': ['Amputação (exceto dedo)']},
                         {'cat': '003', 'Consequencia': ['Óbito', 'Internação do trabalhador']},
                         {'cat': '004', 'Consequencia': ['Internação do trabalhador']},
                         {'cat': '005', 'Consequencia': []}
                         ])

    esperado = pd.DataFrame([{'cat': '001', 'Consequencia': ['Óbito']},
                             {'cat': '002', 'Consequencia': ['Amputação (exceto dedo)']},
                             {'cat': '003', 'Consequencia': ['Óbito', 'Internação do trabalhador']},
                             {'cat': '004', 'Consequencia': ['Internação do trabalhador']},
                             {'cat': '005', 'Consequencia': []}
                             ])

    resultado = acidentes_filtrar.consequencias(cats, df_usuarios).reset_index(drop=True)

    assert_frame_equal(esperado, resultado)


def test_risco():
    df_usuarios = pd.Series({'Fator de risco': 'Sim',
                             'Fatores de risco': '611 - Máquinas e equipamentos, 621 - Queda de pessoa com diferença de nível'})

    cats = pd.DataFrame([{'cat': '001', 'CDFatorAmbiental': ['611']},
                         {'cat': '002', 'CDFatorAmbiental': ['621']},
                         {'cat': '003', 'CDFatorAmbiental': ['611', '621']},
                         {'cat': '004', 'CDFatorAmbiental': ['611', '631']},
                         {'cat': '004', 'CDFatorAmbiental': ['112']},
                         {'cat': '004', 'CDFatorAmbiental': ['112', '211']},
                         {'cat': '005', 'CDFatorAmbiental': []}
                         ])

    esperado = pd.DataFrame([{'cat': '001', 'CDFatorAmbiental': ['611']},
                             {'cat': '002', 'CDFatorAmbiental': ['621']},
                             {'cat': '003', 'CDFatorAmbiental': ['611', '621']},
                             {'cat': '004', 'CDFatorAmbiental': ['611', '631']},
                             ])

    resultado = acidentes_filtrar.risco(cats, df_usuarios).reset_index(drop=True)

    assert_frame_equal(esperado, resultado)


def test_risco_nao_optado():
    df_usuarios = pd.Series({'Fator de risco': 'Não',
                             'Fatores de risco': np.NAN})

    cats = pd.DataFrame([{'cat': '001', 'CDFatorAmbiental': ['611']},
                         {'cat': '002', 'CDFatorAmbiental': ['621']},
                         {'cat': '003', 'CDFatorAmbiental': ['611', '621']},
                         {'cat': '004', 'CDFatorAmbiental': ['611', '631']},
                         {'cat': '004', 'CDFatorAmbiental': ['112']},
                         {'cat': '004', 'CDFatorAmbiental': ['112', '211']},
                         {'cat': '005', 'CDFatorAmbiental': []}
                         ])

    esperado = pd.DataFrame([{'cat': '001', 'CDFatorAmbiental': ['611']},
                             {'cat': '002', 'CDFatorAmbiental': ['621']},
                             {'cat': '003', 'CDFatorAmbiental': ['611', '621']},
                             {'cat': '004', 'CDFatorAmbiental': ['611', '631']},
                             {'cat': '004', 'CDFatorAmbiental': ['112']},
                             {'cat': '004', 'CDFatorAmbiental': ['112', '211']},
                             {'cat': '005', 'CDFatorAmbiental': []}
                             ])

    resultado = acidentes_filtrar.risco(cats, df_usuarios).reset_index(drop=True)

    assert_frame_equal(esperado, resultado)


def test_cnae():
    df_usuarios = pd.Series({'Setores econômicos': 'Sim',
                             'Seção CNAE': 'A - Agricultura, Pecuária, Produção Florestal, Pesca e Aqüicultura, B - Indústrias Extrativas'})

    cats = pd.DataFrame([{'cat': '001', 'secao_cnae_local_acidente': 'A'},
                         {'cat': '002', 'secao_cnae_local_acidente': 'B'},
                         {'cat': '003', 'secao_cnae_local_acidente': 'C'},
                         {'cat': '004', 'secao_cnae_local_acidente': np.NAN}
                         ])

    esperado = pd.DataFrame([{'cat': '001', 'secao_cnae_local_acidente': 'A'},
                             {'cat': '002', 'secao_cnae_local_acidente': 'B'},
                             ])

    resultado = acidentes_filtrar.cnae(cats, df_usuarios).reset_index(drop=True)

    assert_frame_equal(esperado, resultado)


def test_cnae_nao_optado():
    df_usuarios = pd.Series({'Setores econômicos': 'Não',
                             'Seção CNAE': np.NAN})

    cats = pd.DataFrame([{'cat': '001', 'secao_cnae_local_acidente': 'A'},
                         {'cat': '002', 'secao_cnae_local_acidente': 'B'},
                         {'cat': '003', 'secao_cnae_local_acidente': 'C'},
                         {'cat': '004', 'secao_cnae_local_acidente': np.NAN}
                         ])

    esperado = pd.DataFrame([{'cat': '001', 'secao_cnae_local_acidente': 'A'},
                             {'cat': '002', 'secao_cnae_local_acidente': 'B'},
                             {'cat': '003', 'secao_cnae_local_acidente': 'C'},
                             {'cat': '004', 'secao_cnae_local_acidente': np.NAN}
                             ])

    resultado = acidentes_filtrar.cnae(cats, df_usuarios).reset_index(drop=True)

    assert_frame_equal(esperado, resultado)
