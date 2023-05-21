from django.db import models
import uuid

def user_directory_path(instance, filename):
    return 'users/{0}/{1}'.format(instance.username, filename)

# Пользователь.
class User(models.Model):
    username = models.CharField(unique=True, max_length=32)
    name = models.CharField(max_length=32)
    surname = models.CharField(max_length=32)
    bday = models.DateField(null=True)
    email = models.CharField(max_length=32)
    password = models.CharField(max_length=64)
    person_info = models.CharField(max_length=256, null=True)
    avatar = models.ImageField(upload_to = user_directory_path, null=True)

# Запись при регистрации.
class Registration(models.Model):
    username = models.CharField(unique=True, max_length=32)
    name = models.CharField(max_length=32)
    surname = models.CharField(max_length=32)
    email = models.CharField(max_length=32)
    password = models.CharField(max_length=64)
    time_add = models.DateTimeField()
    verification_code = models.CharField(max_length=8)
    
# Админы.
class Admin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permissions = models.CharField(max_length=3, null=True)