import smtplib  # Библиотека для отправки писем
import mimetypes  # Библиотека для обработки неизвестных mime типов
from email.mime.multipart import MIMEMultipart  # Позволяет создать письмо из разных частей
from email import encoders
import os

from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage


def send_email(email, subject, text, attachments=None):
    addr_form = os.getenv('FROM')
    password = os.getenv('PASSWORD')

    # Добавляем текст в письмо
    msg = MIMEMultipart()
    msg['FROM'] = addr_form
    msg['To'] = email
    msg['Subject'] = subject

    # Добавляем текст в письмо
    body = text
    msg.attach(MIMEText(body, 'plain'))  # plain тип текст

    if attachments is not None:
        process_attachments(msg, attachments)
    # Отправляем письмо на сервер
    server = smtplib.SMTP_SSL(os.getenv('HOST'), os.getenv('PORT'))
    server.login(addr_form, password)
    server.send_message(msg)
    server.quit()
    return True


def process_attachments(msg, attachments):  # Ищем файл
    for f in attachments:
        if os.path.isfile(f):  # Если это файл, то обращаемся к функции
            attach_file(msg, f)
        elif os.path.exists(f):  # Если это не файл, но путь существет, то это директория, где есть этот файл
            dir = os.listdir(f)
            for file in dir:
                attach_file(msg, f+'/' + file)


def attach_file(msg, f):
    attach_types = {
        'text': MIMEText,
        'image': MIMEImage,
        'audio': MIMEAudio
    }
    filename = os.path.basename(f)
    ctype, encoding = mimetypes.guess_type(f)  # С mimetypes определяем что за файл
    if ctype is None or encoding is not None:  # Когда файл не определился
        ctype = 'application/octet-stream'

    maintype, subtype = ctype.split('/', 1)
    with open(f, mode='rb' if maintype != 'text' else 'r') as fp:
        if maintype in attach_types:  # Если есть такие типы файла, то
            file = attach_types[maintype](fp.read(), _subtype=subtype)  # Получаем нужный тип для его обработки
        else:  # Если у нас неизвестный тип
            file = MIMEBase(maintype, subtype)
            file.set_payload(fp.read())
            encoders.encode_base64(file)  # Кодируем в base64
    file.add_header('Content-Disposition', 'attachment', filename=filename)

    msg.attach(file)  # Прикладываем к нашему сообщению нужный файл
