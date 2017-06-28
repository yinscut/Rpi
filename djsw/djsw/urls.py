"""djsw URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from djswdc.views import userchat,userhome,userregister,userbook,usermenu,userhelp,usercheck,useruser,register_form,login_form,userlogout,user_form,book_form,admin_form

urlpatterns = [
    url(r'^$', userhome),
    url(r'^userchat/$', userchat),
    url(r'^userregister/$', userregister),
    url(r'^userbook/$', userbook),
    url(r'^usercheck/$', usercheck),
    url(r'^usermenu/$', usermenu),
    url(r'^userhelp/$', userhelp),
    url(r'^useruser/$', useruser,),
    url(r'^userlogout/$', userlogout),
    url(r'^register/$', register_form),
    url(r'^login/$', login_form),
    url(r'^user/$', user_form),
    url(r'^book/$', book_form),
    url(r'^admin2/$',admin_form),
    url(r'^admin/', admin.site.urls),
]
