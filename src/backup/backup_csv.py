"""Módulo com funções para salvar backups em arquivo .csv"""

from pathlib import Path
import pandas as pd
import os
from glob import glob
import csv
from datetime import datetime


def backup_csv(df: pd.DataFrame, backup_path: str):
    """Faz backup da Dataframe em arquivo .csv quando ela for diferente do último backup realizado. O backup sobrescreve
    o arquivo anterior, adicionando os novos registros.

    Args:
        df: Pandas DataFrame com os dados a serem salvos
        backup_path: Diretório e nome do arquivo a ser salvo. Deve ser incluindo o sufixo '.csv'
    """
    Path(os.path.dirname(backup_path)).mkdir(parents=True, exist_ok=True)
    df = df.astype(str)

    if not os.path.isfile(backup_path):
        df.to_csv(backup_path, index=False, quoting=csv.QUOTE_NONNUMERIC)

    else:
        df_backup = pd.read_csv(backup_path, dtype='object', keep_default_na=False)

        uniao = pd.concat([df_backup, df])
        compilado = uniao[~uniao.duplicated(keep='first')].reset_index(drop=True)

        compilado.to_csv(backup_path, index=False, quoting=csv.QUOTE_NONNUMERIC)


def backup_csv_new_file(df: pd.DataFrame, filename: str, directory: str):
    """Faz backup da Dataframe em arquivo .csv quando ela for diferente do último backup realizado. O backup se dá por
    meio da criação de um novo arquivo, com sufixo contendo data e hora.

    Args:
        df: Pandas DataFrame com os dados a serem salvos
        filename: Nome do arquivo a ser salvo, sem o sufixo '.csv'
        directory: Diretório em que será salvo o backup e no qual constam os backups anteriores.
    """
    Path(directory).mkdir(parents=True, exist_ok=True)
    backup_files = sorted(glob(f'{os.path.join(directory, filename)} *.csv'))
    agora_str = datetime.now().strftime("%Y-%m-%d T%H.%M.%S")
    df = df.astype(str)

    if len(backup_files) == 0:
        df.to_csv(f'{os.path.join(directory, filename)} {agora_str}.csv', index=False, quoting=csv.QUOTE_NONNUMERIC)
    else:
        last_backup = backup_files[-1]
        df_last_backup = pd.read_csv(last_backup, dtype='object', keep_default_na=False)
        if not df.equals(df_last_backup):
            df.to_csv(f'{os.path.join(directory, filename)} {agora_str}.csv', index=False, quoting=csv.QUOTE_NONNUMERIC)