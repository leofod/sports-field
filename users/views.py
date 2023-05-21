from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views import View
from .forms import LoginForm, RegForm, EditForm, CheckRegForm, ResendVC, DeleteAcc
from .func import get_user, get_meetings, get_verification_email, get_date_in, get_admin
from fields.func import get_recommended_fields
import logging

logger = logging.getLogger(__name__)

def check_login(func):
    def wrapper(self, request, *args, **kwargs):
        kwargs['url'] = 'nolog.html'
        if(request.session.get('user_id')):
            kwargs['ses'] = request.session.get('user_id')
            kwargs['url'] = 'log.html'
        return func(self, request, *args, **kwargs)
    return wrapper

def check_admin(func):
    def wrapper(self, request, *args, **kwargs):
        if get_admin(request.session.get('user_id')):
            return func(self, request, *args, **kwargs)
        return HttpResponseRedirect('/')
    return wrapper


def go_login(func):
    def wrapper(self, request, *args, **kwargs):
        if not(request.session.get('user_id')):
            return HttpResponseRedirect('/login')
        kwargs['ses'] = request.session.get('user_id')
        kwargs['url'] = 'log.html'
        return func(self, request, *args, **kwargs)
    return wrapper

def del_sess(func):
    def wrapper(self, request, *args, **kwargs):
        if(request.session.get('user_id')):
            logger.info('Out - ' + str(request.session['user_id']))
            del request.session['user_id']
            return HttpResponseRedirect('/')
        return func(self, request, *args, **kwargs)
    return wrapper

def go_reg(func):
    def wrapper(self, request, *args, **kwargs):
        if(request.session.get('user_id')):
            return HttpResponseRedirect('/')
        kwargs['url'] = 'nolog.html'
        return func(self, request, *args, **kwargs)
    return wrapper

def check_reg(func):
    def wrapper(self, request, *args, **kwargs):
        if(request.session.get('reg_id') and not request.session.get('user_id')):
            kwargs['reg'] = request.session.get('reg_id')
            kwargs['url'] = 'nolog.html'
            return func(self, request, *args, **kwargs)
        return HttpResponseRedirect('/')
    return wrapper

class IndexView(View):
    template_name = 'main.html'    

    @check_login
    def get(self, request, *args, **kwargs):
        if len(kwargs) >= 2:
            flds = get_recommended_fields(kwargs['ses'])
        flds = get_recommended_fields()
        return render(request, self.template_name, {"url": kwargs['url'], "instance": flds})
    
class LoginView(View):
    form_class = LoginForm
    initial = {'key': 'value'}
    template_name = 'loginUser.html'

    @del_sess
    @check_login
    def get(self, request, *args, **kwargs):    
        form = self.form_class(initial = self.initial)
        return render(request, self.template_name, {"form": form, "url": kwargs['url']})

    @check_login
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        ans, response = form.checkLog()
        if ans:
            if response:
                logger.info('In - ' + str(response))
                request.session['user_id'] = response
                return HttpResponseRedirect("/")
            return render(request, self.template_name, {"form": form, "error": True, "url": kwargs['url']})
        else:
            return render(request, self.template_name, {"form": form, "error": False, "url": kwargs['url']})

class CheckRegView(View):
    initial = {'key': 'value'}
    template_name = 'checkRegistration.html'

    @check_reg
    def get(self, request, *args, **kwargs):
        form_vc = CheckRegForm(self.request.GET or None)
        form_rs = ResendVC(self.request.GET or None)
        form_del = DeleteAcc(self.request.GET or None)
        return render(request, self.template_name, {"form": form_vc, "resend": form_rs, "delete": form_del, \
                                                    "email": get_verification_email(kwargs['reg']), "url": kwargs['url']})

    @check_reg
    def post(self, request, *args, **kwargs):
        form_vc = CheckRegForm(self.request.POST)
        form_rs = ResendVC(self.request.POST)
        form_del = DeleteAcc(self.request.POST)
        vc_ans, vc_response = form_vc.check_verificaton(kwargs['reg'])
        rs_ans, rs_resend = form_rs.resend_verefecation_code(kwargs['reg'])
        del_ans = form_del.delete_account_reg(kwargs['reg'])
        if vc_ans:
            if vc_response:
                del request.session['reg_id']
                request.session['user_id'] = vc_response
                logger.info('DR - ' + str(kwargs['reg']))
                logger.info('CU - ' + str(vc_response))
                return JsonResponse({"redirect": True}, status = 200)
            return JsonResponse({"no_empty": True}, status = 200)
        if rs_ans:
            if rs_resend is True:
                logger.info('RR - ' + str(kwargs['reg']))
                return JsonResponse({"resend": True}, status = 200)
            return JsonResponse({"resend": rs_resend}, status = 200)
        if del_ans:
            del request.session['reg_id']
            return JsonResponse({"redirect": True}, status = 200)
        return JsonResponse({"no_empty": False}, status = 200)


class RegView(View):
    form_class = RegForm
    initial = {'key': 'value'}
    template_name = 'registrationUser.html'

    @go_reg
    def get(self, request, *args, **kwargs):
        form = self.form_class(initial = self.initial)
        return render(request, self.template_name, {"form": form, "url": kwargs['url']})

    @go_reg
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        check, response = form.check_registration()
        if check:
            if response:
                logger.info('CR - ' + str(response))
                request.session['reg_id'] = response
                return HttpResponseRedirect("/reg/check/")
            else:
                return render(request, self.template_name, {"form": form, "url": kwargs['url']})
        else:
            return render(request, self.template_name, {"form": form, "error": response, "url": kwargs['url']})


class EditView(View):
    form_class = EditForm
    initial = {'key': 'value'}
    template_name = 'editUser.html'

    @go_login
    def get(self, request, *args, **kwargs):
        form = self.form_class(initial = self.initial)
        user_info = get_user(kwargs['ses'], False)
        if user_info:
            return render(request, self.template_name, {"form": form, "user_info": user_info, "url": kwargs['url']})
        return render(request, self.template_name, {"form": form, "url": kwargs['url']})

    @check_login
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        user_info = get_user(kwargs['ses'], False)
        if request.FILES:
            check, response = form.edit_user(user_info, request.FILES['avatar'])
        else:
            check, response = form.edit_user(user_info)
        if check:
            user_info = get_user(kwargs['ses'], False)
            if not(response):
                return HttpResponseRedirect("/user/" + user_info.username)
            logger.info('UU - ' + str(user_info.id))
            return render(request, self.template_name, {"form": form, "user_info": user_info, "url": kwargs['url']})
        else:
            return render(request, self.template_name, {"form": form, "user_info": user_info, "error": response, "url": kwargs['url']})


class ShowUserView(View):
    template_name = 'showUser.html'    

    @go_login
    def get(self, request, *args, **kwargs):
        if len(kwargs) >= 3:
            u = get_user(kwargs['usrn'], True)
        else:
            u = get_user(kwargs['ses'], False)
            kwargs['usrn'] = u.username
        if u:
            if len(kwargs) >= 3:
                flag_me = False
                if u.id == kwargs['ses']:
                    flag_me = True
                meets = get_meetings(u)
                meets_d = get_date_in(meets)
                return render(request, self.template_name, {"user_info": u, "meetings": meets, "meetings_date": meets_d,\
                                                            "url": kwargs['url'],"title": kwargs['usrn'], "me": flag_me})
            return render(request, self.template_name, {"user_info": u, "url": kwargs['url'], "guest": True, "title": kwargs['usrn']})
        return render(request,  self.template_name, {"error_user": True, "url": kwargs['url'], "title": kwargs['usrn']})