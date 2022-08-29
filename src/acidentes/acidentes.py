"""Módulo com funções para extrair e tratar e salvar em PDF dados das CATs"""
import functools
import pandas as pd
from datetime import datetime, timedelta
import sqlalchemy
import numpy as np
import os
from pathlib import Path
from jinja2 import Template
import weasyprint
import shutil
from . import helpers_consequencia
from .helpers_format_identificadores import format_cnae, format_cbo, format_nrinsc, format_cpf


def cat_extrair(log_execucoes: Path) -> pd.DataFrame:
    """Importa os dados das novas CATs recebidas ou, em caso de ausência de informação, dos últimos 7 dias.

    Args:
        log_execucoes: Path do arquivo .csv contendo o log de execuções do script.

    Returns:
        DataFrame com os dados das novas CATs
    """
    if os.path.exists(log_execucoes):
        df_log_execucoes = pd.read_csv(log_execucoes)
        ultima_cat = df_log_execucoes.ultima_cat_baixada.fillna('').max()
        query = f"""

            SELECT *
            FROM [DBCAT].[dbo].[TBCAT_eSocial]
            WHERE meta_nr_recibo > '{ultima_cat}'
            """

    else:
        sete_dias_atras = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
        query = f"""
    
            SELECT *
            FROM [DBCAT].[dbo].[TBCAT_eSocial]
            WHERE LEFT(meta_row_key, 8) >= {sete_dias_atras}
            """

    connection_url = sqlalchemy.engine.URL.create("mssql+pyodbc",
                                                  host="MARFIM",
                                                  database="DBCAT",
                                                  query={"driver": "ODBC Driver 17 for SQL Server"})

    connection_engine = sqlalchemy.create_engine(connection_url)

    return pd.read_sql_query(query, connection_engine)


def cat_converter_inteiros(df_cat: pd.DataFrame) -> pd.DataFrame:
    """Converte as colunas apropriadas de 'string' para 'int'

    Args:
        df_cat: DataFrame com os dados das CATs.

    Returns:
        DataFrame com os dados CATs tratados
    """
    df = df_cat.copy()

    cols_to_convert = ['durtrat']
    for col in cols_to_convert:
        df[col] = df[col].astype(int)

    return df


def cat_converter_datas(df_cat: pd.DataFrame) -> pd.DataFrame:
    """Converte as colunas com datas de 'string' para 'date'

    Args:
        df_cat: DataFrame com os dados das CATs.

    Returns:
        DataFrame com os dados CATs tratados
    """
    df = df_cat.copy()

    date_cols = ['dtadm', 'dtnascto', 'dtacid', 'dtobito', 'dtatendimento']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    return df


def cat_formatar_horas(df_cat: pd.DataFrame) -> pd.DataFrame:
    """Formata as strings relativas a horas.

    Args:
        df_cat: DataFrame com os dados das CATs.

    Returns:
        DataFrame com os dados CATs tratados
    """
    df = df_cat.copy()

    cols_horas = ['hracid', 'hrstrabantesacid', 'hratendimento']
    for col in cols_horas:
        df[col] = df[col].apply(lambda x: x[:2] + ':' + x[2:] if not pd.isna(x) else np.NAN)

    return df


def cat_formatar_strings(df_cat: pd.DataFrame) -> pd.DataFrame:
    """Remove os espaços em branco no início e fim das colunas contendo string.
    Args:
        df_cat: DataFrame com os dados das CATs.

    Returns:
        DataFrame com os dados CATs tratados
    """
    df = df_cat.copy()
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    return df


def cat_cid_uppercase(df_cat: pd.DataFrame) -> pd.DataFrame:
    """Converte para letras maiúsculas as strings da coluna contendo código CID.

    Args:
        df_cat: DataFrame com os dados das CATs.

    Returns:
        DataFrame com os dados CATs tratados
    """
    df = df_cat.copy()
    df.codcid = df.codcid.str.upper()
    return df


