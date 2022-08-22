""""Funções auxiliares para classificão dos acidentes por fator de risco"""

from functools import reduce


def reshape_fatores_params(fatores_params: dict) -> dict:
    """Reformata o dicionário de parâmetros, de modo que, para cada campo (ex.: 'codcid'), haja um único
    dicionário para todos os fatores de risco

    Args:
        fatores_params: Dicionário contendo um dicionário para cada fator de risco

    Returns:
        Dicionário contendo um dicionário para cada fator de risco (ex.: 'codcid')

    """
    list_campos = ['codsitgeradora', 'codagntcausador', 'dsclesao', 'codcid', 'codcidCategoria', 'codcid_not']
    fatores_params_reshaped = {}
    for campo in list_campos:
        fatores_params_reshaped[campo] = {}
        for fator in fatores_params:
            fatores_params_reshaped[campo][fator] = {}
            for element in fatores_params[fator][campo]:
                if '-' in element and campo in ['codcid', 'codcidCategoria', 'codcid_not']:
                    hifen_position = element.find('-')
                    cid_inicio = element[:hifen_position]
                    cid_fim = element[hifen_position+1:]
                    cid_lista = list_cid10(cid_inicio, cid_fim)
                    for cid in cid_lista:
                        fatores_params_reshaped[campo][fator][cid] = fator
                else:
                    fatores_params_reshaped[campo][fator][element] = fator
        fatores_params_reshaped[campo] = reduce(merge_dicts, fatores_params_reshaped[campo].values())
    fatores_params_reshaped['CDAgenteSituacao'] = merge_dicts(fatores_params_reshaped['codsitgeradora'],
                                                              fatores_params_reshaped['codagntcausador'])
    del fatores_params_reshaped['codsitgeradora']
    del fatores_params_reshaped['codagntcausador']

    return fatores_params_reshaped


def merge_dicts(d1, d2):
    """Merge two dictionaries after checking whether there are duplicate keys in them. When duplicate keys are found,
    the function raises an error"""
    duplicate_keys = d1.keys() & d2
    if len(duplicate_keys) == 0:
        return {**d1, **d2}
    else:
        raise AssertionError(f'The following keys were found in both dictionaries: {duplicate_keys}')


def list_cid10(cid_inicial: str, cid_final: str) -> list[str]:
    """Cria uma lista de CIDs a partir de uma CID inicial e uma CID Final.

    :param cid_inicial: CID inicial com três ou quatro dígitos.
    :param cid_final: CID final com três ou quatro dígitos.
    :return list_cid: Lista de CIDs
    """
    if len(cid_inicial) != len(cid_final):
        raise ValueError('cid_inicial e cid_final devem ter o mesmo número de dígitos')

    len_cid = len(cid_inicial)

    alfabeto = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    list_letras = alfabeto[alfabeto.find(cid_inicial[0]):alfabeto.find(cid_final[0]) + 1]
    list_cid = []

    if cid_inicial[0] == cid_final[0]:
        list_cid.extend([f'{cid_inicial[0]}{str(i).zfill(len_cid - 1)}' for i in range(int(cid_inicial[1:]), int(cid_final[1:]) + 1)])
    else:
        list_cid.extend([f'{list_letras[0]}{str(i).zfill(len_cid - 1)}' for i in range(int(cid_inicial[1:]), 10 ** (len_cid - 1))])
        for letra in list_letras[1:-1]:
            list_cid.extend([f'{letra}{str(i).zfill(len_cid - 1)}' for i in range(1, 10 ** (len_cid - 1))])
        list_cid.extend([f'{list_letras[-1]}{str(i).zfill(len_cid - 1)}' for i in range(1, int(cid_final[1:]) + 1)])

    return list_cid
