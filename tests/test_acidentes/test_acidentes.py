from functools import partial, reduce
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from pathlib import Path
from utils import read_yaml
import acidentes


def test_fator_risco():
    """Testa atribuição dos fatores de risco e compilação em lista única"""

    # Importa parâmetros para aplicação da função
    root_dir = Path().resolve()
    fatores_params = read_yaml(root_dir / 'config/fatores_risco_classificacao.yaml')
    fatores_params_reshaped = acidentes.reshape_fatores_params(fatores_params)

    # Cria função partial, informando o dicionário de parâmetros
    cat_atribui_fatores_risco_partial = partial(acidentes.cat_atribui_fatores_risco,
                                                fatores_params_reshaped=fatores_params_reshaped)

    function_list = [cat_atribui_fatores_risco_partial, acidentes.cat_compila_fatores_risco]

    cats = pd.DataFrame([{'codsitgeradora': '200044300',  # Diferentes fatores de risco, sem nulos
                          'codagntcausador': '303060000',
                          'dsclesao': '702045000',
                          'codcid': 'J700',
                          'codcidCategoria': 'T70', },

                         {'codsitgeradora': '200044300',  # Diferentes fatores de risco, com nulos
                          'codagntcausador': '303060000',
                          'dsclesao': '702045000',
                          'codcid': 'J700',
                          'codcidCategoria': 'T99', },

                         {'codsitgeradora': '',  # Categoria de CID, com exceções
                          'codagntcausador': '',
                          'dsclesao': '',
                          'codcid': 'L504',
                          'codcidCategoria': 'L50', }]
                        )

    esperado = pd.DataFrame([{'codsitgeradora': '200044300',
                              'codagntcausador': '303060000',
                              'dsclesao': '702045000',
                              'codcid': 'J700',
                              'codcidCategoria': 'T70',
                              'codsitgeradora_fr': '111',
                              'codagntcausador_fr': '121',
                              'dsclesao_fr': '131',
                              'codcid_fr': '132',
                              'codcidCategoria_fr': '141',
                              'CDFatorAmbiental': ['111', '121', '131', '132', '141']},

                             {'codsitgeradora': '200044300',
                              'codagntcausador': '303060000',
                              'dsclesao': '702045000',
                              'codcid': 'J700',
                              'codcidCategoria': 'T99',
                              'codsitgeradora_fr': '111',
                              'codagntcausador_fr': '121',
                              'dsclesao_fr': '131',
                              'codcid_fr': '132',
                              'codcidCategoria_fr': np.NAN,
                              'CDFatorAmbiental': ['111', '121', '131', '132']},

                             {'codsitgeradora': '',
                              'codagntcausador': '',
                              'dsclesao': '',
                              'codcid': 'L504',
                              'codcidCategoria': 'L50',
                              'codsitgeradora_fr': np.NAN,
                              'codagntcausador_fr': np.NAN,
                              'dsclesao_fr': np.NAN,
                              'codcid_fr': '161',
                              'codcidCategoria_fr': np.NAN,
                              'CDFatorAmbiental': ['161']}
                             ])

    resultado = reduce(lambda x, y: y(x), function_list, cats)

    assert_frame_equal(esperado, resultado, check_dtype=False)


