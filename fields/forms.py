from .models import Playground, Sport, Under, Meeting, Rating, FavoritePlaygrounds, AddPlayground
from users.models import User
from django import forms
from django.forms import NumberInput, PasswordInput, TextInput, Textarea
from .func import get_week, move_image, delete_image, get_image_name
from datetime import date
import re, logging

logger = logging.getLogger(__name__)

SOUTH = 55.5099
NORTH = 55.9839
EAST = 37.9288
WEST = 37.2791
LAT_STEP = (NORTH-SOUTH)/50
LNG_STEP = (EAST-WEST)/50

class AddPlaygroundAdminForm(forms.ModelForm):
    class Meta:
        model = Playground
        fields = ['sport', 'name', 'url_name', 'address', 'photo', 'price', 'link', 'field_info', 'lat', 'lng']
        labels = {
            'sport': 'Вид спорта (*): ',
            'name': 'Навзвание (*): ',
            'url_name': 'URL name (*): ',
            'address': 'Адрес (*):',
            'photo': 'Фото: ',
            'price': 'Тип площадки (*): ',
            'link': 'Ссылка: ',
            'field_info': 'Описание: ',
            'lat': 'Широта (*): ',
            'lng': 'Долгота (*): ',
        }
        widgets = {
            'price': TextInput(),
        }

    def uploadPlayground(self, pid, f = None):
        p = Playground()
        if not(self['name'].data):
            return False, 1
        if not(self['url_name'].data):
            return False, 2
        if not(self['address'].data):
            return False, 4
        if not(self['price'].data) or ((self['price'].data != '0') and (self['price'].data != '1')):
            return False, 5
        if not(self['link'].data):
            return False, 6
        if not(self['lat'].data):
            return False, 7
        if not(self['lng'].data):
            return False, 8
        try:
            Playground.objects.get(url_name=self['url_name'].data)
            return False, 3
        except Playground.DoesNotExist:
            pass
        try:
            p.sport = Sport.objects.get(pk = self['sport'].data)
        except Sport.DoesNotExist:
            return False, 9
        p.name = self['name'].data
        p.url_name = self['url_name'].data
        p.address = self['address'].data
        p.price = self['price'].data
        p.link = self['link'].data
        p.field_info = self['field_info'].data
        p.lat = self['lat'].data
        p.lng = self['lng'].data
        p.group_id = int((NORTH - float(self['lat'].data))/LAT_STEP)*50+int((float(self['lng'].data) - WEST)/LNG_STEP)
        p.save()
        logger.info(f"CF - {p.url_name}")
        if f:
            pi = Playground.objects.latest('id')
            f.name = get_image_name(f.name)
            pi.photo = f
            pi.save()
            if pid:
                delete_image(pid)
        else:
            if pid:
                pi = Playground.objects.latest('id')
                if pi.photo:
                    move_image(pid, pi)
                else:
                    AddPlayground.objects.get(pk=pid).delete()
        if pid:
            logger.info(f"DT - {pid}")
        return True, True


class AddPlaygroundForm(forms.ModelForm):
    class Meta:
        model = AddPlayground
        fields = ['sport', 'name', 'address', 'photo', 'price', 'field_info']
        labels = {
            'sport': 'Вид спорта',
            'name': 'Навзвание',
            'address': 'Адрес или ссылка',
            'photo': 'Фото',
            'price': 'Тип площадки',
            'field_info': 'Описание',
        }
        widgets = {
            'price': TextInput(),
        }

    def uploadPlayground(self, uid, f = None):
        if not(self['sport'].data):
            return False, 1
        if not(self['address'].data):
            return False, 2
        if not(self['price'].data) or ((self['price'].data != '0') and (self['price'].data != '1')):
            return False, 3
        try:
            sp = Sport.objects.get(pk = int(self['sport'].data))
        except Sport.DoesNotExist:
            return False, 4
        u = User.objects.get(pk = uid)
        p = AddPlayground(sport=sp, name=self['name'].data[:64], address=self['address'].data[:256], price=int(self['price'].data), \
                       field_info=self['field_info'].data[:128], user=u)
        p.save()
        logger.info(f"CT - {uid}")
        if f:
            pi = AddPlayground.objects.filter(user=u).latest('id')
            f.name = get_image_name(f.name)
            pi.photo = f
            pi.save()
        return True, True


