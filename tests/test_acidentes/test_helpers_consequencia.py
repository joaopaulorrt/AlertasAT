import pandas as pd
import acidentes.helpers_consequencia as consequencia


class TestAmputacaoExcetoDedo:
    def test_amputacao_dsclesao(self):
        cat = pd.Series({'dsclesao': '702070000',
                         'codparteating': '755010400',
                         'codcidCategoria': 'A00',
                         'codcid': 'A000'})

        esperado = 'Amputação (exceto dedo)'
        resultado = consequencia.amputacao_exceto_dedo(cat)
        assert resultado == esperado

    def test_amputacao_cid(self):
        cat = pd.Series({'dsclesao': '000000000',
                         'codparteating': '000000000',
                         'codcidCategoria': 'S08',
                         'codcid': 'S081'})

        esperado = 'Amputação (exceto dedo)'
        resultado = consequencia.amputacao_exceto_dedo(cat)
        assert resultado == esperado

    def test_amputacao_dedo_dsclesao(self):
        cat = pd.Series({'dsclesao': '702070000',
                         'codparteating': '755070000',
                         'codcidCategoria': 'A00',
                         'codcid': 'A000'})

        esperado = None
        resultado = consequencia.amputacao_exceto_dedo(cat)
        assert resultado == esperado

    def test_amputacao_dedo_cid(self):
        cat = pd.Series({'dsclesao': '000000000',
                         'codparteating': '000000000',
                         'codcidCategoria': 'S68',
                         'codcid': 'S681'})

        esperado = None
        resultado = consequencia.amputacao_exceto_dedo(cat)
        assert resultado == esperado

    def test_amputacao_dedo_cid2(self):
        cat = pd.Series({'dsclesao': '000000000',
                         'codparteating': '755070000',
                         'codcidCategoria': 'S68',
                         'codcid': 'S68'})

        esperado = None
        resultado = consequencia.amputacao_exceto_dedo(cat)
        assert resultado == esperado


    def test_nao_amputacao(self):
        cat = pd.Series({'dsclesao': '000000000',
                         'codparteating': '000000000',
                         'codcidCategoria': 'A00',
                         'codcid': 'A000'})

        esperado = None
        resultado = consequencia.amputacao_exceto_dedo(cat)
        assert resultado == esperado


class TestAmputacaoDedo:
    def test_amputacao_dsclesao(self):
        cat = pd.Series({'dsclesao': '702070000',
                         'codparteating': '755010400',
                         'codcidCategoria': 'A00',
                         'codcid': 'A000'})

        esperado = None
        resultado = consequencia.amputacao_dedo(cat)
        assert resultado == esperado

    def test_amputacao_cid(self):
        cat = pd.Series({'dsclesao': '000000000',
                         'codparteating': '000000000',
                         'codcidCategoria': 'S08',
                         'codcid': 'S081'})

        esperado = None
        resultado = consequencia.amputacao_dedo(cat)
        assert resultado == esperado

    def test_amputacao_dedo_dsclesao(self):
        cat = pd.Series({'dsclesao': '702070000',
                         'codparteating': '755070000',
                         'codcidCategoria': 'A00',
                         'codcid': 'A000'})

        esperado = 'Amputação (dedo)'
        resultado = consequencia.amputacao_dedo(cat)
        assert resultado == esperado

    def test_amputacao_dedo_cid(self):
        cat = pd.Series({'dsclesao': '000000000',
                         'codparteating': '000000000',
                         'codcidCategoria': 'S68',
                         'codcid': 'S681'})

        esperado = 'Amputação (dedo)'
        resultado = consequencia.amputacao_dedo(cat)
        assert resultado == esperado

    def test_nao_amputacao(self):
        cat = pd.Series({'dsclesao': '000000000',
                         'codparteating': '000000000',
                         'codcidCategoria': 'A00',
                         'codcid': 'A000'})

        esperado = None
        resultado = consequencia.amputacao_dedo(cat)
        assert resultado == esperado


class TestFraturaExcetoDedo:
    def test_fratura_dsclesao(self):
        cat = pd.Series({'dsclesao': '702035000',
                         'codparteating': '755010400',
                         'codcidCategoria': 'A00',
                         'codcid': 'A000'})

        esperado = 'Fratura (exceto dedo)'
        resultado = consequencia.fratura_exceto_dedo(cat)
        assert resultado == esperado

    def test_fratura_cid(self):
        cat = pd.Series({'dsclesao': '000000000',
                         'codparteating': '000000000',
                         'codcidCategoria': 'S62',
                         'codcid': 'S624'})

        esperado = 'Fratura (exceto dedo)'
        resultado = consequencia.fratura_exceto_dedo(cat)
        assert resultado == esperado

    def test_fratura_dedo_dsclesao(self):
        cat = pd.Series({'dsclesao': '702035000',
                         'codparteating': '755070000',
                         'codcidCategoria': 'A00',
                         'codcid': 'A000'})

        esperado = None
        resultado = consequencia.fratura_exceto_dedo(cat)
        assert resultado == esperado

    def test_fratura_dedo_cid(self):
        cat = pd.Series({'dsclesao': '000000000',
                         'codparteating': '000000000',
                         'codcidCategoria': 'S62',
                         'codcid': 'S625'})

        esperado = None
        resultado = consequencia.fratura_exceto_dedo(cat)
        assert resultado == esperado

    def test_fratura_dedo_cid2(self):
        cat = pd.Series({'dsclesao': '000000000',
                         'codparteating': '755070000',
                         'codcidCategoria': 'S62',
                         'codcid': 'S62'})

        esperado = None
        resultado = consequencia.fratura_exceto_dedo(cat)
        assert resultado == esperado

    def test_nao_fratura(self):
        cat = pd.Series({'dsclesao': '000000000',
                         'codparteating': '000000000',
                         'codcidCategoria': 'A00',
                         'codcid': 'A000'})

        esperado = None
        resultado = consequencia.fratura_exceto_dedo(cat)
        assert resultado == esperado


class TestFraturaDedo:
    def test_fratura_dsclesao(self):
        cat = pd.Series({'dsclesao': '702035000',
                         'codparteating': '755010400',
                         'codcidCategoria': 'A00',
                         'codcid': 'A000'})

        esperado = None
        resultado = consequencia.fratura_dedo(cat)
        assert resultado == esperado

    def test_fratura_cid(self):
        cat = pd.Series({'dsclesao': '000000000',
                         'codparteating': '000000000',
                         'codcidCategoria': 'S62',
                         'codcid': 'S624'})

        esperado = None
        resultado = consequencia.fratura_dedo(cat)
        assert resultado == esperado

    def test_fratura_dedo_dsclesao(self):
        cat = pd.Series({'dsclesao': '702035000',
                         'codparteating': '755070000',
                         'codcidCategoria': 'A00',
                         'codcid': 'A000'})

        esperado = 'Fratura (dedo)'
        resultado = consequencia.fratura_dedo(cat)
        assert resultado == esperado

    def test_fratura_dedo_cid(self):
        cat = pd.Series({'dsclesao': '000000000',
                         'codparteating': '000000000',
                         'codcidCategoria': 'S62',
                         'codcid': 'S625'})

        esperado = 'Fratura (dedo)'
        resultado = consequencia.fratura_dedo(cat)
        assert resultado == esperado

    def test_nao_fratura(self):
        cat = pd.Series({'dsclesao': '000000000',
                         'codparteating': '000000000',
                         'codcidCategoria': 'A00',
                         'codcid': 'A000'})

        esperado = None
        resultado = consequencia.fratura_dedo(cat)
        assert resultado == esperado