def cat_novas_colunas(df_cat: pd.DataFrame) -> pd.DataFrame:
    """Cria algumas novas colunas na DataFrame das CATs.

    Args:
        df_cat: DataFrame com os dados das CATs.

    Returns:
        DataFrame com os dados CATs tratados
    """
    df = df_cat.copy()
    df['idade_DTAcidente'] = ((df.dtacid - df.dtnascto) / np.timedelta64(1, 'Y')).round(0)
    df['DTEmissaoCAT'] = pd.to_datetime(df.meta_row_key.str[:8], errors='coerce')
    df['CDEmitenteCAT'] = '1'
    df['NRCAT'] = df['meta_nr_recibo']
    df['codcidCategoria'] = df['codcid'].str[:3]
    df['ultdiatrab'] = np.NAN
    return df


def cat_uorg_local_acidente(df_cat: pd.DataFrame, uorgs: Path, uf_uorgs: Path) -> pd.DataFrame:
    """Insere o código da UORG do local do acidente.

    Args:
        df_cat: DataFrame com os dados das CATs.
        uorgs: Path do arquivo .csv contendo os códigos de UORG por município.
        uf_uorgs: Path do arquivo .csv contendo as siglas de UF por UORG.

    Returns:
        DataFrame com os dados CATs tratados
    """
    df = df_cat.copy()

    df_uorgs = pd.read_csv(uorgs, dtype='object').set_index('CDMunicipio').to_dict()['NRUORG']
    df_uf_uorgs = pd.read_csv(uf_uorgs, dtype='object').set_index('CDUORG').to_dict()['SGUF']

    df['uorg_local_acidente'] = df['municipio_local_acidente'].map(df_uorgs)
    df['uf_uorg_local_acidente'] = df['uorg_local_acidente'].map(df_uf_uorgs)

    return df


def cat_secao_cnae_local_acidente(df_cat: pd.DataFrame, secoes_cnae: Path) -> pd.DataFrame:
    """Insere o código da Seção da CNAE do local do acidente.

    Args:
        df_cat: DataFrame com os dados das CATs.
        secoes_cnae: Path do arquivo .csv contendo a Seção da CNAE por subclasse.

    Returns:
        DataFrame com os dados CATs tratados
    """
    df = df_cat.copy()

    secao_cnae = (pd.read_csv(secoes_cnae, dtype='object')
                  .set_index('CDSubclasse')
                  .to_dict()['CDSecao'])

    df['secao_cnae_local_acidente'] = df['cnae_local_acidente'].map(secao_cnae)

    return df


def cat_formatar_datas(df_cat: pd.DataFrame) -> pd.DataFrame:
    """Converte as colunas de datas para string no formato 'dd/mm/yyyy'

    Args:
        df_cat: DataFrame com os dados das CATs.

    Returns:
        DataFrame com os dados CATs tratados
    """
    df = df_cat.copy()

    date_cols = ['dtadm', 'dtnascto', 'dtacid', 'dtobito', 'dtatendimento', 'DTEmissaoCAT']
    for col in date_cols:
        df[col] = df[col].dt.strftime('%d/%m/%Y')

    return df


def cat_formatar_identificadores(df_cat: pd.DataFrame) -> pd.DataFrame:
    """Formata CPF, CNPJ, CAEPF, CNO', CNAE e CBO

    Args:
        df_cat: DataFrame com os dados das CATs.

    Returns:
        DataFrame com os dados CATs tratados
    """
    df = df_cat.copy()

    for col in ['cnae_localtabgeral', 'cnae_local_acidente']:
        df[col] = df[col].apply(lambda x: format_cnae(x) if not pd.isna(x) else np.NaN)

    df['codcbo'] = df.codcbo.apply(lambda x: format_cbo(x) if not pd.isna(x) else np.NaN)

    df['nrinsc'] = df.apply(lambda x: format_nrinsc(x['tpinsc'], x['nrinsc']), axis=1)
    df['localtabgeral_nrinsc'] = df.apply(lambda x: format_nrinsc(x['localtabgeral_tpinsc'], x['localtabgeral_nrinsc']), axis=1)
    df['nrinsc_estab_local_acidente'] = df.apply(lambda x: format_nrinsc(x['tpinsc_estab_local_acidente'], x['nrinsc_estab_local_acidente']), axis=1)

    df['cpftrab'] = df.cpftrab.apply(lambda x: format_cpf(x) if not pd.isna(x) else np.NaN)

    return df


