from django import forms
import re, logging
from .models import User, Registration
from django.forms import PasswordInput, Textarea
from django.utils import timezone
from .func import get_verification_code, send_email, get_image_name, get_hash
from datetime import datetime, timedelta
from hashlib import sha256

logger = logging.getLogger(__name__)

class LoginForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['email', 'password']
        labels = {
            'email': 'Почта',
            'password': 'Пароль',
        }
        widgets = {
            'password': PasswordInput(),
        }

    def checkLog(self):
        if not(re.match(r'^([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)$', self['email'].data)):
            return False, False
        # if len(self['password'].data) < 8:
            # return False, False
        try:
            u = User.objects.get(email = self['email'].data.lower())
            if(get_hash(self['email'].data, self['password'].data)  == u.password):
                return True, u.id
            else:
                return True, False 
        except User.DoesNotExist:
            return True, False 

class CheckRegForm(forms.ModelForm):

    class Meta:
        model = Registration
        fields = ['verification_code']
        labels = {
            'verification_code': 'Проверочный код:'
        }

    def check_verificaton(self, reg_id):
        if self['verification_code'].data:
            try:
                reg_info = Registration.objects.get(pk = reg_id)
                if reg_info.verification_code == self['verification_code'].data:
                    user = User(username = reg_info.username, name = reg_info.name, surname = reg_info.surname, \
                                email = reg_info.email, password = reg_info.password)
                    user.save()
                    reg_info.delete()
                    try:
                        return True, User.objects.get(username = reg_info.username).pk
                    except User.DoesNotExist:
                        logger.error('User doesn\'t exist: ' + reg_info.username)
                        return False, True
                return True, False
            except Registration.DoesNotExist:
                logger.error('Reg doesn\'t exist: ' + str(reg_id))
                return False, True
        return False, False
    
class DeleteAcc(forms.Form):
    check_del = forms.BooleanField()

    def delete_account_reg(self, reg_id):
        if self['check_del'].data:
            try:
                reg_acc = Registration.objects.get(pk = reg_id)
                logger.info('DR - ' + reg_acc.email)
                reg_acc.delete()
                return True
            except Registration.DoesNotExist:
                return True
        return False

class ResendVC(forms.Form):
    check = forms.BooleanField()

    def resend_verefecation_code(self, reg_id):
        if self['check'].data:
            try:
                reg_info = Registration.objects.get(pk = reg_id)
                curr_time = datetime.now(tz = timezone.get_current_timezone()) 
                diff_time = curr_time - reg_info.time_add
                if (diff_time > timedelta(minutes=5)):
                    reg_info.time_add = datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S%z')
                    reg_info.verification_code = get_verification_code()                    
                    reg_info.save()
                    if not send_email(reg_info.email, reg_info.verification_code, reg_info.name, False):
                        logger.error('Can\'t resend email to: ' + reg_info.email)
                    return True, True
            # acc.time_add = datetime.strftime(datetime.now(tz = timezone.get_current_timezone()), '%Y-%m-%d %H:%M:%S%z')
                return True, str(datetime.strftime(curr_time+timedelta(minutes=5)-diff_time, '%H:%M:%S'))
            except Registration.DoesNotExist:
                logger.error('Reg doesn\'t exist: ' + str(reg_id))
                return False, True
        return False, False
        
