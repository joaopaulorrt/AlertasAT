import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from alertas_at import helpers_gform


def test_compila_inscricoes_duplicidade():
    inscricoes = pd.DataFrame([{'E-mail': 'joao.reis@economia.gov.br', 'Timestamp': '2022-07-27 10:00:00'},
                               {'E-mail': 'joao.reis@economia.gov.br', 'Timestamp': '2022-07-27 10:00:10'}])

    cancelamentos = pd.DataFrame([{'E-mail': 'rosita.dantas@economia.gov.br', 'Timestamp': '2022-07-27 10:00:10'}])

    esperado = pd.DataFrame([{'E-mail': 'joao.reis@economia.gov.br',
                              'Timestamp_incricao': np.datetime64('2022-07-27T10:00:10'),
                              'Timestamp_cancelamento': np.datetime64('NaT'),
                              'intervalo': np.timedelta64('NaT'),
                              'vigente': True
                              }])

    resultado = helpers_gform.compila_inscricoes(inscricoes, cancelamentos)

    assert_frame_equal(esperado, resultado)


def test_compila_inscricoes_cancelamento():
    inscricoes = pd.DataFrame([{'E-mail': 'joao.reis@economia.gov.br', 'Timestamp': '2022-07-27 10:00:00'},
                               {'E-mail': 'rosita.dantas@economia.gov.br', 'Timestamp': '2022-07-27 10:00:10'}])

    cancelamentos = pd.DataFrame([{'E-mail': 'joao.reis@economia.gov.br', 'Timestamp': '2022-07-27 10:00:30'}])

    esperado = pd.DataFrame([{'E-mail': 'rosita.dantas@economia.gov.br',
                              'Timestamp_incricao': np.datetime64('2022-07-27T10:00:10'),
                              'Timestamp_cancelamento': np.datetime64('NaT'),
                              'intervalo': np.timedelta64('NaT'),
                              'vigente': True
                              }])

    resultado = helpers_gform.compila_inscricoes(inscricoes, cancelamentos)

    assert_frame_equal(esperado, resultado, check_index_type=False)

# TODO TEST (integration) - Nomes das colunas
# TODO TEST (integration) - Parâmetros dentro de lista de parâmetros válidos
