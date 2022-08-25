"""Módulo principal

Serviço de Alerta de Acidentes de Trabalho
Autor: João Paulo Reis Ribeiro Teixeira - joao.reis@economia.gov.br'
"""

import os
from datetime import datetime
from functools import reduce, partial

import pandas as pd

from utils import read_yaml
from pathlib import Path
import backup
import vpn_connection as vpn
import usuarios
import acidentes
import acidentes_filtrar
import email_sender

# # # # # # # # # # # # #
# Variáveis e parâmetros
# # # # # # # # # # # # #
root_dir = Path().resolve().parent

# Importa configurações do sistema
cfg = read_yaml(root_dir / 'config/config.yaml')
secrets = read_yaml(root_dir / 'config/secrets.yaml')
codigos_desativados = read_yaml(root_dir / 'config/codigos_desativados_conversao.yaml')
fatores_params = read_yaml(root_dir / 'config/fatores_risco_classificacao.yaml')
fatores_params_reshaped = acidentes.reshape_fatores_params(fatores_params)

# Indica diretórios e arquivos a serem utilizados
cat_html_template = Path('../data/input/html_templates/cat.html')
alerta_user_html_template = Path('../data/input/html_templates/alerta_usuario.html')
alerta_adm_html_template = Path('../data/input/html_templates/alerta_adm.html')

# Imagens
logo_sit = Path('../data/input/images/logoSIT.png')
logo_saat = Path('../data/input/images/logoSAAT_email.png')

# Cats em PDF
output_dir_cat_pdf = Path('../data/output/cat_pdf')

# LOGs
log_dir = Path('../data/log')
log_alertas_usuario = log_dir / 'log_alertas_usuarios.csv'
log_alertas_adm = log_dir / 'log_alertas_adm.csv'
log_execucoes = log_dir / 'log_execucoes.csv'

# Backup
backup_dir = str(root_dir / 'data/backup')

# Variáveis globais
admins_coord = list(set(cfg['admin'] + cfg['coordenador']))
dt_hoje_str = str(datetime.now().strftime("%d/%m/%Y"))
datetime_str = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# # # # # # # # # #
# Início da rotina
# # # # # # # # # #