class TestReciboRaiz:
    def test_identifica_raiz(self):
        """Testa identificação do recibo raiz para cada CAT"""

        cats = pd.DataFrame(
            [{'meta_nr_recibo': 'a001', 'nrRecCatOrig': None},  # sem recibo anterior

             {'meta_nr_recibo': 'b001', 'nrRecCatOrig': None},  # dois recibos apontando para o mesmo recibo anterior
             {'meta_nr_recibo': 'b002', 'nrRecCatOrig': 'b001'},
             {'meta_nr_recibo': 'b003', 'nrRecCatOrig': 'b001'},

             {'meta_nr_recibo': 'c001', 'nrRecCatOrig': None},  # recibos anteriores em cascata
             {'meta_nr_recibo': 'c002', 'nrRecCatOrig': 'c001'},
             {'meta_nr_recibo': 'c003', 'nrRecCatOrig': 'c002'},

             {'meta_nr_recibo': 'd002', 'nrRecCatOrig': 'd001'},  # recibo anterior inexistente no banco de dados

             {'meta_nr_recibo': 'e001', 'nrRecCatOrig': 'e001'},  # recibo anterior igual ao número do recibo
             ])

        esperado = pd.DataFrame([{'meta_nr_recibo': 'a001', 'nrRecCatOrig': None, 'recibo_raiz': 'a001'},

                                 {'meta_nr_recibo': 'b001', 'nrRecCatOrig': None, 'recibo_raiz': 'b001'},
                                 {'meta_nr_recibo': 'b002', 'nrRecCatOrig': 'b001', 'recibo_raiz': 'b001'},
                                 {'meta_nr_recibo': 'b003', 'nrRecCatOrig': 'b001', 'recibo_raiz': 'b001'},

                                 {'meta_nr_recibo': 'c001', 'nrRecCatOrig': None, 'recibo_raiz': 'c001'},
                                 {'meta_nr_recibo': 'c002', 'nrRecCatOrig': 'c001', 'recibo_raiz': 'c001'},
                                 {'meta_nr_recibo': 'c003', 'nrRecCatOrig': 'c002', 'recibo_raiz': 'c001'},

                                 {'meta_nr_recibo': 'd002', 'nrRecCatOrig': 'd001', 'recibo_raiz': 'd001'},

                                 {'meta_nr_recibo': 'e001', 'nrRecCatOrig': 'e001', 'recibo_raiz': 'e001'},
                                 ])

        resultado = acidentes.cat_identifica_recibo_raiz(cats)
        assert_frame_equal(esperado, resultado, check_dtype=False)

    def test_mantem_ultimo_recibo(self):
        """Testa eliminação dos registros antigos em caso de CATs de reabertura e comunicação de óbito"""

        cats = pd.DataFrame(
            [{'meta_nr_recibo': 'a001', 'nrRecCatOrig': None},  # sem recibo anterior

             {'meta_nr_recibo': 'b001', 'nrRecCatOrig': None},  # dois recibos apontando para o mesmo recibo anterior
             {'meta_nr_recibo': 'b002', 'nrRecCatOrig': 'b001'},
             {'meta_nr_recibo': 'b003', 'nrRecCatOrig': 'b001'},

             {'meta_nr_recibo': 'c001', 'nrRecCatOrig': None},  # recibos anteriores em cascata
             {'meta_nr_recibo': 'c002', 'nrRecCatOrig': 'c001'},
             {'meta_nr_recibo': 'c003', 'nrRecCatOrig': 'c002'},

             {'meta_nr_recibo': 'd002', 'nrRecCatOrig': 'd001'},  # recibo anterior inexistente no banco de dados

             {'meta_nr_recibo': 'e001', 'nrRecCatOrig': 'e001'},  # recibo anterior igual ao número do recibo
             ])

        esperado = pd.DataFrame([{'meta_nr_recibo': 'a001', 'nrRecCatOrig': None, 'recibo_raiz': 'a001'},
                                 {'meta_nr_recibo': 'b003', 'nrRecCatOrig': 'b001', 'recibo_raiz': 'b001'},
                                 {'meta_nr_recibo': 'c003', 'nrRecCatOrig': 'c002', 'recibo_raiz': 'c001'},
                                 {'meta_nr_recibo': 'd002', 'nrRecCatOrig': 'd001', 'recibo_raiz': 'd001'},
                                 {'meta_nr_recibo': 'e001', 'nrRecCatOrig': 'e001', 'recibo_raiz': 'e001'},
                                 ])

        function_list = [acidentes.cat_identifica_recibo_raiz, acidentes.cat_mantem_recibo_ultima_reabertura]
        resultado = reduce(lambda x, y: y(x), function_list, cats)

        assert_frame_equal(esperado, resultado, check_dtype=False)


def test_atribui_consequencia():
    cats = pd.DataFrame([{'indcatobito': 'S',
                          'indinternacao': 'N',
                          'dsclesao': '702035000',
                          'codparteating': '755070000',
                          'codcidCategoria': 'A00',
                          'codcid': 'A000',
                          'durtrat': 40},

                         {'indcatobito': 'N',
                          'indinternacao': 'S',
                          'dsclesao': '000000000',
                          'codparteating': '000000000',
                          'codcidCategoria': 'S68',
                          'codcid': 'S681',
                          'durtrat': 5},
                         ]
                        )

    esperado = pd.DataFrame([{'indcatobito': 'S',
                              'indinternacao': 'N',
                              'dsclesao': '702035000',
                              'codparteating': '755070000',
                              'codcidCategoria': 'A00',
                              'codcid': 'A000',
                              'durtrat': 40,
                              'Consequencia': ['Óbito', 'Fratura (dedo)',
                                               'Duração estimada do tratamento superior a 30 dias']},

                             {'indcatobito': 'N',
                              'indinternacao': 'S',
                              'dsclesao': '000000000',
                              'codparteating': '000000000',
                              'codcidCategoria': 'S68',
                              'codcid': 'S681',
                              'durtrat': 5,
                              'Consequencia': ['Internação do trabalhador', 'Amputação (dedo)']},
                             ]
                            )

    resultado = acidentes.cat_atribui_consequencia(cats)
    assert_frame_equal(esperado, resultado)
