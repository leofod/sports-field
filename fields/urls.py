from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views
from .views import AddPlaygroundAdminView, ShowPlaygroundView, ShowPlaygroundMeetingView, ShowMapView, AddPlaygroundView, ShowAddedPlayground

urlpatterns = [
    path("admin/add/", AddPlaygroundAdminView.as_view(), name="addPlaygroundFormAdmin"),
    path("admin/add/<int:pid>", AddPlaygroundAdminView.as_view(), name="addPlaygroundFormAdmin"),
    path("add/", AddPlaygroundView.as_view(), name="addPlaygroundForm"),
    path("admin/list/", ShowAddedPlayground.as_view(), name="showAddedPlayground"),
    # path("a/", AsyncView.as_view(), name="async"),
    path("show/", ShowPlaygroundView.as_view(), name="showpPlaygrounds"),
    path("show/<str:sport>/<str:price>/<str:under>", ShowPlaygroundView.as_view(), name="showpPlaygrounds"),
    path("map/", ShowMapView.as_view(), name="showpMap"),
    path("show/<str:fid>", ShowPlaygroundMeetingView.as_view(), name="showPlaygroundInfo"),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