def cat_identifica_recibo_raiz(df_cat: pd.DataFrame) -> pd.DataFrame:
    """Em caso de uma ou mais reabertura(s) ou de comunicação de óbito, identifica o número do recibo da primeira CAT
    transmitida pelo empregador para o acidente/doença.

    Args:
        df_cat: DataFrame com os dados das CATs.

    Returns:
        DataFrame com os dados CATs tratados
    """
    df = df_cat.copy()
    dict_recibo_anterior = pd.Series(df.nrRecCatOrig.values, index=df.meta_nr_recibo).to_dict()

    @functools.cache
    def recibo_raiz(recibo):
        if pd.isna(dict_recibo_anterior[recibo]) or recibo == dict_recibo_anterior[recibo]:
            return recibo
        else:
            try:
                return recibo_raiz(dict_recibo_anterior[recibo])
            except KeyError:
                return dict_recibo_anterior[recibo]

    df['recibo_raiz'] = df.meta_nr_recibo.map(recibo_raiz)
    return df


def cat_mantem_recibo_ultima_reabertura(df_cat: pd.DataFrame) -> pd.DataFrame:
    """Em caso de uma ou mais reabertura(s) ou de comunicação de óbito, mantém na DataFrame somente a última CAT
    transmitida pelo empregador.

    Args:
        df_cat: DataFrame com os dados das CATs.

    Returns:
        DataFrame com os dados CATs tratados
    """
    df = df_cat.copy()
    df = (df
          .sort_values('meta_nr_recibo', ascending=False)
          .groupby('recibo_raiz', dropna=False)
          .head(1)
          .sort_values('meta_nr_recibo')
          .reset_index(drop=True)
          )
    return df


def cat_atribui_fatores_risco(df_cat: pd.DataFrame, fatores_params_reshaped: dict) -> pd.DataFrame:
    """Insere cinco colunas contendo códigos de fatores de risco relacionados ao acidente, baseados, respectivamente,
    nos valores das colunas 'codsitgeradora', 'codagntcausador', 'dsclesao', 'codcid' e 'codcidCategoria'

    Args:
        df_cat: DataFrame com os dados das CATs.
        fatores_params_reshaped: Dicionário informando, para os possíveis valores das colunas 'codsitgeradora',
        'codagntcausador', 'dsclesao' e 'codcid', qual o correspondente código do fator de risco.

    Returns:
        DataFrame com os dados CATs tratados
    """
    df = df_cat.copy()

    dict_new_columns = {'codsitgeradora_fr': {'col': 'codsitgeradora', 'map': 'CDAgenteSituacao'},
                        'codagntcausador_fr': {'col': 'codagntcausador', 'map': 'CDAgenteSituacao'},
                        'dsclesao_fr': {'col': 'dsclesao', 'map': 'dsclesao'},
                        'codcid_fr': {'col': 'codcid', 'map': 'codcid'},
                        'codcidCategoria_fr': {'col': 'codcidCategoria', 'map': 'codcidCategoria'},
                        'codcidCategoria_fr_not': {'col': 'codcid', 'map': 'codcid_not'}
                        }

    # Atribui o fator de risco de acordo com cada um dos critérios
    for new_col, map_dict in dict_new_columns.items():
        col_to_map = map_dict['col']
        dict_map = fatores_params_reshaped[map_dict['map']]

        df[new_col] = df[col_to_map].map(dict_map)

    df['codcidCategoria_fr'] = np.where(df['codcidCategoria_fr'] == df['codcidCategoria_fr_not'], np.nan,
                                        df['codcidCategoria_fr'])

    df = df.drop(columns=['codcidCategoria_fr_not'])

    return df


