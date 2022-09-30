"""Módulo principal

Serviço de Alerta de Acidentes de Trabalho
Autor: João Paulo Reis Ribeiro Teixeira - joao.reis@economia.gov.br'
"""

from datetime import datetime
import pandas as pd
from pathlib import Path
import os

import backup
import acidentes
import email_sender


def alerta_usuario(usuario: pd.Series,
                   cats: pd.DataFrame,
                   cat_pdf_dir: Path,
                   template_html: Path,
                   cfg: dict,
                   secrets: dict,
                   logo: Path):
    """ Envia e-mail de alerta ao usuário

    Args:
        usuario: Pandas series com as preferências do usuário
        cats: Pandas DataFrame com as CATs que serão encaminhadas ao usuário
        cat_pdf_dir: Diretório com os arquivos das CATs em PDF
        template_html: Template html a ser utilizado para mesclagem do email
        cfg: Dicionário com as configurações para envio do email, contendo as chaves 'SENDER_EMAIL', 'SMPT_SERVER' e 'PORT'
        secrets: Dicionário com as credenciais para envio do e-mail, contendo as chaves 'EMAIL' e 'PASSWORD'
        logo: Path da imagem a ser inserida no cabeçalho do e-mail

    """
    anexos = [cat_pdf_dir / f'{cat.meta_nr_recibo}.pdf' for cat in cats.itertuples()]

    cats_resumo_html = acidentes.cat_tabela_resumo(cats).to_html(index=False, escape=False)

    campos_email = {'cats': cats_resumo_html,
                    'uf': usuario.fillna('-')['UF'],
                    'uorg': usuario.fillna('-')['UORG'],
                    'tpacid': usuario.fillna('-')['Tipo de acidente'],
                    'consequencia': usuario.fillna('-')['Consequência do acidente'],
                    'setores': usuario.fillna('-')['Seção CNAE'],
                    'riscos': usuario.fillna('-')['Fatores de risco']}
    msg_usuario = email_sender.EmailMessageHTML(destinatario=usuario['E-mail'],
                                                sender_email=cfg['SENDER_EMAIL'],
                                                assunto='Alerta de acidente do trabalho',
                                                template_html=template_html,
                                                template_campos=campos_email,
                                                anexos=anexos,
                                                imagens=logo)

    msg_usuario.send(auth_user=secrets['EMAIL'],
                     password=secrets['PASSWORD'],
                     smtp_server=cfg['SMPT_SERVER'],
                     port=cfg['PORT'])


def alerta_coordenador(coordenador: pd.Series,
                       cats: pd.DataFrame,
                       cats_coord: pd.DataFrame,
                       cat_pdf_dir: Path,
                       df_resumo_alertas_hj: pd.DataFrame,
                       template_html: Path,
                       cfg: dict,
                       secrets: dict,
                       logo: Path):
    """ Envia e-mail de alerta ao coordenador

    Args:
        coordenador: Pandas series com as preferências do coordenador
        cats: Pandas DataFrame com todas as CATs novas.
        cats_coord: Pandas DataFrame com as CATs que serão encaminhadas ao coordenador
        cat_pdf_dir: Diretório com os arquivos das CATs em PDF
        df_resumo_alertas_hj: Pandas DataFrame com o resumo dos alertas enviados na data corrente, por usuário
        template_html: Template html a ser utilizado para mesclagem do email
        cfg: Dicionário com as configurações para envio do email, contendo as chaves 'SENDER_EMAIL', 'SMPT_SERVER' e 'PORT'
        secrets: Dicionário com as credenciais para envio do e-mail, contendo as chaves 'EMAIL' e 'PASSWORD'
        logo: Path da imagem a ser inserida no cabeçalho do e-mail

    """
    if not cats_coord.empty:
        anexos_adm = [cat_pdf_dir / f'{cat.meta_nr_recibo}.pdf' for cat in cats_coord.itertuples()]
        cats_resumo_html_adm = acidentes.cat_tabela_resumo(cats_coord).to_html(index=False, escape=False)
    else:
        anexos_adm = None
        cats_resumo_html_adm = None

    resumo_alertas_hj_html = df_resumo_alertas_hj.to_html(index=False, escape=False)

    campos_email_adm = {'qtd_cats': cats.shape[0],
                        'cats': cats_resumo_html_adm if cats_resumo_html_adm else f'Sem novos registros',
                        'resumo_notificacoes': resumo_alertas_hj_html}

    msg_adm = email_sender.EmailMessageHTML(destinatario=coordenador['E-mail'],
                                            sender_email=cfg['SENDER_EMAIL'],
                                            assunto=f'Alerta de acidente do trabalho ({str(datetime.now().strftime("%d/%m/%Y"))}) - Coordenador',
                                            template_html=template_html,
                                            template_campos=campos_email_adm,
                                            anexos=anexos_adm if anexos_adm else None,
                                            imagens=logo)

    msg_adm.send(auth_user=secrets['EMAIL'],
                 password=secrets['PASSWORD'],
                 smtp_server=cfg['SMPT_SERVER'],
                 port=cfg['PORT'])