class RegForm(forms.ModelForm):
    password = forms.CharField(label = 'Введите пароль', widget = forms.PasswordInput)
    password_repeat = forms.CharField(label = 'Повторите пароль', widget = forms.PasswordInput)

    class Meta:
        model = Registration
        fields = ['username', 'name', 'surname', 'email']
        labels = {
            'username': 'Логин',
            'name': 'Имя',
            'surname': 'Фамилия',
            'email' : 'Почта'
        }

    def check_registration(self):
        if not(re.match(r'^(?=.*[a-zA-Z].*)[A-Za-z0-9][A-Za-z0-9_\.]{2,31}$', self['username'].data)):
            return False, 1
        else:
            try:
                User.objects.get(username = self['username'].data.lower())
                return False, 2
            except User.DoesNotExist:
                try:
                    Registration.objects.get(username = self['username'].data.lower())
                    return False, 2
                except Registration.DoesNotExist:
                    username = self['username'].data.lower()
        if not(re.match(r'^[a-zA-Zа-яА-ЯЁ][a-zа-яё]{1,31}$', self['name'].data)):
            return False, 3
        if not(re.match(r'^[a-zA-Zа-яА-ЯЁ][a-zA-Zа-яА-ЯЁ\s\-]{1,31}$', self['surname'].data)):
            return False, 4
        if re.match(r'^([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)$', self['email'].data):
            try:
                User.objects.get(email = self['email'].data.lower())
                return False, 5
            except User.DoesNotExist:
                try:
                    Registration.objects.get(email = self['email'].data.lower())
                    return False, 5
                except Registration.DoesNotExist:
                    email = self['email'].data.lower()
        else:
            return False, 5

        if not(re.match(r'^(?=.*[0-9].*)(?=.*[a-z].*)(?=.*[A-Z].*)[0-9a-zA-Z!\-_\.]{8,63}$', self['password'].data)):
            return False, 6
        if self['password'].data != self['password_repeat'].data:
            return False, 7
        acc = Registration(username = username, name = self['name'].data, surname = self['surname'].data, email = email, password = get_hash(email, self['password'].data))
        acc.verification_code = get_verification_code()
        acc.time_add = datetime.strftime(datetime.now(tz = timezone.get_current_timezone()), '%Y-%m-%d %H:%M:%S%z')
        try:                
            acc.save()
            if not send_email(acc.email, acc.verification_code, acc.name, True):
                logger.error('Can\'t send email to: ' + acc.email)
        except Exception as e:
            logger.error('Can\'t save reg: ' + username)
            return True, False
        try:
            return True, Registration.objects.get(username = username).id
        except Registration.DoesNotExist:
            logger.error('Reg doesn\'t exist: ' + username)
            return True, False

class EditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'name', 'surname', 'bday', 'person_info', 'avatar']
        labels = {
            'username': 'Логин:',
            'name': 'Имя:',
            'surname': 'Фамилия:',
            'bday': 'День рождения:',
            'person_info': 'О себе:',
            'avatar': 'Выбрать изображение профиля:',
        }
        widgets = {
            'person_info': Textarea(),
        }

    def edit_user(self, current_user, f = None):
        username = self['username'].data.lower()
        if current_user.username != username:
            if not(re.match(r'^(?=.*[a-zA-Z].*)[A-Za-z0-9][A-Za-z0-9_\.]{2,31}$', username)):
                return False, 1
            else:
                try:
                    User.objects.get(username = self['username'].data.lower())
                    return False, 2
                except User.DoesNotExist:
                    try:
                        Registration.objects.get(username = self['username'].data.lower())
                        return False, 2
                    except Registration.DoesNotExist:
                        current_user.username = username
        if current_user.name != self['name'].data:
            if not(re.match(r'^[a-zA-Zа-яА-ЯЁ][a-zа-яё]{1,30}$', self['name'].data)):
                return False, 3
            current_user.name = self['name'].data
        if current_user.surname != self['surname'].data:
            if not(re.match(r'^[a-zA-Zа-яА-ЯЁ][a-zA-Zа-яА-ЯЁ\s\-]{1,30}$', self['surname'].data)):
                return False, 4
            current_user.surname = self['surname'].data
        if self['bday'].data:
            if current_user.bday != self['bday'].data:
                if int(self['bday'].data[:4]) < 1900 or int(self['bday'].data[:4]) >= 2020:
                    return False, 5
            current_user.bday = self['bday'].data
        if self['person_info'].data:
            if current_user.person_info != self['person_info'].data:
                current_user.person_info = self['person_info'].data[:255]
        else:
            current_user.person_info = ''
        if f:
            if current_user.avatar:
                if sha256(f.read()).hexdigest() != sha256(current_user.avatar.read()).hexdigest():
                    f.name = get_image_name(f.name)
                    current_user.avatar.delete()
                    current_user.avatar = f
                else:
                    return True, False
            else:
                f.name = get_image_name(f.name)
                current_user.avatar = f
        current_user.save()
        return True, True