def cat_compila_fatores_risco(df_cat: pd.DataFrame) -> pd.DataFrame:
    """Compila as colunas contendo os códigos dos fatores de risco relacionados ao acidente em uma coluna única,
    contendo uma lista.

    Args:
        df_cat: DataFrame com os dados das CATs.

    Returns:
        DataFrame com os dados CATs tratados
    """
    df = df_cat.copy()

    def compila_fr_ordenados_sem_duplicidades(s: pd.Series):
        conjunto = {s['codsitgeradora_fr'], s['codagntcausador_fr'], s['dsclesao_fr'],
                    s['codcid_fr'], s['codcidCategoria_fr']}
        lista_sem_nulos = [x for x in conjunto if pd.isna(x) is False]
        return sorted(lista_sem_nulos)

    df['CDFatorAmbiental'] = df.apply(compila_fr_ordenados_sem_duplicidades, axis=1)

    return df


def cat_atribui_consequencia(df_cat: pd.DataFrame) -> pd.DataFrame:
    """ Cria uma coluna contendo a lista de consequências do acidente, conforme categorias pré-definidas.

    Args:
        df_cat: DataFrame com os dados das CATs.

    Returns:
        DataFrame com os dados CATs tratados
    """
    df = df_cat.copy()

    def consequencia(s: pd.Series):
        function_list = [helpers_consequencia.obito,
                         helpers_consequencia.internacao,
                         helpers_consequencia.amputacao_dedo,
                         helpers_consequencia.amputacao_exceto_dedo,
                         helpers_consequencia.fratura_dedo,
                         helpers_consequencia.fratura_exceto_dedo,
                         helpers_consequencia.perda_visao,
                         helpers_consequencia.perda_audicao,
                         helpers_consequencia.tratamento_15,
                         helpers_consequencia.tratamento_30]

        return [fun(s) for fun in function_list if fun(s) is not None]

    df['Consequencia'] = df.apply(consequencia, axis=1)

    return df


def cat_inserir_descricoes(df_cat: pd.DataFrame, aux_tables_dir: Path) -> pd.DataFrame:
    """ Insere colunas com as descrições dos códigos numéricos presentes em diversas colunas.

    Args:
        df_cat: DataFrame com os dados das CATs.
        aux_tables_dir: Path do diretório contendo os arquivos .csv das tabelas auxiliares.

    Returns:
        DataFrame com os dados CATs tratados
    """
    df = df_cat.copy()
    cols_to_map = {'tpacid': 'tpacid.csv',
                   'tplocal_acidente': 'tplocal_acidente.csv',
                   'tplograd_local_acidente': 'tplograd_local_acidente.csv',
                   'municipio_local_acidente': 'municipio.csv',
                   'pais_local_acidente': 'pais_local_acidente.csv',
                   'codagntcausador': 'codagntcausador.csv',
                   'codsitgeradora': 'codsitgeradora.csv',
                   'codparteating': 'codparteating.csv',
                   'lateralidade': 'lateralidade.csv',
                   'dsclesao': 'dsclesao.csv',
                   'codcid': 'codcid.csv',
                   'ideoc': 'ideoc.csv',
                   'codcbo': 'codcbo.csv',
                   'grauinstr': 'grauinstr.csv',
                   'racacor': 'racacor.csv',
                   'codcateg': 'codcateg.csv',
                   'tpinsc': 'tpinsc.csv',
                   'localtabgeral_tpinsc': 'tpinsc.csv',
                   'cnae_localtabgeral': 'cnae.csv',
                   'municipio_empregador': 'municipio.csv',
                   'tpinsc_estab_local_acidente': 'tpinsc.csv',
                   'cnae_local_acidente': 'cnae.csv',
                   'municipio_estab_local_acidente': 'municipio.csv',
                   'CDEmitenteCAT': 'CDEmitenteCAT.csv',
                   'iniciatcat': 'iniciatcat.csv',
                   'tpcat': 'tpcat.csv',
                   'indretif': 'indretif.csv',
                   'procemi': 'procemi.csv',
                   'inporte': 'inporte.csv'}

    cols_integer_as_index = ['tpinsc', 'localtabgeral_tpinsc', 'tpinsc_estab_local_acidente', 'grauinstr',
                             'racacor', 'tpacid', 'inporte', 'pais_local_acidente', 'tpcat', 'inporte', 'codcateg',
                             'tpcat', 'lateralidade', 'iniciatcat', 'indretif', ]

    for col, csv in cols_to_map.items():
        if col in cols_integer_as_index:
            df_map = pd.read_csv(aux_tables_dir / csv)
        else:
            df_map = pd.read_csv(aux_tables_dir / csv, dtype='object')
        dict_map = dict(zip(df_map.iloc[:, 0], df_map.iloc[:, 1]))
        df[f'ds_{col}'] = df[col].map(dict_map)

    return df


