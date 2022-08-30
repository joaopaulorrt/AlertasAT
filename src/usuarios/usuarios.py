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


def adiciona_uf_uorgs(df_usuarios: pd.DataFrame) -> pd.DataFrame:
    """Adiciona a UF para os usuários que optaram por receber alertas por UORG

    Args:
        df_usuarios: DataFrame com os dados de inscrições

    Returns:
        DataFrame com os dados de inscrições atualizados
    """
    df = df_usuarios.copy()

    df['uf_uorg'] = df.UORG.str.extract(r'^([A-Z]{2})\s-')
    df['UF'] = df.UF.fillna(df.uf_uorg)

    return df


def update_codigos_desativados(df_usuarios: pd.DataFrame, codigos_desativados: dict) -> pd.DataFrame:
    """Converte os códigos desativados presentes em inscrições antigas

    Args:
        df_usuarios: DataFrame com os dados de inscrições
        codigos_desativados: Dicionário com os valores de conversão de códigos antigos

    Returns:
        DataFrame com os dados de inscrições atualizados
    """
    df = df_usuarios.copy()

    cols_to_update = ['Consequência do acidente', 'UORG', 'Fatores de risco']
    dict_update = [codigos_desativados['CONSEQUENCIA'],
                   codigos_desativados['UORG'],
                   codigos_desativados['FATOR_RISCO']]

    for col, dict_conversao in zip(cols_to_update, dict_update):
        for antigo, novo in dict_conversao.items():
            df[col] = df[col].str.replace(antigo, novo, regex=False)

    return df


def usuarios(id_gsheet_insc: str, id_gsheet_canc: str, codigos_desativados: dict) -> pd.DataFrame:
    """Compila lista de usuários ativos no Serviço de Alerta de Acidentes do Trabalho.

    Args:
        id_gsheet_insc: ID da Google spreadsheet contendo os dados de Inscrição
        id_gsheet_canc: ID da Google spreadsheet contendo os dados de cancelamento
        codigos_desativados: Dicionário com os valores de conversão de códigos antigos

    Returns:
        DataFrame com lista de usuários ativos no Serviço de Alerta de Acidentes do Trabalho
    """
    # Importa listas de inscrições e cancelamentos e compila lista de usuários ativos
    inscricoes = import_google_spreadsheet(id_gsheet_insc)
    cancelamentos = import_google_spreadsheet(id_gsheet_canc)
    inscricoes_compilado = compila_inscricoes(df_inscricao=inscricoes, df_cancelamento=cancelamentos)
    inscricoes_compilado_novos_codigos = update_codigos_desativados(inscricoes_compilado, codigos_desativados)
    df_usuarios = adiciona_uf_uorgs(inscricoes_compilado_novos_codigos)

    return df_usuarios
