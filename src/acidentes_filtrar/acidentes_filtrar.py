"""Módulo com funções para filtrar a DataFrame de CATs tratada, de acordo com as preferências do usuário"""

import re
from functools import partial, reduce
from pathlib import Path
import pandas as pd
import os


def uf(cats: pd.DataFrame, usuario: pd.Series) -> pd.DataFrame:
    """Filtra a DataFrame de CATs por UF, de acordo com os critérios selecionados pelo usuário no formulário de inscrição

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
    """Filtra a DataFrame de CATs por UORG, de acordo com os critérios selecionados pelo usuário no formulário de
    inscrição

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
    """Filtra a DataFrame de CATs por tipo de acidente, de acordo com os critérios selecionados pelo usuário no
    formulário de inscrição

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
    """Filtra a DataFrame de CATs por consequência do acidente, de acordo com os critérios selecionados pelo usuário
    no formulário de inscrição

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
    """Filtra a DataFrame de CATs por fator de risco, de acordo com os critérios selecionados pelo usuário no
    formulário de inscrição

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
    """Filtra a DataFrame de CATs por CNAE, de acordo com os critérios selecionados pelo usuário no formulário de
    inscrição

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


def preferencias_usuario(cats: pd.DataFrame, usuario: pd.Series, log_alertas: Path):
    """Filtra CATs de acordo com as preferências do usuário

    Args:
        cats: DataFrama com as CATs a serem filtradas
        usuario: Pandas Series com as preferências dos usuários
        log_alertas: Path do log contendo os alertas anteriormente enviados aos usuários

    Returns:
        DataFrama com as CATs filtradas
    """
    funcoes_filtra_cats = [uf,
                           uorg,
                           tpacid,
                           consequencias,
                           risco,
                           cnae]

    funcoes_filtra_cats_partial = [partial(function, usuario=usuario) for function in funcoes_filtra_cats]

    cats_filtradas = reduce(lambda x, y: y(x), funcoes_filtra_cats_partial, cats)

    if os.path.exists(log_alertas):
        ja_notificadas = pd.read_csv(log_alertas)
        ja_notificadas_recibo = (ja_notificadas[ja_notificadas.email == usuario['E-mail']]
                                 .meta_nr_recibo
                                 .to_list())
        cats_filtradas = cats_filtradas[~cats_filtradas.meta_nr_recibo.isin(ja_notificadas_recibo)]

    return cats_filtradas


def preferencias_coordenador(cats: pd.DataFrame, coordenador: pd.Series, log_alertas: Path):
    """Filtra CATs de acordo com as preferências do coordenador

    Args:
        cats: DataFrama com as CATs a serem filtradas
        coordenador: Pandas Series com as preferências dos coordenadores
        log_alertas: Path do log contendo os alertas anteriormente enviados aos coordenadores

    Returns:
        DataFrama com as CATs filtradas
    """
    funcoes_filtra_cats = [tpacid,
                           consequencias,
                           risco,
                           cnae]

    funcoes_filtra_cats_partial = [partial(function, usuario=coordenador) for function in funcoes_filtra_cats]

    cats_filtradas = reduce(lambda x, y: y(x), funcoes_filtra_cats_partial, cats)

    if os.path.exists(log_alertas):
        ja_notificadas = pd.read_csv(log_alertas)
        ja_notificadas_recibo = (ja_notificadas[ja_notificadas.email == coordenador['E-mail']]
                                 .meta_nr_recibo
                                 .to_list())
        cats_filtradas = cats_filtradas[~cats_filtradas.meta_nr_recibo.isin(ja_notificadas_recibo)]

    return cats_filtradas
