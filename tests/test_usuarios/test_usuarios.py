import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
import src.usuarios as usuarios
from src.utils import read_yaml

# Importa configurações do sistema
cfg = read_yaml('config/config.yaml')
fatores_risco_inativos = read_yaml('config/fatores_risco_inativos.yaml')
consequencia_inativos = read_yaml('config/consequencia_inativos.yaml')
uorg_inativos = read_yaml('config/uorg_inativos.yaml')


class TestCompilaInscricoes:
    def test_duplicidade(self):
        inscricoes = pd.DataFrame([{'E-mail': 'joao.reis@economia.gov.br', 'Timestamp': '2022-07-27 10:00:00'},
                                   {'E-mail': 'joao.reis@economia.gov.br', 'Timestamp': '2022-07-27 10:00:10'}])

        cancelamentos = pd.DataFrame([{'E-mail': 'rosita.dantas@economia.gov.br', 'Timestamp': '2022-07-27 10:00:10'}])

        esperado = pd.DataFrame([{'E-mail': 'joao.reis@economia.gov.br',
                                  'Timestamp_incricao': np.datetime64('2022-07-27T10:00:10'),
                                  'Timestamp_cancelamento': np.datetime64('NaT'),
                                  'intervalo': np.timedelta64('NaT'),
                                  'vigente': True
                                  }])

        resultado = usuarios.compila_inscricoes(inscricoes, cancelamentos)

        assert_frame_equal(esperado, resultado)

    def test_cancelamento(self):
        inscricoes = pd.DataFrame([{'E-mail': 'joao.reis@economia.gov.br', 'Timestamp': '2022-07-27 10:00:00'},
                                   {'E-mail': 'rosita.dantas@economia.gov.br', 'Timestamp': '2022-07-27 10:00:10'}])

        cancelamentos = pd.DataFrame([{'E-mail': 'joao.reis@economia.gov.br', 'Timestamp': '2022-07-27 10:00:30'}])

        esperado = pd.DataFrame([{'E-mail': 'rosita.dantas@economia.gov.br',
                                  'Timestamp_incricao': np.datetime64('2022-07-27T10:00:10'),
                                  'Timestamp_cancelamento': np.datetime64('NaT'),
                                  'intervalo': np.timedelta64('NaT'),
                                  'vigente': True
                                  }])

        resultado = usuarios.compila_inscricoes(inscricoes, cancelamentos)

        assert_frame_equal(esperado, resultado, check_index_type=False)


class TestOpcoesFormularioInscricao:
    # Testes para verificar se os valores na planilha que alimenta o formulário de inscrição são válidos
    def test_uorg(self):
        """Testa se os valores na coluna 'UORG' da planilha que alimenta o formulário de inscrição são válidos"""

        df_valid_values = usuarios.import_google_spreadsheet(cfg['FORM_INSC_OPCOES']['ID_GSHEET'])
        assert df_valid_values.UORG.str.contains(r'[0-9]{9}').all()

    def test_cnae(self):
        """Testa se os valores na coluna 'Seção CNAE' da planilha que alimenta o formulário de inscrição são válidos"""

        df_valid_values = usuarios.import_google_spreadsheet(cfg['FORM_INSC_OPCOES']['ID_GSHEET'])
        assert df_valid_values['Seção CNAE'].str.contains(r'^[A-Z]\s').all()

    def test_fatores_risco(self):
        """Testa se os valores na coluna 'Fatores de risco' da planilha que alimenta o formulário de inscrição são válidos"""

        df_valid_values = usuarios.import_google_spreadsheet(cfg['FORM_INSC_OPCOES']['ID_GSHEET'])
        assert df_valid_values['Fatores de risco'].str.contains(r'^[0-9]{3}\s').all()


