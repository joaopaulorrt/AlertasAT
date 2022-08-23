"""Módulo com funções para filtrar a DataFrame de CATs tratada, de acordo com as preferências do usuário"""

import re
import pandas as pd


def uf(cats: pd.DataFrame, usuario: pd.Series) -> pd.DataFrame:
    """Filtra a DataFrame de CATs, de acordo com os critérios selecionados pelo usuário no formulário de inscrição

        Args:
            cats: DataFrame contendo as CATs tratadas
            usuario: Pandas Series contendo os dados do usuário

        Returns:
            DataFrame contendo as CATs que atendam aos critérios do usuário
        """
    if cats.empty:
        return cats

    df = cats.copy()
    uf_selecionada = usuario['UF'] if isinstance(usuario['UF'], str) else None

    if uf_selecionada:
        filtro_uf = df['sguf_local_acidente'] == uf_selecionada
        return df[filtro_uf]
    else:
        return df


def uorg(cats: pd.DataFrame, usuario: pd.Series) -> pd.DataFrame:
    """Filtra a DataFrame de CATs, de acordo com os critérios selecionados pelo usuário no formulário de inscrição

        Args:
            cats: DataFrame contendo as CATs tratadas
            usuario: Pandas Series contendo os dados do usuário

        Returns:
            DataFrame contendo as CATs que atendam aos critérios do usuário
        """
    if cats.empty:
        return cats

    df = cats.copy()
    uorg_selecionada = re.findall(r'[0-9]{9}', usuario['UORG'])[0] if isinstance(usuario['UORG'], str) else None

    if uorg_selecionada:
        filtro_uorg = df['uorg_local_acidente'] == uorg_selecionada
        return df[filtro_uorg]
    else:
        return df


def tpacid(cats: pd.DataFrame, usuario: pd.Series) -> pd.DataFrame:
    """Filtra a DataFrame de CATs, de acordo com os critérios selecionados pelo usuário no formulário de inscrição

        Args:
            cats: DataFrame contendo as CATs tratadas
            usuario: Pandas Series contendo os dados do usuário

        Returns:
            DataFrame contendo as CATs que atendam aos critérios do usuário
        """
    if cats.empty:
        return cats

    df = cats.copy()

    dict_tp_acid = {'Acidentes típicos': 1, 'Doenças do Trabalho': 2, 'Acidentes de Trajeto': 3}
    lista_tpacid = list(map(dict_tp_acid.get, usuario['Tipo de acidente'].split(', ')))

    filtro_tpacid = df['tpacid'].isin(lista_tpacid)

    return df[filtro_tpacid]


def consequencias(cats: pd.DataFrame, usuario: pd.Series) -> pd.DataFrame:
    """Filtra a DataFrame de CATs, de acordo com os critérios selecionados pelo usuário no formulário de inscrição

        Args:
            cats: DataFrame contendo as CATs tratadas
            usuario: Pandas Series contendo os dados do usuário

        Returns:
            DataFrame contendo as CATs que atendam aos critérios do usuário
        """
    if cats.empty or 'Todos' in usuario['Consequência do acidente']:
        return cats

    df = cats.copy()
    lista_consequencias = usuario['Consequência do acidente'].split(', ')
    filtro_consequencias = df['Consequencia'].apply(lambda x: not set(x).isdisjoint(lista_consequencias))
    return df[filtro_consequencias]


def risco(cats: pd.DataFrame, usuario: pd.Series) -> pd.DataFrame:
    """Filtra a DataFrame de CATs, de acordo com os critérios selecionados pelo usuário no formulário de inscrição

        Args:
            cats: DataFrame contendo as CATs tratadas
            usuario: Pandas Series contendo os dados do usuário

        Returns:
            DataFrame contendo as CATs que atendam aos critérios do usuário
        """
    if cats.empty or usuario['Fator de risco'] == 'Não':
        return cats

    df = cats.copy()
    lista_risco = re.findall(r'[0-9]{3}', usuario['Fatores de risco'])
    filtro_risco = df['CDFatorAmbiental'].apply(lambda x: not set(x).isdisjoint(lista_risco))
    return df[filtro_risco]


def cnae(cats: pd.DataFrame, usuario: pd.Series) -> pd.DataFrame:
    """Filtra a DataFrame de CATs, de acordo com os critérios selecionados pelo usuário no formulário de inscrição

        Args:
            cats: DataFrame contendo as CATs tratadas
            usuario: Pandas Series contendo os dados do usuário

        Returns:
            DataFrame contendo as CATs que atendam aos critérios do usuário
        """
    if cats.empty or usuario['Setores econômicos'] == 'Não':
        return cats

    df = cats.copy()
    lista_cnae = re.findall(r'(?:^|,\s)([A-Z]) -', usuario['Seção CNAE'])
    filtro_cnae = df['secao_cnae_local_acidente'].isin(lista_cnae)
    return df[filtro_cnae]
