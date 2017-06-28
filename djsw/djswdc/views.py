from django.shortcuts import render,HttpResponse
from django.contrib.auth.models import User
from djswdc.models import dc_data,dc_conf
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.csrf import csrf_exempt
from djswdc.multipro import multpro_start
from py532lib.i2c import *
from datetime import datetime,timedelta
import time,re,json
from channels import Group

weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
value_dict = {0: '未订餐', 1: '早餐', 2: '中餐', 4: '晚餐', 3: '早中餐', 5: '早晚餐', 6: '中晚餐', 7: '早中晚餐'}

def userchat(request):
    return render(request,'chat.html')

def userhome(request):
    if request.user.is_authenticated:
        status = str(request.user)+' 用户已登陆！若非该用户，请退出后重新登陆！'
        return render(request,'status.html',{'status':status})
    else:
        status = '多么美好的一天！'
        return render(request,'home.html',{'status':status})

def userregister(request):
    if request.user.is_authenticated:
        status = str(request.user)+' 用户已登陆！若非该用户，请退出后再进行注册！'
        return render(request,'status.html',{'status':status})
    else:
        return render(request,'register.html',)

def userbook(request):
    if request.user.is_authenticated:
        result = dc_select()
        return render(request,'book.html',{'result':result})
    else:
        status = '订餐前，请先登录！'
        return render(request,'status.html',{'status':status})

def usercheck(request):#获取订餐情况
    if request.user.is_authenticated:
        result = dc_check(request)
        return render(request,'check.html',{'result':result})
    else:
        status = '查询前，请先登录！'
        return render(request, 'status.html', {'status': status})

def usermenu(request):#菜单
    menu = dc_conf.objects.get(conf=1).menu
    return render(request,'menu.html',{'menu':menu})

def userhelp(request):#帮助
    help = dc_conf.objects.get(conf=1).help
    return render(request,'help.html',{'help':help})

def useruser(request):
    if request.user.is_authenticated:
        if str(request.user) == '0000':
            useradmin = 1
        else:
            useradmin = 0
        return render(request,'user.html',{'useradmin':useradmin})
    else:
        status = '用户未登录，请先登录！'
        return render(request, 'status.html',{'status':status})

def dc_select():
    dc_now = datetime.now()
    list_select = []
    for x in range(7):
        dc_now_x = dc_now+timedelta(days=x+1)
        dc_date_x = dc_now_x.strftime('%Y-%m-%d')
        dc_time_x = dc_now_x.strftime('%H:%M:%S')
        dc_week_x = weekday[dc_now_x.weekday()]
        if x==0:
            dc_week_x=dc_week_x+' (明天)'
        elif x==1:
            dc_week_x=dc_week_x+' (后天)'
        if x==0 and  '19:00:00'<dc_time_x:
            disable = 1
        else:
            disable = 0
        list_select.append((dc_date_x,dc_week_x,disable))
    return list_select

def dc_check(request):
    username = request.user
    dc_now = datetime.now()
    list_select = []
    object = dc_data.objects.get(user=User.objects.get(username=username))
    for x in range(8):
        value = 0
        dc_now_x = dc_now + timedelta(days=x)
        dc_date_x = dc_now_x.strftime('%Y-%m-%d')
        dc_time_x = dc_now_x.strftime('%H:%M:%S')
        dc_week_x = weekday[dc_now_x.weekday()]
        if x == 0:
            dc_week_x = dc_week_x + ' (今天)'
        elif x == 1:
            dc_week_x = dc_week_x + ' (明天)'
        elif x == 2:
            dc_week_x = dc_week_x + ' (后天)'
        if dc_date_x in object.breakfast_book:
            value = value + 1
        if dc_date_x in object.lunch_book:
            value = value + 2
        if dc_date_x in object.dinner_book:
            value = value + 4
        print(dc_date_x, dc_week_x,value)
        list_select.append((dc_date_x, dc_week_x, value_dict[value]))
    return list_select