class TestInscricao:
    def test_insc_col_names(self):
        """Testa se as colunas na planilha com os resultados do formulário de inscrição correspondem às colunas esperadas"""

        esperado = set(cfg['FORM_INSC']['COLS'])

        resultado = set(usuarios.import_google_spreadsheet(cfg['FORM_INSC']['ID_GSHEET']).columns)

        assert resultado == esperado

    def test_insc_tipo_acidente_validation(self):
        """Testa se os valores na coluna 'Tipo de Acidente' são valores válidos"""

        df_valid_values = usuarios.import_google_spreadsheet(cfg['FORM_INSC_OPCOES']['ID_GSHEET'])
        valid_values_tpacid = set(df_valid_values['Tipo de acidente'].dropna().to_list())

        inscricoes = usuarios.import_google_spreadsheet(cfg['FORM_INSC']['ID_GSHEET'])

        values_tpacid = set(inscricoes['Tipo de acidente'].str.split(', ').explode().unique())

        assert values_tpacid.issubset(valid_values_tpacid)

    def test_insc_uorg_validation(self):
        """Testa se os valores na coluna 'UORG' dos dados de inscrição são válidos"""

        df_valid_values = usuarios.import_google_spreadsheet(cfg['FORM_INSC_OPCOES']['ID_GSHEET'])
        valid_values_uorg = set(df_valid_values.UORG.str.extract(r'([0-9]{9})', expand=False).dropna().to_list())
        valid_values_uorg_including_deprecated = valid_values_uorg | uorg_inativos.keys()

        inscricoes = usuarios.import_google_spreadsheet(cfg['FORM_INSC']['ID_GSHEET'])

        values_uorg = set(inscricoes['UORG'].str.extract(r'([0-9]{9})', expand=False).dropna().unique())

        assert values_uorg.issubset(valid_values_uorg_including_deprecated)

    def test_insc_consequencia_validation(self):
        """Testa se os valores na coluna 'Consequência do acidente' dos dados de inscrição são válidos"""

        df_valid_values = usuarios.import_google_spreadsheet(cfg['FORM_INSC_OPCOES']['ID_GSHEET'])
        valid_values_consequencia = set(df_valid_values['Consequência do acidente'].dropna().to_list())
        # valid_values_consequencia_including_deprecated = valid_values_consequencia | consequencia_inativos.keys()
        # Todo fazer a conversão antes de checar valid values
        inscricoes = usuarios.import_google_spreadsheet(cfg['FORM_INSC']['ID_GSHEET'])

        values_consequencia = set(inscricoes['Consequência do acidente'].str.split(', ').explode().dropna().unique())

        assert values_consequencia.issubset(valid_values_consequencia_including_deprecated)

    def test_insc_cnae_validation(self):
        """Testa se os valores na coluna 'Seção CNAE' dos dados de inscrição são válidos"""

        df_valid_values = usuarios.import_google_spreadsheet(cfg['FORM_INSC_OPCOES']['ID_GSHEET'])
        valid_values_cnae = set(df_valid_values['Seção CNAE'].str[:1].dropna().to_list())

        inscricoes = usuarios.import_google_spreadsheet(cfg['FORM_INSC']['ID_GSHEET'])

        values_cnae = set(inscricoes['Seção CNAE'].str.findall(r'(?:^|\s)([A-Z])\s').explode().dropna().unique())

        assert values_cnae.issubset(valid_values_cnae)

    def test_insc_risco_validation(self):
        """Testa se os valores na coluna 'UORG' dos dados de inscrição são válidos"""

        df_valid_values = usuarios.import_google_spreadsheet(cfg['FORM_INSC_OPCOES']['ID_GSHEET'])
        valid_values_risco = set(df_valid_values['Fatores de risco'].str.extract(r'([0-9]{3})', expand=False).dropna().to_list())
        valid_values_risco_including_deprecated = valid_values_risco | fatores_risco_inativos.keys()

        inscricoes = usuarios.import_google_spreadsheet(cfg['FORM_INSC']['ID_GSHEET'])

        values_risco = set(inscricoes['Fatores de risco'].str.findall(r'([0-9]{3})').explode().dropna().unique())

        assert values_risco.issubset(valid_values_risco_including_deprecated)