def resumo_alertas_hj(usuarios: pd.DataFrame, log_alertas_usuario: Path) -> pd.DataFrame:
    """Cria DataFrame com o resumo dos alertas enviados na data corrente, por usuário

    Args:
        usuarios: DataFrame com os dados dos usuários
        log_alertas_usuario: Path do arquivo .csv contendo o log de alertas enviados aos usuários

    Returns:
        DataFrame com o resumo dos alertas enviados na data corrente, por usuário
    """
    dt_hoje_str = str(datetime.now().strftime("%d/%m/%Y"))

    resumo_inscricoes = (usuarios[['UF', 'E-mail', 'UORG']]
                         .fillna('Todas')
                         .sort_values(['UF', 'UORG', 'E-mail', ]))

    if os.path.exists(log_alertas_usuario):
        envios = pd.read_csv(log_alertas_usuario)
        envios.timestamp = pd.to_datetime(envios.timestamp)
        envios_hj = envios[envios.timestamp.dt.date == datetime.now().date()]
        envios_hj_count = envios_hj.groupby('email').size().rename(f"Alertas enviados <br>em {dt_hoje_str}")
    else:
        envios_hj_count = pd.Series(name=f"Alertas enviados <br>em {dt_hoje_str}")
        envios_hj_count.index.name = 'email'

    df_resumo = (resumo_inscricoes
                 .merge(envios_hj_count, how='left', left_on='E-mail', right_on='email')
                 .fillna(0)
                 .convert_dtypes())

    return df_resumo


def log_alertas(log: Path, destinatario: pd.Series, cats: pd.DataFrame, sucesso: bool):
    """Adiciona ao log o resultado do envio das CATs presentes na DataFrame ao destinatário

    Args:
        log: Path do arquivo .csv contendo o log de alertas
        destinatario: Pandas series com as preferências do usuário
        cats: Pandas DataFrame com as cats que serão encaminhadas ao usuário
        sucesso: Indica se houve sucesso no envio

    """
    for _, cat in cats.iterrows():
        log_dict = {'timestamp': str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    'email': destinatario['E-mail'],
                    'meta_nr_recibo': cat['meta_nr_recibo'],
                    'dtacid': cat['dtacid'],
                    'DTEmissaoCAT': cat['DTEmissaoCAT'],
                    'status': 'Sucesso' if sucesso else 'Falhou'}
        backup.backup_csv_append(log, log_dict)


