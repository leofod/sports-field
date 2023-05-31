from .forms import AddPlaygroundAdminForm, AddPlaygroundForm, ShowPlaygroundForm, ShowPlaygroundMeetingForm, RatePlaygroundForm, AddToFavor
from users.views import check_login, go_login, check_admin
from django.views import View
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from .func import get_under, get_sport, get_week, get_field, get_members, get_raiting_value, fill_members,\
                    fill_raitings, fill_visited_fields, fill_avg_mark, fill_raiting_field, get_count_added_playground, \
                    get_added_playground, get_one_added_playground, get_under_coord


def check_rate_scale(func):
    def wrapper(self, request, *args, **kwargs):
        if len(kwargs) >= 3:
            kwargs['rate_scale'], kwargs['rate_change'], kwargs['favor'] = get_raiting_value(kwargs['ses'], kwargs['fid'])
        return func(self, request, *args, **kwargs)
    return wrapper

class AddPlaygroundAdminView(View):
    form_class = AddPlaygroundAdminForm
    initial = {'key': 'value'}
    template_name = 'addPlaygroundFormAdmin.html'
    sport_list = get_sport()

    @go_login
    @check_admin
    def get(self, request, *args, **kwargs):
        form = self.form_class(initial = self.initial)
        if len(kwargs) >= 3:
            p = get_one_added_playground(kwargs['pid'])
            if p:
                return render(request, self.template_name, {"form": form, "sport": sport_list, \
                                                            "url": kwargs['url'], "playground": p})
        # fill_members()
        # fill_raitings()
        # fill_avg_mark()
        # fill_visited_fields()
        # fill_raiting_field()
        return render(request, self.template_name, {"form": form, "sport": sport_list, "url": kwargs['url']})

    @go_login
    @check_admin
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if len(kwargs) >= 3:
            pid = kwargs['pid']
        else:
            pid = False
        if request.FILES:
            ans, code = form.upload_playground(pid=pid, f=request.FILES['photo'])
        else:
            ans, code = form.upload_playground(pid=pid)
        if ans:
            return HttpResponseRedirect("/")
        return render(request, self.template_name, {"form": form, "sport": sport_list, "url": kwargs['url'], "error": code})

    
class ShowAddedPlayground(View):
    template_name = 'showAddedPlaygrounds.html'

    @go_login
    @check_admin
    def get(self, request, *args, **kwargs):
        return render(request,  self.template_name, {"url": kwargs['url'], "playground": get_added_playground()})

    
class AddPlaygroundView(View):
    form_class = AddPlaygroundForm
    initial = {'key': 'value'}
    template_name = 'addPlaygroundForm.html'
    sport_list = get_sport()

    @go_login
    def get(self, request, *args, **kwargs):
        if get_count_added_playground(kwargs['ses']):
            form = self.form_class(initial = self.initial)
            return render(request, self.template_name, {"form": form, "sport": sport_list, "url": kwargs['url']})
        else:
            return render(request, self.template_name, {"url": kwargs['url']})

    @go_login
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if request.FILES:
            ans, code = form.upload_playground(kwargs['ses'], request.FILES['photo'])
        else:
            ans, code = form.upload_playground(kwargs['ses'])
        if ans:
            return HttpResponseRedirect("/f/add/")
        return render(request, self.template_name, {"form": form, "sport": sport_list, "url": kwargs['url'], "error": code})


class ShowPlaygroundView(View):
    form_class = ShowPlaygroundForm
    initial = {'key': 'value'}
    template_name = 'showPlayground.html'
    global under_list, sport_list, u_list
    under_list = get_under()
    sport_list = get_sport()

    @check_login
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        if len(kwargs) >= 3:
            checkCrit = self.form_class.get_crit(kwargs['sport'], kwargs['price'], kwargs['under'])            
            if checkCrit:
                arr_fields, _ = form.get_list_playground(False, *checkCrit)
                if not(arr_fields):
                    return render(request, self.template_name, {"form": form, "sport": sport_list, "stations": under_list, "under": checkCrit[2], \
                                                                "choosen_sport": kwargs['sport'], "price": kwargs['price'], "error": "Нет площадок", "url": kwargs['url']})
                return render(request, self.template_name, {"form": form, "sport": sport_list, "stations": under_list, "under": checkCrit[2], \
                                                            "choosen_sport": kwargs['sport'], "price": kwargs['price'], "instance": arr_fields, "url": kwargs['url']})
            return render(request, self.template_name, {"form": form, "sport": sport_list, "stations": under_list, "error": "Неправильные аргументы в строке поиска.", "url": kwargs['url']})        
        return render(request, self.template_name, {"form": form, "sport": sport_list, "stations": under_list, "url": kwargs['url']})

    @check_login
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        try:
            under = under_list.get(name = form.data['group_id'])
        except:
            return render(request, self.template_name, {"form": form, "sport": sport_list, "stations": under_list, "error": "Выберите станцию метро из списка.", "url_change": True, "url": kwargs['url']})                    
        try:
            sport = sport_list.get(en_name = form.data['sport'])
        except:
            return render(request, self.template_name, {"form": form, "sport": sport_list, "stations": under_list, "under": under['name'], "error": "Выберите спорт.", "url_change": True, "url": kwargs['url']})                    
        arr_fields, url_adding = form.get_list_playground(False, sport.id)
        if not(arr_fields):
            return render(request, self.template_name, {"form": form, "sport": sport_list, "stations": under_list, "under": under['name'], "error": "Нет площадок", \
                                                        "url_sport": sport.en_name, "url_price": url_adding[1], "url_under": url_adding[0], "url": kwargs['url']})
        return render(request, self.template_name, {"form": form, "sport": sport_list, "stations": under_list, "under": under['name'], "instance": arr_fields, \
                                                    "url_sport": sport.en_name, "url_price": url_adding[1], "url_under": url_adding[0], "url": kwargs['url']})


