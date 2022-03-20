"""djangapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views
# from django.conf import settings
# from django.conf.urls.static import static
urlpatterns = [
    path("", views.login), #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    # path("disp_db/", views.Display_DB),
    path("menu/", views.Menu),
    path("loggedinmenu/", views.Menu),
    path("menu/newblock/", views.newblock),
    path("menu/newblock/newblockstore/", views.newblockstore),
    path("menu/insertblock/", views.insertblock),
    path("menu/insertblock/insertblockstore/", views.insertblockstore),
    path("menu/updateblock/", views.updateblock),
    path("menu/updateblock/updateblockstore/", views.updateblockstore),
    path("menu/viewblock/", views.viewblock),
    path("menu/viewblock/viewprof/", views.viewprofile),
    path("menu/viewblock/viewprof/viewmed/", views.viewmedical),
    path("menu/reset/", views.reset),
    path("menu/reset/resetresult/", views.resetquestion),
]
