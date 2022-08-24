"""Módulo com funções para importar e tratar dados de inscrições e cancelamentos das planilhas geradas a partir dos
formulários Google."""

import pandas as pd
from datetime import timedelta


def import_google_spreadsheet(spreadsheet_id: str, sheetname: str = 'sheet1') -> pd.DataFrame:
    """Importa dados de uma spreadsheet do Google para uma pandas DataFrame.
    Obs.: Todas as colunas são importadas como objeto.

    Args:
        spreadsheet_id: ID da Google spreadsheet, obtida através da URL
        sheetname: Nome da planilha que será importada, no âmbito da Spreadsheet

    Returns:
        Pandas DataFrame, com os dados importados
    """
    url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheetname}'
    return pd.read_csv(url, dtype='object')


def compila_inscricoes(df_inscricao: pd.DataFrame, df_cancelamento: pd.DataFrame) -> pd.DataFrame:
    """Compila a lista de inscrições válidas.
    Em caso de múltiplas inscrições, somente a última inscrição é considerada.

    Args:
        df_inscricao: DataFrame com os dados de inscrição, obtida a partir do formulário Google.
        df_cancelamento: DataFrame com os dados de cancelamento, obtida a partir do formulário Google.

    Returns:
        Pandas DataFrame, com as inscrições válidas
    """
    df_inscricao.Timestamp = pd.to_datetime(df_inscricao.Timestamp, format='%d/%m/%Y %H:%M:%S')
    df_cancelamento.Timestamp = pd.to_datetime(df_cancelamento.Timestamp, format='%d/%m/%Y %H:%M:%S')

    ultima_inscricao = df_inscricao.sort_values('Timestamp', ascending=False).groupby('E-mail').head(1)
    ultimo_cancelamento = df_cancelamento.sort_values('Timestamp', ascending=False).groupby('E-mail').head(1)

    compilado = ultima_inscricao.merge(ultimo_cancelamento,
                                       how='left',
                                       on='E-mail',
                                       suffixes=('_incricao', '_cancelamento'))

    compilado['intervalo'] = compilado.Timestamp_cancelamento - compilado.Timestamp_incricao
    compilado['vigente'] = (compilado.intervalo < timedelta(microseconds=0)) | (compilado.intervalo.isna())

    return compilado[compilado.vigente == 1]


def update_codigos_desativados(usuarios: pd.DataFrame, codigos_desativados: dict) -> pd.DataFrame:
    df = usuarios.copy()

    cols_to_update = ['Consequência do acidente', 'UORG', 'Fatores de risco']
    dict_update = [codigos_desativados['CONSEQUENCIA'],
                   codigos_desativados['UORG'],
                   codigos_desativados['FATOR_RISCO']]

    for col, dict_conversao in zip(cols_to_update, dict_update):
        for antigo, novo in dict_conversao.items():
            df[col] = df[col].str.replace(antigo, novo, regex=False)

    return df