class ShowMapView(View):
    form_class = ShowPlaygroundForm
    initial = {'key': 'value'}
    template_name = 'showMap.html'
    global under_list, sport_list, u_list
    under_list = get_under()
    sport_list = get_sport()

    @check_login
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form, "sport": sport_list, "stations": under_list, "url": kwargs['url']})

    @check_login
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        try:
            under = under_list.get(name = form.data['group_id'])
        except:
            return JsonResponse({"error": "Выберите станцию метро."}, status = 200)
        try:
            sport = sport_list.get(en_name = form.data['sport'])
        except:
            return JsonResponse({"error": "Выберите вид спорта."}, status = 200)
        arr_fields, _ = form.get_list_playground(True, sport)
        if not(arr_fields):
            return JsonResponse({"error": "Нет площадок по заданным критериям."}, status = 200)
        under_lat, under_lng = get_under_coord(under['name'])
        try:
            if form.data['price'] == '1':
                return JsonResponse({"ans": arr_fields, "lat": under_lat, "lng": under_lng, \
                                     "info": "Показаны платные площадки по " + sport.name.lower() + "у у станции метро \"" + under['name'] + "\"."}, status = 200)
            return JsonResponse({"ans": arr_fields, "lat": under_lat, "lng": under_lng, \
                                 "info": "Показаны бесплатные площадки по " + sport.name.lower() + "у у станции метро \"" + under['name'] + "\"."}, status = 200)
        except Exception as e:
            return JsonResponse({"ans": arr_fields, "lat": under_lat, "lng": under_lng, \
                                 "info": "Показаны все площадки по " + sport.name.lower() + "у у станции метро \"" + under['name'] + "\"."}, status = 200)


class ShowPlaygroundMeetingView(View):
    inital = {'key': 'value'}
    template_name = 'fieldInfo.html'

    @check_login
    @check_rate_scale
    def get(self, request, *args, **kwargs):
        if(kwargs['fid']):
            fld = get_field(kwargs['fid'])
            if fld:
                if(len(kwargs)>=3):
                    members, user_activiy = get_members(fld, kwargs['ses'])
                    if kwargs['rate_change']:
                        form_rate = RatePlaygroundForm(self.request.GET or None)
                    else:
                        form_rate = False
                    form_favor = AddToFavor(self.request.GET or None)
                    form_meet = ShowPlaygroundMeetingForm(self.request.GET or None)
                    return render(request, self.template_name, {"fld": fld, "form": form_meet, "star": form_rate, "favor": form_favor,\
                                                                "favor_flag": kwargs['favor'],"ex_star": int(kwargs['rate_scale']),\
                                                                "arrd": get_week(True), "members": members, "current": user_activiy, "url": kwargs['url']})
                return render(request, self.template_name, {"fld": fld, "url": kwargs['url']})
        return render(request, self.template_name, {"url": kwargs['url']})
    
    @check_login
    def post(self, request, *args, **kwargs):
        form_rate = RatePlaygroundForm(self.request.POST)
        form_meet = ShowPlaygroundMeetingForm(self.request.POST)
        form_favor = AddToFavor(self.request.POST)
        favor_ans, favor_in = form_favor.change(kwargs['fid'], kwargs['ses'])
        meet_ans, meet_in, meet_date = form_meet.sign_up_meeting(kwargs['fid'], kwargs['ses'])
        rate_ans, rate_new = form_rate.rate_playground(kwargs['fid'], kwargs['ses'])
        if favor_ans:
            return JsonResponse({"ans": favor_in}, status = 200)
        elif meet_ans:
            if not(meet_date):
                return JsonResponse({"ans": meet_in, "date": meet_date}, status = 200)
            return JsonResponse({"ans": meet_in, "date": meet_date}, status = 200)
        elif rate_ans:
            return JsonResponse({"ans": rate_new, "mark": form_rate.data['mark']}, status = 200)
        return JsonResponse({"empty_mark": True}, status=200)