@csrf_exempt
def register_form(request):#注册
    num = request.POST.get('num')
    password = request.POST.get('password')
    password2 = request.POST.get('password2')
    name = request.POST.get('name')
    nfcobject = dc_conf.objects.get(conf=1)
    nfcobject.mode = 'register'
    nfcobject.save()
    time.sleep(10)
    nfcobject = dc_conf.objects.get(conf=1)
    if nfcobject.mode == 'register':
        status = '注册超时，请重试！！'
        nfcobject.mode = 'eat'
        nfcobject.save()
        return render(request,'status.html',{'status':status})
    elif nfcobject.mode == 'eat':
        uid = nfcobject.register
        nfcobject.register = ''
        nfcobject.save()
        if re.match(r'^\d{4}$',num) and re.match(r'^\d{4}$',password) and name and uid and password==password2:
            try:
                dc_data.objects.create(user=User.objects.create_user(username=num,password=password),uid=uid,name=name)
                status = '注册成功，请登陆！'
                return render(request, 'status.html', {'status': status})
            except:
                status = '注册失败，用户已存在或者其他问题！'
            return render(request, 'status.html', {'status': status})
        else:
            status = '注册失败，数据输入错误！'
            return render(request, 'status.html', {'status': status})

@csrf_exempt
def login_form(request):#登陆
    num = request.POST.get('num')
    password = request.POST.get('password')
    user = authenticate(request,username=num,password=password)
    if user is not None:
        login(request,user)
        status = '登入成功！'
        return render(request, 'status.html', {'status': status})
    else:
        status = '登入失败，请重试！'
        return render(request, 'status.html', {'status': status})

@csrf_exempt
def userlogout(request):#退出
    logout(request)
    status ='退出成功！'
    return render(request,'status.html',{'status':status})

@csrf_exempt
def user_form(request):#修改用户
    num = request.POST.get('num')
    password = request.POST.get('password')
    newpassword = request.POST.get('password2')
    newpassword2 = request.POST.get('password3')
    name = request.POST.get('name')
    user = authenticate(username=num,password=password)
    nfcobject = dc_conf.objects.get(conf=1)
    nfcobject.mode = 'change'
    nfcobject.save()
    time.sleep(10)
    nfcobject = dc_conf.objects.get(conf=1)
    if nfcobject.mode == 'change':
        status = '修改超时，请重试！！'
        nfcobject.mode = 'eat'
        nfcobject.save()
        return render(request,'status.html',{'status':status})
    elif nfcobject.mode == 'eat':
        uid = nfcobject.change
        nfcobject.change = ''
        nfcobject.save()
        if user and re.match(r'^\d{4}$',newpassword) and newpassword==newpassword2 and uid:
            object = dc_data.objects.get(user=user)
            user.set_password(newpassword)
            object.uid = uid
            if name:
                object.name = name
            user.save()
            object.save()
            userlogout(request)
            status = '资料修改成功，请重新登陆！'
            return render(request,'status.html',{'status':status})
        else:
            status = '密码输入错误！请重新输入!'
            return render(request,'status.html',{'status':status})

@csrf_exempt
def book_form(request):#订餐
    book_data = request.POST
    book_dict = dict(book_data)
    del book_dict['csrfmiddlewaretoken']
    user_object = User.objects.get(username=request.user)
    object = dc_data.objects.get(user=user_object)
    for book_date,book_value in book_dict.items():
        book_value = int(book_value[0])
        if book_value == 8:
            continue
        try:object.breakfast_book.remove(book_date)
        except:
            pass
        try:object.lunch_book.remove(book_date)
        except:
            pass
        try:object.dinner_book.remove(book_date)
        except:
            pass
        if book_value==1 or book_value==3 or book_value==5 or book_value==7:
            object.breakfast_book.append(book_date)
        if book_value==2 or book_value==3 or book_value==6 or book_value==7:
            object.lunch_book.append(book_date)
        if book_value==4 or book_value==5 or book_value==6 or book_value==7:
            object.dinner_book.append(book_date)
    object.save()
    status = '订餐成功'
    return render(request,'status.html',{'status':status})

@csrf_exempt
def admin_form(request):#用户管理
    num = request.POST.get('num')
    password = request.POST.get('password')
    menu = request.POST.get('menu')
    help = request.POST.get('help')
    user = authenticate(username='0000',password=password)
    if user and num=='0000':
        nfcobject = dc_conf.objects.get(conf=1)
        if menu:
            nfcobject.menu = menu
        if help:
            nfcobject.help = help
        nfcobject.save()
        status = '修改成功'
        return render(request,'status.html',{'status':status})
    else:
        status = '输入数据错误，请重试！'
        return render(request, 'status.html', {'status': status})

multpro_start()