def log_execucao(log_execucoes, sucesso: bool, cats=None, log_alertas_usuario=None):
    """Adiciona ao log o resultado da execução do script

    Args:
        log_execucoes: Path do arquivo .csv contendo o log de execuções
        sucesso: Indica se houve sucesso na execução
        cats: Pandas DataFrame com as novas CATs baixadas
        log_alertas_usuario: Path do arquivo .csv contendo o log de alertas aos usuários

    """
    if sucesso:
        if os.path.exists(log_alertas_usuario):
            envios = pd.read_csv(log_alertas_usuario)
            envios.timestamp = pd.to_datetime(envios.timestamp)
            envios_hj = envios[envios.timestamp.dt.date == datetime.now().date()]
        else:
            envios_hj = pd.DataFrame()

        ultima_cat = cats[cats.meta_nr_recibo == cats.meta_nr_recibo.max()]

        log_dict = {'timestamp': str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    'qtd_cat_baixada': cats.shape[0],
                    'ultima_cat_baixada': ultima_cat.squeeze().meta_nr_recibo,
                    'dt_ultima_cat_baixada': ultima_cat.squeeze().DTEmissaoCAT,
                    'alertas_enviados_no_dia': len(envios_hj),
                    'status': 'Sucesso'
                    }
    else:
        log_dict = {'timestamp': str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    'qtd_cat_baixada': '',
                    'ultima_cat_baixada': '',
                    'dt_ultima_cat_baixada': '',
                    'alertas_enviados_no_dia': '',
                    'status': 'Falhou'
                    }

    backup.backup_csv_append(log_execucoes, log_dict)


