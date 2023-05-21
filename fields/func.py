from .models import Sport, Under, Playground, Meeting, Rating, Visit, AvgRating, FavoritePlaygrounds, AddPlayground
from users.models import User
from django.db.models import Count, Sum
from datetime import date, timedelta, datetime
from random import randint
from django.conf import settings
import os, shutil, random


# Рейтинг площадки.
def calc_grade(count_membebrs, avg_rate):
    return count_membebrs**2 + int(avg_rate.sum_mark**2/(avg_rate.count_mark+1))

# Количестов добавлений площадок пользователем сегодня.
def get_count_added_playground(uid):
    return AddPlayground.objects.filter(user=User.objects.get(pk=uid)).filter(date_add=date.today()).count() < 3

# Список площадок, добавленных пользователями.
def get_added_playground():
    return AddPlayground.objects.filter(date_add__lt=date.today())[:20]

# Возвращает добавленную площадку по id.
def get_one_added_playground(pid):
    try:
        return AddPlayground.objects.get(pk=pid)
    except AddPlayground.DoesNotExist:
        return False
    
# Копирование фотографии из /add/ в /fields/. 
def move_image(from_pid, to_p):
    p = AddPlayground.objects.get(pk=from_pid)
    path_from = os.path.join(settings.MEDIA_ROOT, p.photo.name)
    path_to = os.path.join(str(settings.MEDIA_ROOT), 'fields/', str(to_p.id))
    os.mkdir(path_to, mode=0o775)
    shutil.copy(path_from, path_to)
    to_p.photo = 'fields/{0}{1}'.format(to_p.id, path_from[path_from.rindex('/'):])
    to_p.save()
    p.photo.delete()
    os.rmdir(path_from[:path_from.rindex('/')])
    p.delete()
    return True

# Генерация имени картинки.
def get_image_name(name):
    chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',\
            'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',\
            'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    return ''.join(random.choices(chars, k=12)) + name[name.rindex('.'):]

    
# Удалить фотографию из /add
def delete_image(pid):
    p = AddPlayground.objects.get(pk=pid)
    path_dir = os.path.join(settings.MEDIA_ROOT, p.photo.name[:p.photo.name.rindex('/')])
    p.photo.delete()
    os.rmdir(path_dir)
    p.delete()
    return True

# Посчитать рейтинг для каждой площадки
def fill_raiting_field():
    playgrounds = Playground.objects.all()
    for p in playgrounds:
        # print(p.id, calc_grade(Meeting.objects.filter(playground=p).filter(date_meet=date.today().strftime('%Y-%m-%d')).count(), \
                    # AvgRating.objects.get(playground = p)))
        p.grade = calc_grade(Meeting.objects.filter(playground=p).filter(date_meet=date.today().strftime('%Y-%m-%d')).count(), \
                            AvgRating.objects.get(playground = p))
        p.save()
    return

# Наполнение таблицы самых популярных площадок для каждого пользователя.
def fill_visited_fields():
    users = User.objects.all()
    for u in users:
        # На какие площадки пользователь записался самое большое количество раз, начиная с прошлой недели. 
        m = Meeting.objects.all().values('playground').annotate(count = Count('id')).filter(user=u).\
                        filter(date_meet__gt=date.today()-timedelta(7)).order_by('-count')[:3]
        list_sport = []
        list_group_id = []        
        # Если пользователь, как минимум раз, записывался на какую-либо площадку.
        if len(m):
            for i in m:
                p = Playground.objects.get(id = i['playground'])
                list_sport.append(p.sport.id)
                list_group_id.append(p.group_id)
        else:
            list_sport.append(1)
            list_group_id.append(913)
            # Дефолтные значения [футбол, щука]
            # p = Playground.objects.first()
        v = Visit()
        v.user = u
        v.sport_id = list_sport
        v.group_id = list_group_id
        v.save()
    return

# Рекомендованные площадки.
def get_recommended_fields(uid=None):
    if uid: 
        try:
            v = Visit.objects.get(user = uid)
            return Playground.objects.filter(group_id__in=v.group_id).filter(sport__in=v.sport_id).order_by('-grade')[:20]
        except Visit.DoesNotExist:
            return Playground.objects.all().order_by('-grade')[:20]
    return Playground.objects.all()[:20]