try:
    # # # # # # # # # # # # # # # # # # # # #
    # Compila lista de usuários e faz backup
    # # # # # # # # # # # # # # # # # # # # #

    # Importa dados que populam as opções do formulário de inscrição
    opcoes = usuarios.import_google_spreadsheet(cfg['FORM_INSC_OPCOES']['ID_GSHEET'])

    # Importa listas de inscrições e cancelamentos e compila lista de usuários ativos
    inscricoes = usuarios.import_google_spreadsheet(cfg['FORM_INSC']['ID_GSHEET'])
    cancelamentos = usuarios.import_google_spreadsheet(cfg['FORM_CANCEL']['ID_GSHEET'])
    inscricoes_compilado = usuarios.compila_inscricoes(df_inscricao=inscricoes, df_cancelamento=cancelamentos)
    inscricoes_compilado_novos_codigos = usuarios.update_codigos_desativados(inscricoes_compilado, codigos_desativados)

    # Realiza backup dos dados provenientes dos formulários de inscrição e cancelamento
    backup.backup_csv_new_file(opcoes, directory=backup_dir, filename='opcoes_form_insc.csv')
    backup.backup_csv(inscricoes, backup_path=os.path.join(backup_dir, 'inscricoes.csv'))
    backup.backup_csv(cancelamentos, backup_path=os.path.join(backup_dir, 'cancelamentos.csv'))
    backup.backup_csv(inscricoes_compilado_novos_codigos, backup_path=os.path.join(backup_dir, 'inscricoes_compilado.csv'))

    # # # # # # # # # # #
    # Importa as CATs
    # # # # # # # # # # #

    # Tenta conectar à VPN
    vpn.try_connection_forticlient_vpn(vpn_path=cfg['VNP_PATH'],
                                       user=secrets['USER'],
                                       password=secrets['PASSWORD'],
                                       url_test_connection=cfg['VPN_URL_TEST_CONNECTION'])

    # Importa novas CATs
    cats = acidentes.cat_extrair()

    # # # # # # # # # # # # # # # # # # # # # #
    # Erro por ausência de carga de novas CATs
    # # # # # # # # # # # # # # # # # # # # # #
    if cats.empty:

        df_log_execucoes = pd.read_csv(log_execucoes, dtype='object').fillna('')
        ultima_cat = df_log_execucoes[df_log_execucoes.ultima_cat_baixada == df_log_execucoes.ultima_cat_baixada.max()].squeeze()

        sem_cat_msg = (
            'Não há novos registros no banco de dados das CATs.'
            f' A CAT {ultima_cat.ultima_cat_baixada}, de {ultima_cat.dt_ultima_cat_baixada}, é a mais recente no banco.')

        raise Exception(sem_cat_msg)

    # # # # # # # # # # #
    # Trata as CATs
    # # # # # # # # # # #
    cat_atribui_fatores_risco_partial = partial(acidentes.cat_atribui_fatores_risco,
                                                fatores_params_reshaped=fatores_params_reshaped)

    functions_list = [acidentes.cat_converter_inteiros,
                      acidentes.cat_converter_datas,
                      acidentes.cat_formatar_horas,
                      acidentes.cat_formatar_strings,
                      acidentes.cat_cid_uppercase,
                      acidentes.cat_novas_colunas,
                      acidentes.cat_uorg_local_acidente,
                      acidentes.cat_secao_cnae_local_acidente,
                      acidentes.cat_formatar_datas,
                      acidentes.cat_formatar_identificadores,
                      acidentes.cat_identifica_recibo_raiz,
                      acidentes.cat_mantem_recibo_ultima_reabertura,
                      cat_atribui_fatores_risco_partial,
                      acidentes.cat_compila_fatores_risco,
                      acidentes.cat_atribui_consequencia,
                      acidentes.cat_inserir_descricoes
                      ]

    cats_tratadas = reduce(lambda x, y: y(x), functions_list, cats)

    # # # # # # # # # # #
    # Notifica usuários
    # # # # # # # # # # #

    for index, destinatario in inscricoes_compilado_novos_codigos.iterrows():

        # Filtra CATs para o usuário
        funcoes_filtra_cats = [acidentes_filtrar.uf,
                               acidentes_filtrar.uorg,
                               acidentes_filtrar.tpacid,
                               acidentes_filtrar.consequencias,
                               acidentes_filtrar.risco,
                               acidentes_filtrar.cnae, ]

        funcoes_filtra_cats_partial = [partial(function, usuario=destinatario) for function in funcoes_filtra_cats]

        cats_filtradas = reduce(lambda x, y: y(x), funcoes_filtra_cats_partial, cats_tratadas)

        if not cats_filtradas.empty:
            # Gera PDF das CAT
            for index_cat, cat in cats_filtradas.iterrows():
                acidentes.cat_to_pdf(cat,
                                     html_template=cat_html_template,
                                     logo=logo_sit,
                                     output_dir=output_dir_cat_pdf)

            # Envia alerta por email
            anexos = [output_dir_cat_pdf / f'{cat.meta_nr_recibo}.pdf' for cat in cats_filtradas.itertuples()]
            cats_resumo_html = acidentes.cat_tabela_resumo(cats_filtradas).to_html(index=False, escape=False)
            campos_email = {'cats': cats_resumo_html,
                            'uf': destinatario.fillna('-')['UF'],
                            'uorg': destinatario.fillna('-')['UORG'],
                            'tpacid': destinatario.fillna('-')['Tipo de acidente'],
                            'consequencia': destinatario.fillna('-')['Consequência do acidente'],
                            'setores': destinatario.fillna('-')['Seção CNAE'],
                            'riscos': destinatario.fillna('-')['Fatores de risco']}
            msg_usuario = email_sender.EmailMessageHTML(destinatario=destinatario['E-mail'],
                                                        sender_email=cfg['SENDER_EMAIL'],
                                                        assunto='Alerta de acidente do trabalho',
                                                        template_html=alerta_user_html_template,
                                                        template_campos=campos_email,
                                                        anexos=anexos,
                                                        imagens=logo_saat)

            try:
                msg_usuario.send(auth_user=secrets['EMAIL'],
                                 password=secrets['PASSWORD'],
                                 smtp_server=cfg['SMPT_SERVER'],
                                 port=cfg['PORT'])

                # Registra no log o sucesso
                for index_cat, cat in cats_filtradas.iterrows():
                    log_dict = {'timestamp': datetime_str,
                                'email': destinatario['E-mail'],
                                'meta_nr_recibo': cat['meta_nr_recibo'],
                                'dtacid': cat['dtacid'],
                                'DTEmissaoCAT': cat['DTEmissaoCAT'],
                                'status': 'Sucesso'}
                    backup.backup_csv_append(log_alertas_usuario, log_dict)
            except:
                # Registra no log a falha
                for index_cat, cat in cats_filtradas.iterrows():
                    log_dict = {'timestamp': datetime_str,
                                'email': destinatario['E-mail'],
                                'meta_nr_recibo': cat['meta_nr_recibo'],
                                'dtacid': cat['dtacid'],
                                'DTEmissaoCAT': cat['DTEmissaoCAT'],
                                'status': 'Falhou'}

                    backup.backup_csv_append(log_alertas_usuario, log_dict)

    # # # # # # # # # # # # # # # # # # # # # # # # #
    # Notifica administradores / coordenador nacional
    # # # # # # # # # # # # # # # # # # # # # # # # #

    # Filtra CATs para os administradores / coordenadores
    perfil_admin = pd.Series({'Consequência do acidente': 'Óbito',
                              'Tipo de acidente': 'Acidentes típicos, Doenças do Trabalho'})

    funcoes_filtra_cats_adm = [acidentes_filtrar.tpacid,
                               acidentes_filtrar.consequencias]

    funcoes_filtra_cats_partial_adm = [partial(function, usuario=perfil_admin) for function in funcoes_filtra_cats_adm]

    cats_filtradas_adm = reduce(lambda x, y: y(x), funcoes_filtra_cats_partial_adm, cats_tratadas)

    if not cats_filtradas_adm.empty:
        # Gera PDF das CAT
        for index_cat, cat in cats_filtradas_adm.iterrows():
            acidentes.cat_to_pdf(cat,
                                 html_template=cat_html_template,
                                 logo=logo_sit,
                                 output_dir=output_dir_cat_pdf)

        # Envia alerta por email
        anexos = [output_dir_cat_pdf / f'{cat.meta_nr_recibo}.pdf' for cat in cats_filtradas_adm.itertuples()]

        cats_resumo_html = acidentes.cat_tabela_resumo(cats_filtradas_adm).to_html(index=False, escape=False)

        resumo_inscricoes = (inscricoes_compilado_novos_codigos[['UF', 'E-mail', 'UORG']]
                             .fillna('Todas')
                             .sort_values(['UF', 'UORG', 'E-mail', ]))

        envios = pd.read_csv(log_alertas_usuario)
        envios.timestamp = pd.to_datetime(envios.timestamp)
        envios_hj = envios[envios.timestamp.dt.date == datetime.now().date()]
        envios_hj_count = envios_hj.groupby('email').size().rename(f"Alertas enviados <br>em {dt_hoje_str}")

        resumo_alertas_hj = resumo_inscricoes.merge(envios_hj_count, how='left', left_on='E-mail', right_on='email')
        resumo_alertas_hj_html = resumo_alertas_hj.to_html(index=False, escape=False)

        alerta_adm_html_template = Path('../data/input/html_templates/alerta_adm.html')
        campos_email_adm = {'cats': cats_resumo_html,
                            'resumo_notificacoes': resumo_alertas_hj_html}

        for adm_email in admins_coord:
            msg_adm = email_sender.EmailMessageHTML(destinatario=adm_email,
                                                    sender_email=cfg['SENDER_EMAIL'],
                                                    assunto=f'Alerta de acidente do trabalho ({dt_hoje_str}) - Coordenador',
                                                    template_html=alerta_adm_html_template,
                                                    template_campos=campos_email_adm,
                                                    anexos=anexos,
                                                    imagens=logo_saat)

            try:
                msg_adm.send(auth_user=secrets['EMAIL'],
                             password=secrets['PASSWORD'],
                             smtp_server=cfg['SMPT_SERVER'],
                             port=cfg['PORT'])

                # Registra no log o sucesso
                for index_cat, cat in cats_filtradas_adm.iterrows():
                    log_dict = {'timestamp': datetime_str,
                                'email': adm_email,
                                'meta_nr_recibo': cat['meta_nr_recibo'],
                                'dtacid': cat['dtacid'],
                                'DTEmissaoCAT': cat['DTEmissaoCAT'],
                                'status': 'Sucesso'}

                    backup.backup_csv_append(log_alertas_adm, log_dict)

            except:
                # Registra no log a falha
                for index_cat, cat in cats_filtradas_adm.iterrows():
                    log_dict = {'timestamp': datetime_str,
                                'email': adm_email,
                                'meta_nr_recibo': cat['meta_nr_recibo'],
                                'dtacid': cat['dtacid'],
                                'DTEmissaoCAT': cat['DTEmissaoCAT'],
                                'status': 'Falhou'}

                    backup.backup_csv_append(log_alertas_adm, log_dict)

    # # # # # # # # # # # # # # # # # # # # # # # # #
    # Registra no log o resultado da execução
    # # # # # # # # # # # # # # # # # # # # # # # # #

    envios = pd.read_csv(log_alertas_usuario)
    envios.timestamp = pd.to_datetime(envios.timestamp)
    envios_hj = envios[envios.timestamp.dt.date == datetime.now().date()]

    ultima_cat = cats_tratadas[cats_tratadas.meta_nr_recibo == cats_tratadas.meta_nr_recibo.max()]

    log_dict = {'timestamp': datetime_str,
                'ultima_cat_baixada': ultima_cat.squeeze().meta_nr_recibo,
                'dt_ultima_cat_baixada': ultima_cat.squeeze().DTEmissaoCAT,
                'alertas_enviados': len(envios_hj),
                'status': 'Sucesso'
                }

    backup.backup_csv_append(log_execucoes, log_dict)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Registra no log e notifica o administrador, em caso de erro
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

except Exception as error:
    log_dict = {'timestamp': datetime_str,
                'ultima_cat_baixada': '',
                'dt_ultima_cat_baixada': '',
                'alertas_enviados': '',
                'status': 'Falhou'
                }

    backup.backup_csv_append(log_execucoes, log_dict)

    for adm_email in cfg['admin']:
        msg_txt = email_sender.EmailMessagText(destinatario=adm_email,
                                               sender_email=cfg['SENDER_EMAIL'],
                                               assunto='SAAT - Erro na execução do script',
                                               conteudo=f'{datetime_str} - Houve o seguinte erro na execução do script: {error}')

        msg_txt.send(auth_user=secrets['EMAIL'],
                     password=secrets['PASSWORD'],
                     smtp_server=cfg['SMPT_SERVER'],
                     port=cfg['PORT'])
