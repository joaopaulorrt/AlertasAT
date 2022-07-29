"""Módulo com funções genéricas utilizadas em vários módulos do projeto"""
from pathlib import Path
import pandas as pd
import os
from glob import glob
import csv
from datetime import datetime


def backup(df: pd.DataFrame, backup_path: str):
    """Faz backup da Dataframe em arquivo .csv quando ela for diferente do último backup realizado. O backup sobrescreve
    o arquivo anterior, adicionando os novos registros.

    Args:
        df: Pandas DataFrame com os dados a serem salvos
        backup_path: Diretório e nome do arquivo a ser salvo. Deve ser incluindo o sufixo '.csv'
    """
    df_backup = pd.read_csv(backup_path, dtype='object')

    df_cols = list(df)  # Creates list of all column headers
    df[df_cols] = df[df_cols].astype(str)

    uniao = pd.concat([df_backup, df])
    compilado = uniao[~uniao.duplicated(keep='first')].reset_index(drop=True)

    Path(os.path.dirname(backup_path)).mkdir(parents=True, exist_ok=True)
    compilado.to_csv(backup_path, index=False, quoting=csv.QUOTE_NONNUMERIC)


def backup_new_file(df: pd.DataFrame, filename: str, directory: str):
    """Faz backup da Dataframe em arquivo .csv quando ela for diferente do último backup realizado. O backup se dá por
    meio da criação de um novo arquivo, com sufixo contendo data e hora.

    Args:
        df: Pandas DataFrame com os dados a serem salvos
        filename: Nome do arquivo a ser salvo, sem o sufixo '.csv'
        directory: Diretório em que será salvo o backup e no qual constam os backups anteriores.
    """
    last_backup = sorted(glob(f'{os.path.join(directory, filename)} *.csv'))[-1]
    df_last_backup = pd.read_csv(last_backup, dtype='object')

    df_cols = list(df)  # Creates list of all column headers
    df[df_cols] = df[df_cols].astype(str)

    if not df.equals(df_last_backup):
        Path(directory).mkdir(parents=True, exist_ok=True)

        agora_str = datetime.now().strftime("%Y-%m-%d T%H.%M.%S")
        df.to_csv(f'{os.path.join(directory, filename)} {agora_str}.csv', index=False, quoting=csv.QUOTE_NONNUMERIC)