def cat_to_pdf(series: pd.Series,
               html_template: Path,
               logo: Path,
               output_dir: Path | None = None):
    """ Gera um PDF para a CAT.

    Args:
        series: Series com os dados da CAT
        html_template: Local do template HTML.
        logo:  Local do logo para ser inserido no template
        output_dir: Diretório de destino do arquivo PDF

    """
    nr_recibo = series.meta_nr_recibo

    html_path = output_dir / f'{nr_recibo}.html' if output_dir else f'{nr_recibo}.html'
    pdf_path = output_dir / f'{nr_recibo}.pdf' if output_dir else f'{nr_recibo}.pdf'

    if not os.path.isfile(output_dir / logo.name):
        shutil.copy(logo, output_dir / logo.name)

    if not os.path.isfile(pdf_path):
        series = series.fillna('N/A')

        with open(html_template, 'r', encoding='utf-8') as f:
            template = Template(f.read())

        cat_html = template.render({col: series[col] for col in series.index} | {'logo_path': logo.name})
        with open(html_path, 'w', encoding="utf-8") as file:
            file.write(cat_html)

        weasyprint.HTML(html_path, encoding="utf-8").write_pdf(pdf_path)

        os.remove(html_path)


def cat_tabela_resumo(df_cat: pd.DataFrame, fatores_risco: Path) -> pd.DataFrame:
    """Gera tabela com os principais campos da CAT, para ser anexada no corpo do email do alerta.

    Args:
        df_cat: DataFrame com os dados das CATs.
        fatores_risco: Path do arquivo .csv contendo as descrições dos fatores de risco.

    Returns:
        DataFrame com os dados CATs tratados
    """
    alerta_cols = ['meta_nr_recibo', 'ds_tpacid', 'Consequencia', 'CDFatorAmbiental',
                   'ds_municipio_local_acidente', 'sguf_local_acidente', ]
    df = df_cat[alerta_cols].copy()

    df.Consequencia = df.Consequencia.apply(lambda x: '<br>'.join(x))

    def map_fr(lista):
        map_dict = (pd.read_csv(fatores_risco, dtype='object')
                    .set_index('CDFatorAmbiental')['DSFatorAmbiental']
                    .to_dict())
        lista_mapped = [f'{elemento} - {map_dict[elemento]}' for elemento in lista]
        return '<br>'.join(lista_mapped)

    df['CDFatorAmbiental'] = df['CDFatorAmbiental'].apply(map_fr)

    df["Local do Acidente"] = df["ds_municipio_local_acidente"] + '/' + df["sguf_local_acidente"]

    df = (df
          .drop(columns=['ds_municipio_local_acidente', 'sguf_local_acidente'])
          .rename(columns={'meta_nr_recibo': 'Número da CAT',
                           'ds_tpacid': 'Tipo',
                           'Consequencia': 'Consequências',
                           'CDFatorAmbiental': 'Fatores de risco'}))

    return df
