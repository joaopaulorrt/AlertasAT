"""Módulo com funções para conexão à VPN do Ministério do Trabalho"""

from pywinauto_recorder.player import send_keys, click, UIPath
import time
import requests


def try_connection_forticlient_vpn(vpn_path: str, user: str, password: str, url_test_connection: str):
    """ Tenta connectar à VPN do Ministério do Trabalho.

    Args:
        vpn_path: Path apontando para o arquivo executável da VPN Forticlient.
            Formatação das barras no estilo do windows.
        user: Usuário para conexão à VPN
        password: Senha para conexão à VPN
        url_test_connection: URL utilizado para testar se a conexão à VPN foi bem sucedida.
    """
    max_attempts = 3
    attempts = 0

    while True:
        try:
            if _is_vpn_connected(url_test_connection):
                break
            else:
                _connect_forticlient_vpn(vpn_path, user, password)
                assert _is_vpn_connected(url_test_connection)
                break
        except AssertionError:
            attempts += 1
            print("Falha ao tentar conectar à VPN")
            if attempts >= max_attempts:
                class MyException(Exception):
                    pass
                raise MyException("Excedido o número máximo de tentativas de conectar à VPN")


def _connect_forticlient_vpn(vpn_path: str, user: str, password: str):
    """Faz tentativa única de conexão à VPN.

    Args:
        vpn_path: Path apontando para o arquivo executável da VPN Forticlient.
            Formatação das barras no estilo do windows.
        user: Usuário para conexão à VPN
        password: Senha para conexão à VPN
    """
    send_keys("{VK_LWIN down}r""{VK_LWIN up}")
    with UIPath(u"Run||Window"):
        send_keys("{VK_CONTROL down}a""{VK_CONTROL up}""{DELETE}")
        send_keys('"' + vpn_path + '"', pause=0)
        send_keys(u"{ENTER}")

    time.sleep(3)

    with UIPath(u"FortiClient||Pane"):
        click(u"FortiClient -- Zero Trust Fabric Agent||Document", duration=-1)
        send_keys(u"{ENTER}", pause=0)
        click(u"FortiClient -- Zero Trust Fabric Agent||Document", duration=-1)
        send_keys(u"{TAB}{TAB}", pause=0)
        send_keys(user, pause=0)
        send_keys(u"{TAB}", pause=0)
        send_keys(password, pause=0)
        send_keys(u"{TAB}{TAB}{ENTER}", pause=0)
        time.sleep(45)


def _is_vpn_connected(url_test_connection: str) -> bool:
    """Testa se a VPN do Ministério do Trabalho está conectada.

    Args:
        url_test_connection: URL utilizado para testar se a VPN do Ministério do Trabalho está conectada.

    Returns:
        Boolean indicando se a VPN do Ministério do Trabalho está conectada.

    """
    try:
        x = requests.get(url_test_connection)
        if x.status_code == 200:
            return True
        else:
            return False

    except requests.exceptions.RequestException:
        return False
