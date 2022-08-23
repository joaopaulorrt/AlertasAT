"""Módulo principal do sistema"""


if __name__ == '__main__':
    import os
    from functools import reduce, partial
    from utils import read_yaml
    from pathlib import Path
    import usuarios
    import backup
    import vpn_connection as vpn
    import usuarios
    import acidentes
    import acidentes_filtrar

    root_dir = Path().resolve().parent

    # Importa configurações do sistema
    cfg = read_yaml(root_dir / 'config/config.yaml')
    secrets = read_yaml(root_dir / 'config/secrets.yaml')
    codigos_desativados = read_yaml(root_dir / 'config/codigos_desativados_conversao.yaml')
    fatores_params = read_yaml(root_dir / 'config/fatores_risco_classificacao.yaml')
    fatores_params_reshaped = acidentes.reshape_fatores_params(fatores_params)

    # Indica diretórios e arquivos a serem utilizados
    cat_html_template = Path('../data/input/html_templates/cat.html')
    logo_sit = Path('../data/input/images/logoSIT.png')
    output_dir_cat_pdf = Path('../data/output/cat_pdf')

    # Importa dados que populam as opções do formulário de inscrição
    opcoes = usuarios.import_google_spreadsheet(cfg['FORM_INSC_OPCOES']['ID_GSHEET'])

    # Importa listas de inscrições e cancelamentos e compila lista de usuários ativos
    inscricoes = usuarios.import_google_spreadsheet(cfg['FORM_INSC']['ID_GSHEET'])
    cancelamentos = usuarios.import_google_spreadsheet(cfg['FORM_CANCEL']['ID_GSHEET'])
    inscricoes_compilado = usuarios.compila_inscricoes(df_inscricao=inscricoes, df_cancelamento=cancelamentos)
    inscricoes_compilado_novos_codigos = usuarios.update_codigos_desativados(inscricoes_compilado, codigos_desativados)

    # Realiza backup dos dados provenientes dos formulários de inscrição e cancelamento
    backup_dir = str(root_dir / 'data/backup')

    backup.backup_csv_new_file(opcoes, directory=backup_dir, filename='opcoes_form_insc.csv')
    backup.backup_csv(inscricoes, backup_path=os.path.join(backup_dir, 'inscricoes.csv'))
    backup.backup_csv(cancelamentos, backup_path=os.path.join(backup_dir, 'cancelamentos.csv'))
    backup.backup_csv(inscricoes_compilado_novos_codigos, backup_path=os.path.join(backup_dir, 'inscricoes_compilado.csv'))

    # Tenta conectar à VPN
    vpn.try_connection_forticlient_vpn(vpn_path=cfg['VNP_PATH'],
                                       user=secrets['VNP_USER'],
                                       password=secrets['VNP_PASSWORD'],
                                       url_test_connection=cfg['VPN_URL_TEST_CONNECTION'])

    # Importa novas CATs
    cats = acidentes.cat_extrair()

    # TODO raise error se não houver novos registros

    # Trata CATs
    cat_atribui_fatores_risco_partial = partial(acidentes.cat_atribui_fatores_risco,
                                                fatores_params_reshaped=fatores_params_reshaped)

    functions_list = [acidentes.cat_eliminar_ja_alertadas,
                      acidentes.cat_converter_inteiros,
                      acidentes.cat_converter_datas,
                      acidentes.cat_formatar_horas,
                      acidentes.cat_formatar_strings,
                      acidentes.cat_cid_uppercase,
                      acidentes.cat_novas_colunas,
                      acidentes.cat_uorg_local_acidente,
                      acidentes.cat_secao_cnae_local_acidente,
                      acidentes.cat_formatar_datas,
                      acidentes.cat_identifica_recibo_raiz,
                      acidentes.cat_mantem_recibo_ultima_reabertura,
                      cat_atribui_fatores_risco_partial,
                      acidentes.cat_compila_fatores_risco,
                      acidentes.cat_atribui_consequencia,
                      acidentes.cat_inserir_descricoes
                      ]

    cats_tratadas = reduce(lambda x, y: y(x), functions_list, cats)

    # TODO loop nos usuarios
    destinatario = inscricoes_compilado_novos_codigos.iloc[1]

    # Filtra CATs para o usuário
    funcoes_filtra_cats = [acidentes_filtrar.uf,
                           acidentes_filtrar.uorg,
                           acidentes_filtrar.tpacid,
                           acidentes_filtrar.consequencias,
                           acidentes_filtrar.risco,
                           acidentes_filtrar.cnae, ]

    funcoes_filtra_cats_partial = [partial(function, usuario=destinatario) for function in funcoes_filtra_cats]

    cats_filtradas = reduce(lambda x, y: y(x), funcoes_filtra_cats_partial, cats_tratadas)

    # Gera PDF das CAT
    for cat in cats_filtradas.index:
        acidentes.cat_to_pdf(cats_filtradas.loc[cat],
                             html_template=cat_html_template,
                             logo=logo_sit,
                             output_dir=output_dir_cat_pdf)

        # Encaminha email
        # Registra no log (Timestamp / email / Recibo / data emissão / data acidente)

    # Notifica administradores / coordenador nacional
        # Quantidade de novos acidentes, por consequencia
        # Tabela resumo das CAT fatais, para o corpo do e-mail
        # Tabela resumo dos usuários inscritos

    # Registra no log
        # Timestamp / sucesso / Última CAT baixada (se sucesso) / Quantidade de novos acidentes notificados

    # TODO capturar erro em caso de falha na execução do script e notificar o administrador