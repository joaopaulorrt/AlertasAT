import pandas as pd
import os
from datetime import datetime
import shutil
from glob import glob
import src.backup as backup
from pathlib import Path
from time import sleep
import pytest
import csv
from pandas.testing import assert_frame_equal


@pytest.fixture()
def del_temp_dir():
    yield None
    shutil.rmtree("temp")


class TestBackupCSV:
    def test_novos_registros(self, del_temp_dir):
        """Testa se o backup é realizado quando há novos registros"""
        df = pd.DataFrame({'A': [1, 2, 3, 4],
                           'B': [1, 2, 3, 4]})

        last_backup = pd.DataFrame({'A': ['1', '2', '3'],
                                    'B': ['1', '2', '3']})

        esperado = pd.DataFrame({'A': ['1', '2', '3', '4'],
                                 'B': ['1', '2', '3', '4']})

        backup_path = os.path.join('temp', 'backup.csv')
        Path(os.path.dirname(backup_path)).mkdir(parents=True, exist_ok=True)

        last_backup.to_csv(backup_path, index=False, quoting=csv.QUOTE_NONNUMERIC)

        # Executa função
        backup.backup_csv(df=df, backup_path=backup_path)

        df_backup = pd.read_csv(backup_path, dtype='object')

        assert_frame_equal(df_backup, esperado)

    def test_sem_mudancas(self, del_temp_dir):
        """Testa se o backup deixa de ser realizado quando nada mudou"""
        df = pd.DataFrame({'A': [1, 2, 3],
                           'B': [1, 2, 3]})

        last_backup = pd.DataFrame({'A': ['1', '2', '3'],
                                    'B': ['1', '2', '3']})

        esperado = pd.DataFrame({'A': ['1', '2', '3'],
                                 'B': ['1', '2', '3']})

        backup_path = os.path.join('temp', 'backup.csv')
        Path(os.path.dirname(backup_path)).mkdir(parents=True, exist_ok=True)

        last_backup.to_csv(backup_path, index=False, quoting=csv.QUOTE_NONNUMERIC)

        # Executa função
        backup.backup_csv(df=df, backup_path=backup_path)

        df_backup = pd.read_csv(backup_path, dtype='object')

        assert_frame_equal(df_backup, esperado)


class TestBackupCSVNewFile:
    def test_com_mudancas(self, del_temp_dir):
        """Testa se o backup é realizado quando algo mudou"""
        df = pd.DataFrame({'A': [2, 3, 4],
                           'B': [2, 3, 4]})

        df_last_backup = pd.DataFrame({'A': ['1', '2', '3'],
                                       'B': ['1', '2', '3']})

        backup_path = 'temp'
        filename = 'test'

        # Salva backup
        Path(backup_path).mkdir(parents=True, exist_ok=True)
        backup_time = datetime.now().strftime("%Y-%m-%d T%H.%M.%S")
        df_last_backup.to_csv(f'{os.path.join(backup_path, filename)} {backup_time}.csv',
                              index=False,
                              quoting=csv.QUOTE_NONNUMERIC)
        sleep(1)

        # Executa função
        backup.backup_csv_new_file(df=df, filename=filename, directory=backup_path)

        assert len(glob(f'{os.path.join(backup_path, filename)} *.csv')) == 2

    def teste_sem_mudancas(self, del_temp_dir):
        """Testa se o backup deixa de ser realizado quando nada mudou"""
        df = pd.DataFrame({'A': [1, 2, 3],
                           'B': [1, 2, 3]})

        df_last_backup = pd.DataFrame({'A': ['1', '2', '3'],
                                       'B': ['1', '2', '3']})

        backup_path = 'temp'
        filename = 'test'

        # Salva backup
        Path(backup_path).mkdir(parents=True, exist_ok=True)
        backup_time = datetime.now().strftime("%Y-%m-%d T%H.%M.%S")
        df_last_backup.to_csv(f'{os.path.join(backup_path, filename)} {backup_time}.csv',
                              index=False,
                              quoting=csv.QUOTE_NONNUMERIC)
        sleep(1)

        # Executa função
        backup.backup_csv_new_file(df=df, filename=filename, directory=backup_path)

        assert len(glob(f'{os.path.join(backup_path, filename)} *.csv')) == 1