if __name__ == '__main__':
    from pathlib import Path
    import pandas as pd
    from datetime import datetime

    import acidentes
    import usuarios
    import backup
    import acidentes_filtrar
    import email_sender
    from utils import read_yaml

    root_dir = Path().resolve().parent

    # Importa configurações do sistema
    cfg = read_yaml(root_dir / 'config/config.yaml')
    secrets = read_yaml(root_dir / 'config/secrets.yaml')
    codigos_desativados = read_yaml(root_dir / 'config/codigos_desativados_conversao.yaml')
    fatores_params = read_yaml(root_dir / 'config/fatores_risco_classificacao.yaml')
    fatores_params_reshaped = acidentes.reshape_fatores_params(fatores_params)

    # HTML Templates
    cat_html_template = Path('../data/input/html_templates/cat.html')
    alerta_user_html_template = Path('../data/input/html_templates/alerta_usuario.html')
    alerta_adm_html_template = Path('../data/input/html_templates/alerta_adm.html')

    # Tabelas auxiliares
    aux_tables_dir = Path('../data/input/aux_tables')

    # Imagens
    logo_sit = Path('../data/input/images/logoSIT.png')
    logo_saat = Path('../data/input/images/logoSAAT_email.png')

    # Cats em PDF
    cat_pdf_dir = Path('../data/output/cat_pdf')

    # LOGs
    log_dir = Path('../data/log')
    log_alertas_usuario = log_dir / 'log_alertas_usuarios.csv'
    log_alertas_adm = log_dir / 'log_alertas_adm.csv'
    log_execucoes = log_dir / 'log_execucoes.csv'

    # Backup
    backup_dir = root_dir / 'data/backup'
    backup_opcoes_form = backup_dir / 'opcoes_form_insc.csv'
    backup_usuarios = backup_dir / 'usuarios.csv'

    # Faz backup dos dados que populam as opções do formulário de inscrição
    opcoes = usuarios.import_google_spreadsheet(cfg['FORM_INSC_OPCOES']['ID_GSHEET'])
    backup.backup_csv_new_file(opcoes, backup_path=backup_opcoes_form)

    # Carrega as lista de usuários ativos e faz backup
    df_usuarios = usuarios.usuarios(id_gsheet_insc=cfg['FORM_INSC']['ID_GSHEET'],
                                    id_gsheet_canc=cfg['FORM_CANCEL']['ID_GSHEET'],
                                    codigos_desativados=codigos_desativados)
    backup.backup_csv(df_usuarios, backup_path=backup_usuarios)

    # Carrega lista de coordenadores
    df_coord = pd.DataFrame(cfg['COORDENADORES'])

    try:
        # Carrega CATs
        cats_tratadas = acidentes.cat_tratadas(vpn_path=cfg['VNP_PATH'],
                                               user=secrets['USER'],
                                               password=secrets['PASSWORD'],
                                               url_test_connection=cfg['VPN_URL_TEST_CONNECTION'],
                                               log_execucoes=log_execucoes,
                                               aux_tables_dir=aux_tables_dir,
                                               fatores_risco=fatores_params_reshaped)

        # Alerta usuários
        for _, destinatario in df_usuarios.iterrows():
            # Filtra CATs
            cats_filtradas = acidentes_filtrar.preferencias_usuario(cats_tratadas, destinatario, log_alertas_usuario)

            # Gera PDF das CAT
            if not cats_filtradas.empty:
                for index_cat, cat in cats_filtradas.iterrows():
                    acidentes.cat_to_pdf(cat,
                                         html_template=cat_html_template,
                                         logo=logo_sit,
                                         output_dir=cat_pdf_dir)

                # Notifica usuário e registra no log
                try:
                    alerta_usuario(usuario=destinatario,
                                   cats=cats_filtradas,
                                   cat_pdf_dir=cat_pdf_dir,
                                   template_html=alerta_user_html_template,
                                   cfg=cfg,
                                   secrets=secrets,
                                   logo=logo_saat)
                    log_alertas(log=log_alertas_usuario, destinatario=destinatario, cats=cats_filtradas, sucesso=True)

                except:
                    log_alertas(log=log_alertas_usuario, destinatario=destinatario, cats=cats_filtradas, sucesso=False)

        # Alerta coordenador
        for _, destinatario in df_coord.iterrows():
            # Filtra CATs
            cats_filtradas = acidentes_filtrar.preferencias_coordenador(cats_tratadas, destinatario, log_alertas_adm)

            # Gera PDF das CAT
            if not cats_filtradas.empty:
                for index_cat, cat in cats_filtradas.iterrows():
                    acidentes.cat_to_pdf(cat,
                                         html_template=cat_html_template,
                                         logo=logo_sit,
                                         output_dir=cat_pdf_dir)

            # Calcula número de alertas por usuário
            df_resumo_alertas_hj = resumo_alertas_hj(usuarios=df_usuarios, log_alertas_usuario=log_alertas_usuario)

            # Notifica coordenador e registra no log
            try:
                alerta_coordenador(coordenador=destinatario,
                                   cats=cats_tratadas,
                                   cats_coord=cats_filtradas,
                                   cat_pdf_dir=cat_pdf_dir,
                                   df_resumo_alertas_hj=df_resumo_alertas_hj,
                                   template_html=alerta_adm_html_template,
                                   cfg=cfg,
                                   secrets=secrets,
                                   logo=logo_saat)
                log_alertas(log=log_alertas_adm, destinatario=destinatario, cats=cats_filtradas, sucesso=True)
            except:
                log_alertas(log=log_alertas_adm, destinatario=destinatario, cats=cats_filtradas, sucesso=False)

        # Registra log da execução
        log_execucao(log_execucoes, sucesso=True, cats=cats_tratadas, log_alertas_usuario=log_alertas_usuario)

    except Exception as error:
        log_execucao(log_execucoes, sucesso=False)

        for adm_email in cfg['ADMIN']:
            msg_txt = email_sender.EmailMessagText(destinatario=adm_email,
                                                   sender_email=cfg['SENDER_EMAIL'],
                                                   assunto='SAAT - Erro na execução do script',
                                                   conteudo=(f'{str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}'
                                                             f' - Houve o seguinte erro na execução do script: {error}')
                                                   )

            msg_txt.send(auth_user=secrets['EMAIL'],
                         password=secrets['PASSWORD'],
                         smtp_server=cfg['SMPT_SERVER'],
                         port=cfg['PORT'])

        raise Exception('error')

    print('ok')
