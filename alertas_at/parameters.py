"""Módulo com todas as constantes e parâmetros utilizados no projeto"""

# Formulário de inscrição
ID_GSHEET_INSC = '1BGNomIEkIgiPaPbMpeCArVCpERKK9TGHYFyT4Mt9grk'
NAME_WORKSHEET_INSC = 'sheet1'
GSHEET_INSC_COLS: list[str] = ['Timestamp', 'E-mail', 'Consequência do acidente', 'Abrangência geográfica',
                               'UF', 'UORG', 'Tipo de acidente', 'Setores econômicos', 'Seção CNAE',
                               'Fator de risco', 'Fatores de risco']
LINK_INSCRICAO = 'https://forms.gle/eGjE2vTw8ngeNCBGA'

OPCOES_INSCRICAO = 'https://docs.google.com/spreadsheets/d/1e4HI1t4aVx98ZqEBjFI75hxX-wysZkt3Zqea6b1c40k/edit#gid=0'
"""Link com planilha utilizada como base para popular os campos do dicionário de inscrição"""

OPCOES_INSCRICAO_SCRIPT = 'https://script.google.com/u/0/home/projects/1fFtDuIgWZAaDvpMthyMqNjTJXkxr1SMBmp9cQnek2fkyAd7Ej7d58-zR/edit'
"""Link com o script utilizado para popular, de forma automática, os campos do formulário de inscrição, com base na 
planilha do link apontado pela variável OPCOES_INSCRICAO"""

# Formulário de canelamento da inscrição
ID_GSHEET_CANCEL = '1bNqrMwDAPVNG8YxzEJt6sZNmtO9xEdHjIvDUw8c_oyY'
NAME_WORKSHEET_CANCEL = 'sheet1'
GSHEET_CANCEL_COLS: list[str] = ['Timestamp', 'E-mail']
LINK_CANCELAMENTO = 'https://forms.gle/bwHyvjMCGYkHZMPU7'
