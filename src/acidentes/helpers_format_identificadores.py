""""Funções auxiliares para formatação de documentos"""


def format_cpf(cpf: str) -> str:
    cpf_formatado = (
            cpf[:3]
            + '.'
            + cpf[3:6]
            + '.'
            + cpf[6:9]
            + '-'
            + cpf[9:]
    )
    return cpf_formatado


def format_cnpj(cnpj: str) -> str:
    cnpj_formatado = (
            cnpj[:2]
            + '.'
            + cnpj[2:5]
            + '.'
            + cnpj[5:8]
            + '/'
            + cnpj[8:12]
            + '-'
            + cnpj[12:]
    )
    return cnpj_formatado


def format_cnpj_raiz(cnpj: str) -> str:
    cnpj_formatado = (
            cnpj[:2]
            + '.'
            + cnpj[2:5]
            + '.'
            + cnpj[5:8]
    )
    return cnpj_formatado


def format_cnae(cnae: str) -> str:
    cnae_formatado = (
            cnae[:4]
            + '-'
            + cnae[4:5]
            + '/'
            + cnae[5:]
    )
    return cnae_formatado


def format_cbo(cbo: str) -> str:
    cbo_formatado = (
            cbo[:4]
            + '-'
            + cbo[4:]
    )
    return cbo_formatado


def format_caepf(caepf: str) -> str:
    caepf_formatado = (
            caepf[:3]
            + '.'
            + caepf[3:6]
            + '.'
            + caepf[6:9]
            + '/'
            + caepf[9:12]
            + '-'
            + caepf[12:]
    )
    return caepf_formatado


def format_cno(cno: str) -> str:
    cno_formatado = (
            cno[:2]
            + '.'
            + cno[2:5]
            + '.'
            + cno[5:10]
            + '/'
            + cno[10:]
    )
    return cno_formatado


def format_nrinsc(tpinsc: str, nrinsc: str):
    match tpinsc:
        case 1:
            if len(nrinsc) == 8:
                return format_cnpj_raiz(nrinsc)
            else:
                return format_cnpj(nrinsc)
        case 2:
            return format_cpf(nrinsc)
        case 3:
            return format_caepf(nrinsc)
        case 4:
            return format_cno(nrinsc)
