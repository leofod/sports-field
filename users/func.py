import random, smtplib, os
from .models import User, Registration, Admin
from fields.models import Meeting
from fields.func import get_week
from configparser import ConfigParser

# Отпрака письма.
def send_email(receiver, verification_code):
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_path, "mail.ini")        

    if os.path.exists(config_path):
        config = ConfigParser()
        config.read(config_path)
    else:
        return False
    
    charset = f'Content-Type: text/plain; charset=utf-8'
    mime = 'MIME-Version: 1.0'
    subject = 'Проверочный код'
    text = f"Проверочный код: {verification_code}"
    
    body = "\r\n".join((f"From: {config.get('smtp', 'user')}", f"To: {receiver}", 
            f"Subject: {subject}", mime, charset, "", text))

    try:
        smtp = smtplib.SMTP(config.get("smtp", "server"), config.get("smtp", "port"))
        smtp.starttls()
        smtp.ehlo()
        smtp.login(config.get("smtp", "user"), config.get("smtp", "passwd"))
        smtp.sendmail(config.get("smtp", "user"), receiver, body.encode('utf-8'))
    except smtplib.SMTPException as err:
        raise err
    finally:
        smtp.quit()
    return True

# Получить запись пользователя по логину/айди.
def get_user(val, flag):
    if(flag):
        try:
            return User.objects.get(username = val)
        except User.DoesNotExist:
            return False
    else:
        try:
            return User.objects.get(pk = val)
        except User.DoesNotExist:
            return False

# Возвращает списко площадок, на которых пользователь u будет на этой неделе.
def get_meetings(u):
    w = get_week(False)
    # Выбирать только нужные поля.
    m = Meeting.objects.filter(user = u).filter(date_meet__in = w).order_by('date_meet')
    if m.count():
        return m
    else:
        return False    

# Возвращает дни, в которые пользователь будет на площадках. 
def get_date_in(m):
    if m:
        c = set()
        for i in m:
            c.add(i.date_meet)
        return sorted(list(c))
    return False


# Возаращает проверочный код из 8-ми символов.
def get_verification_code():
    chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', '-', '+',\
            'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', '?', '@',\
            'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '!', '.', '_']
    return ''.join(random.choices(chars, k=8))

# Генерация имени картинки.
def get_image_name(name):
    chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',\
            'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',\
            'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    return ''.join(random.choices(chars, k=12)) + name[name.rindex('.'):]

# Получить email, указанный при регистрации.
def get_verification_email(id):
    try:
        return Registration.objects.get(pk=id).email
    except Registration.DoesNotExist:
        return False
    
# Проверка пользователя на админа.
def get_admin(uid):
    try:
        Admin.objects.get(user = User.objects.get(pk=uid))
        return True
    except Admin.DoesNotExist:
        return False