class ShowPlaygroundForm(forms.ModelForm):
    class Meta:
        model = Playground
        fields = ['sport', 'group_id', 'price']
        labels = {
            'sport': 'Вид спорта: ',
            'group_id': 'Метро: ',
            'price': 'Тип площадки: ',
        }
        widgets = {
            'price': TextInput(),
        }

    def getCrit(sport, price, under):
        try:
            sp = Sport.objects.get(en_name = sport).id
        except Sport.DoesNotExist:
            return False
        if price == 'all':
            pr = None
        elif price == 'free':
            pr = 0
        elif price == 'paid':
            pr = 1
        else:
            return False
        try:
            un = Under.objects.get(en_name = under).name
        except Under.DoesNotExist:
            return False
        return [sp, pr, un]
    
    def makeGroupList(self, seed, flag_add):
        if flag_add:
            return [seed-2, seed+2, seed-52, seed-48, seed-101, seed-100, seed-99, seed-150, seed-3, \
                    seed+48, seed+52, seed+99, seed+100, seed+101, seed+150, seed+3]
        return [seed, seed-1, seed+1, seed-50, seed-51, seed-49, seed+49, seed+50, seed+51]

    
    def getListPlaygrounds(self, flag_map, sport, price=None, un=None):
        if un is None:
            price = self['price'].data
            under = Under.objects.get(name = self['group_id'].data)
        else:
            under = Under.objects.get(name = un)
        ret_url_arr = [under.en_name]
        if price is not None:        
            ret_arr = Playground.objects.filter(group_id__in = self.makeGroupList(under.group_id, False)).filter(sport = sport).filter(price = price)[:15]
            if ret_arr.count() < 10:
                ret_arr |= Playground.objects.filter(group_id__in = self.makeGroupList(under.group_id, True)).filter(sport = sport).filter(price = price)[:(15-ret_arr.count())]
            if price == '1':
                ret_url_arr.append('paid')
            else:
                ret_url_arr.append('free')
        else:
            ret_arr = Playground.objects.filter(group_id__in = self.makeGroupList(under.group_id, False)).filter(sport = sport)[:15]
            if ret_arr.count() < 10:
                ret_arr |= Playground.objects.filter(group_id__in = self.makeGroupList(under.group_id, True)).filter(sport = sport)[:(15-ret_arr.count())]
            ret_url_arr.append('all')
        if ret_arr:
            if flag_map:
                ret_list = [[0] * 9 for i in range(ret_arr.count())]
                for i, p in enumerate(ret_arr):
                    ret_list[i][0] = p.name                        
                    ret_list[i][1] = p.url_name                        
                    ret_list[i][2] = p.address                        
                    ret_list[i][3] = p.price                        
                    ret_list[i][4] = p.link                        
                    ret_list[i][5] = p.field_info
                    if p.photo:
                        ret_list[i][6] = p.photo.url
                    else:
                        ret_list[i][6] = ''
                    ret_list[i][7] = p.lat                        
                    ret_list[i][8] = p.lng
                return ret_list, ret_url_arr
            return ret_arr, ret_url_arr
        return False, ret_url_arr


class ShowPlaygroundMeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['date_meet']

    def getPlayground(uname):
        try:
            return Playground.objects.get(url_name = uname)
        except Playground.DoesNotExist:
            return
    
    def getMembers(f):
        w = get_week(False)
        meeting = Meeting.objects.filter(playground = f).filter(date_meet__in = w)
        if meeting.count() == 0:
            return 0
        return_str = [[0] * 3 for i in range(meeting.count())]
        for i, m in enumerate(meeting):
            return_str[i][0] = m.date_meet.strftime("%Y-%m-%d")
            return_str[i][1] = m.user.name + " " + m.user.surname
            return_str[i][2] = m.user.username
        return return_str

    def signUpMeeting(self, fname, uid):
        if self['date_meet'].data not in get_week(False):
            return False, False, False
        f = Playground.objects.get(url_name = fname)
        u = User.objects.get(pk = uid)
        try:
            m = Meeting.objects.get(user = u, playground = f, date_meet = self['date_meet'].data)
            m.delete()
            logger.info(f"DM - {u.id} - {f.id} - {self['date_meet'].data}")
            return True, False, self['date_meet'].data
        except Meeting.DoesNotExist:
            if Meeting.objects.filter(user = u).filter(date_meet = self['date_meet'].data).count() >= 3:
                return True, True, False
            m = Meeting(date_meet=self['date_meet'].data, playground=f, user=u)
            m.save()
            logger.info(f"CM - {u.id} - {f.id} - {self['date_meet'].data}")
            return True, True, self['date_meet'].data


class RatePlaygroundForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['mark']

    def ratePlayground(self, fname, uid):
        if self['mark'].data and re.match(r'^\d{1}$', self['mark'].data) and int(self['mark'].data) >= 1 and int(self['mark'].data) <= 5:
            f = Playground.objects.get(url_name = fname)
            u = User.objects.get(pk = uid)
            try:
                r = Rating.objects.get(user = u, playground = f)
                r.mark = int(self['mark'].data)
                r.date_mark = date.today().strftime('%Y-%m-%d')
                r.save()
                logger.info(f"CR - {u.id} - {f.id}")
                return True, False
            except Rating.DoesNotExist:
                r = Rating(mark=int(self['mark'].data), playground=f, user=u, date_mark= date.today().strftime('%Y-%m-%d'))
                r.save()
                logger.info(f"UR - {u.id} - {f.id}")
                return True, True
        return False, False

 
class AddToFavor(forms.Form):
    check = forms.BooleanField()

    def change(self, fname, uid):
        if self['check'].data:
            f = Playground.objects.get(url_name = fname)
            u = User.objects.get(pk = uid)
            try:
                logger.info(f"DFP - {u.id} - {f.id}")
                p = FavoritePlaygrounds.objects.get(user = u, playground = f)
                p.delete()
                return True, False
            except FavoritePlaygrounds.DoesNotExist:
                logger.info(f"CFP - {u.id} - {f.id}")
                p = FavoritePlaygrounds(user = u, playground = f)
                p.save()
                return True, True
        return False, False