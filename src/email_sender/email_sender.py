"""Módulo com funções para enviar alertas por e-mail para os usuários do sistema"""

import os
from pathlib import Path
from os.path import basename
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from time import sleep

from jinja2 import Template


class EmailMessage:
    def __init__(self):
        self.sender_email = None
        self.destinatario = None
        self.message = None

    def send(self,
             auth_user: str,
             password: str,
             smtp_server: str,
             port: int):

        context = ssl.create_default_context()
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(auth_user, password)
        server.sendmail(self.sender_email, self.destinatario, self.message.as_string())
        server.quit()
        sleep(1)


class EmailMessageHTML(EmailMessage):
    def __init__(self,
                 destinatario: str,
                 sender_email: str,
                 assunto: str,
                 template_html: Path,
                 template_campos: dict,
                 anexos: Path | list[Path] | None,
                 imagens: Path | list[Path] | None):

        self.destinatario = destinatario
        self.sender_email = sender_email

        # Create a multipart message
        message = MIMEMultipart()
        message["Subject"] = assunto
        message["From"] = sender_email
        message["To"] = destinatario

        # Corpo em html
        with open(template_html, 'r', encoding='utf-8') as f:
            html_template = Template(f.read())

        html_string = html_template.render(template_campos)
        message.attach(MIMEText(html_string, "html"))

        # Imagens
        if imagens:
            imagens_list = [imagens] if type(imagens) != list else imagens
            for imagem_path in imagens_list:
                if os.path.isfile(imagem_path):
                    with open(imagem_path, "rb") as img:
                        imagem = MIMEApplication(img.read())
                    imagem.add_header('Content-ID', f'<{imagem_path.name}>')
                    message.attach(imagem)

        # Anexos
        if anexos:
            anexos_list = [anexos] if type(anexos) != list else anexos
            for anexo_path in anexos_list:
                if os.path.isfile(anexo_path):
                    with open(anexo_path, "rb") as attachment:
                        anexo = MIMEApplication(attachment.read(), Name=basename(anexo_path))

                    anexo['Content-Disposition'] = f'attachment; filename="{basename(anexo_path)}"'
                    message.attach(anexo)

        self.message = message


class EmailMessagText(EmailMessage):
    def __init__(self,
                 destinatario: str,
                 sender_email: str,
                 assunto: str,
                 conteudo: str):
        self.destinatario = destinatario
        self.sender_email = sender_email

        # Create a multipart message
        message = MIMEMultipart()
        message["Subject"] = assunto
        message["From"] = sender_email
        message["To"] = destinatario
        message.attach(MIMEText(conteudo, "plain"))

        self.message = message