# Для каждой площадки подсчитывается сумма и количество оценок.
def fill_avg_mark():
    # p = Rating.objects.values('mark')
    p = Rating.objects.values('playground').annotate(total = Sum('mark')).annotate(count = Count('mark'))
    for i in Playground.objects.all():
        for j in p:
            if i.pk == j['playground']:
                try:
                    exist_avg = AvgRating.objects.get(playground = i)
                    exist_avg.count_mark = j['count']
                    exist_avg.sum_mark = j['total']
                    exist_avg.save()
                except AvgRating.DoesNotExist:
                    new_avg = AvgRating()
                    new_avg.playground = i
                    new_avg.count_mark = j['count']
                    new_avg.sum_mark = j['total']
                    new_avg.save()
                break
        else:
            try:
                exist_avg = AvgRating.objects.get(playground = i)
            except AvgRating.DoesNotExist:
                new_avg = AvgRating()
                new_avg.playground = i
                new_avg.count_mark = 0
                new_avg.sum_mark = 0
                new_avg.save()
    return

# Заполнить таблицу Meeting случайными значениями
def fill_members():
    users = User.objects.all()
    week = get_week(False)
    playgrounds = Playground.objects.all()
    for i in users:
        for j in week:
            for k in playgrounds:
                if not(randint(0, 3)):
                    m = Meeting()
                    m.date_meet = j
                    m.playground = k
                    m.user = i
                    m.save()
    return

# Заполнить таблицу Raiting случайными значениями
def fill_raitings():
    users = User.objects.all()
    today = date.today().strftime('%Y-%m-%d')
    playgrounds = Playground.objects.all()
    for i in users:
        for k in playgrounds:
            if randint(0, 1):
                value_mark = randint(1, 10)
                if value_mark <= 2:
                    mark = 1
                elif value_mark <= 3:
                    mark = 2
                elif value_mark <= 4:
                    mark = 3
                elif value_mark <= 6:
                    mark = 4
                else:
                    mark = 5
                r = Rating()
                r.mark = mark
                r.playground = k
                r.user = i
                r.date_mark = today
                r.save()


# Получить название всех станций метро.
def get_under():
    try:
        return Under.objects.values('name')
    except Under.DoesNotExist:
        return False

# Координаты метро.
def get_under_coord(uname):
    try:
        under = Under.objects.get(name=uname)
        return under.lat, under.lng
    except Under.DoesNotExist:
        return False, False
    
# Получить всю информацию о видах спорта.
def get_sport():
    try:
        return Sport.objects.all()
    except Sport.DoesNotExist:
        return False

# Получить 7 ближайших дней. 
def get_week(fl):
    ret_str = ['']*7
    for i in range(7):
        # Для фронта.
        if(fl):
            ret_str[i] = (datetime.today() + timedelta(i))
        # Для бэка.
        else:
            ret_str[i] = (date.today() + timedelta(i)).strftime('%Y-%m-%d')
    return ret_str

# Получить всю информацию площадки по url'у.
def get_field(uname):
    try:
        return Playground.objects.get(url_name = uname)
    except Playground.DoesNotExist:
        return False

# Информация о встречах на площадке на ближайшую неделю.
def get_members(f, uid):
    w = get_week(False)
    meeting = Meeting.objects.filter(playground = f).filter(date_meet__in = w)
    if meeting.count() == 0:
        return False, False
    return_str = [[0] * 3 for i in range(meeting.count())]
    user_activity = []
    for i, m in enumerate(meeting):
        if m.user.pk == uid:
            user_activity.append(m.date_meet.strftime("%Y-%m-%d"))
        return_str[i][0] = m.date_meet.strftime("%Y-%m-%d")
        return_str[i][1] = m.user.name + " " + m.user.surname
        return_str[i][2] = m.user.username
    return return_str, user_activity

# Информация об оценке площадке от пользователя.
def get_raiting_value(uid, fname):
    try:
        f = Playground.objects.get(url_name = fname)
    except Playground.DoesNotExist:
        return False, False, False
    try:
        FavoritePlaygrounds.objects.get(user = uid, playground = f)
        favor_flag = True
    except FavoritePlaygrounds.DoesNotExist:
        favor_flag = False
    u = User.objects.get(pk = uid)
    # Если пользователь ставил оценку данной площадке в течение последних 30 дней.
    try:
        rating = Rating.objects.get(user = uid, playground = f)
        if rating.date_mark < date.today() - timedelta(30):
            return rating.mark, True, favor_flag
        return rating.mark, False, favor_flag
    except Rating.DoesNotExist:
        return False, True, favor_flag
    
