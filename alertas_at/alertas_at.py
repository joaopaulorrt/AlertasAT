"""Módulo principal do sistema"""


if __name__ == '__main__':
    import os
    from utils import backup, backup_new_file
    from helpers_gform import import_google_spreadsheet, compila_inscricoes
    from parameters import ID_GSHEET_INSC, ID_GSHEET_CANCEL, ID_GSHEET_INSC_OPCOES
    from parameters import ROOT_DIR

    opcoes = import_google_spreadsheet(ID_GSHEET_INSC_OPCOES)
    inscricoes = import_google_spreadsheet(ID_GSHEET_INSC)
    cancelamentos = import_google_spreadsheet(ID_GSHEET_CANCEL)

    backup_folder = os.path.join(f'{ROOT_DIR}', 'data', 'log')
    backup_new_file(opcoes, directory=backup_folder, filename='opcoes_form_insc.csv')
    backup(inscricoes, backup_path=os.path.join(backup_folder, 'inscricoes.csv'))
    backup(cancelamentos, backup_path=os.path.join(backup_folder, 'cancelamentos.csv'))

