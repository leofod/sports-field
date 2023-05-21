from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from .views import IndexView, LoginView, RegView, EditView, ShowUserView, CheckRegView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("login/", LoginView.as_view(), name="login"),
    path("reg/", RegView.as_view(), name="reg"),
    path("reg/check/", CheckRegView.as_view(), name="checkReg"),
    path("edit/", EditView.as_view(), name="edit"),
    path("user/", ShowUserView.as_view(), name="showuser"),
    path("user/<str:usrn>", ShowUserView.as_view(), name="showuser"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
