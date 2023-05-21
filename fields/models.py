from django.db import models
from users.models import User
from django.contrib.postgres.fields import ArrayField

def field_directory_path(instance, filename):
    return 'fields/{0}/{1}'.format(instance.id, filename)

def user_field_directory_path(instance, filename):
    return 'add/{0}/{1}'.format(instance.id, filename)


# Станции метро.
class Under(models.Model):
    group_id = models.IntegerField()
    name = models.CharField(max_length=32)
    en_name = models.CharField(max_length=32, null=True)
    lat = models.FloatField(default=48.3139)
    lng = models.FloatField(default=40.2688)

# Виды спорта.
class Sport(models.Model):
    name = models.CharField(max_length=32)
    en_name = models.CharField(max_length=32)

# Площадки.
class Playground(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    url_name = models.CharField(max_length=64, unique=True)
    address = models.CharField(max_length=64)
    group_id = models.IntegerField()
    photo = models.ImageField(upload_to = field_directory_path, null=True)
    price = models.BooleanField(default=False)
    link = models.CharField(max_length=64)
    field_info = models.CharField(max_length=128, null=True)
    lat = models.FloatField(default=55.7603)
    lng = models.FloatField(default=37.6300)
    grade = models.SmallIntegerField(null=True)

# Добавленные пользователями площадки.
class AddPlayground(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, null=True)
    address = models.CharField(max_length=256)
    price = models.BooleanField(default=False)
    photo = models.ImageField(upload_to = user_field_directory_path, null=True)
    field_info = models.CharField(max_length=128, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_add = models.DateField(auto_now_add=True)


# Встречи.
class Meeting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE)
    date_meet = models.DateField()

# Оценка от пользователя.
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE)
    mark = models.SmallIntegerField()
    # mark = models.CharField(max_length=2, null=True)
    date_mark = models.DateField()

# Где и чем пользователь занимался чаще.
class Visit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    # sport = ArrayField(models.ForeignKey(Sport, on_delete=models.CASCADE), size=3)
    sport_id = ArrayField(models.SmallIntegerField(), size=3)
    group_id = ArrayField(models.SmallIntegerField(), size=3)

# Средний рейтинг для каждой площадки.
class AvgRating(models.Model):
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE)
    sum_mark = models.SmallIntegerField()
    count_mark = models.SmallIntegerField()

# Избранные площадки.
class FavoritePlaygrounds(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE)
    