from django.shortcuts import render,HttpResponse
from django.contrib.auth.models import User
from djswdc.models import dc_data
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.csrf import csrf_exempt
from djswdc.multipro import multpro_start
from py532lib.i2c import *
from datetime import datetime,timedelta
from djswdc.pinfc import isindata
import time,re

def userhome(request):
    if request.user.is_authenticated:
        status = request.user+'用户已登陆！若非本用户，请退出后重新登陆！'
        return render(request,'status.html',{'status':status})
    else:
        return render(request,'home.html',)

def userregister(request):
    if request.user.is_authenticated:
        status = request.user+'用户已登陆！若非本用户，请退出后重新登陆！'
        return render(request,'status.html',{'status':status})
    else:
        return render(request,'register.html',)






















def userdatetime():#获取时间
    return (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def dc_state(request):#获取订餐情况
    dc_now = datetime.now()
    list_select = []
    try:
        object = dc_data.objects.get(user=User.objects.get(username=username))
        for x in range(8):
            value = 0
            dc_now_x = dc_now + timedelta(days=x)
            dc_date_x = dc_now_x.strftime('%Y-%m-%d')
            dc_time_x = dc_now_x.strftime('%H:%M:%S')
            dc_week_x = weekday[dc_now_x.weekday()]
            if x == 0:
                dc_week_x = dc_week_x + ' 今天'
            elif x == 1:
                dc_week_x = dc_week_x + ' 明天'
            elif x == 2:
                dc_week_x = dc_week_x + ' 后天'
            if dc_date_x in object.breakfast_book:
                value = value+1
            elif dc_date_x in object.lunch_book:
                value = value+2
            elif dc_date_x in object.dinner_book:
                value = value+4
            list_select.append((dc_date_x,dc_week_x,value_dict[value]))
        return list_select
    except:
        return 0

def home(request):#主页
    return render(request,'home.html',{'userdatetime':userdatetime()})

@csrf_exempt
def register(request):#注册
    num = request.POST.get('num')
    password = request.POST.get('password')
    password2 = request.POST.get('password2')
    name = request.POST.get('name')
    uid = str(pn532_register_read())
    if re.match(r'^\d{4}$',num) and re.match(r'^\d{4}$',password) and name and uid and password==password2:
        try:
            dc_data.objects.create(user=User.objects.create_user(username=num,password=password),uid=uid,name=name)
            state = '注册成功，请登陆！'
            print('注册成功，请登陆！')
            return render(request, 'home.html', {'state': state, 'userdatetime': userdatetime()})
        except:
            state = '注册失败，用户已存在！'
            print('注册失败，用户已存在！')
        return render(request, 'home.html', {'state': state, 'userdatetime': userdatetime()})
    else:
        state = '注册失败，数据输入错误！'
        print('注册失败，数据输入错误！')
        return render(request, 'home.html', {'state': state,'userdatetime':userdatetime()})

@csrf_exempt
def userlogin(request):#登陆
    num = request.POST.get('num')
    password = request.POST.get('password')
    user = authenticate(request,username=num,password=password)
    if user is not None:
        login(request,user)
        state = '登入成功！'
        print('登陆成功')
        return render(request, 'home.html', {'state': state,'userdatetime':userdatetime()})
    else:
        state = '登入失败，请重试！'
        print('登陆失败')
        return render(request, 'home.html', {'state': state,'userdatetime':userdatetime()})

@csrf_exempt
def userbook(request):
    if request.user.is_authenticated:
        user_data = request.POST
        user_dict = dict(user_data)
        del user_dict['csrfmiddlewaretoken']
        user_object = User.objects.get(username=request.user)
        object = dc_data.objects.get(user=user_object)
        for dc_date,dc_value in user_dict.items():
            dc_value = int(dc_value[0])
            try:object.breakfast_book.remove(dc_date)
            except:
                pass
            try:object.lunch_book.remove(dc_date)
            except:
                pass
            try:object.dinner_book.remove(dc_date)
            except:
                pass
            if dc_value==1 or dc_value==3 or dc_value==5 or dc_value==7:
                object.breakfast_book.append(dc_date)
            if dc_value==2 or dc_value==3 or dc_value==5 or dc_value==7:
                object.lunch_book.append(dc_date)
            if dc_value==4 or dc_value==5 or dc_value==6 or dc_value==7:
                object.dinner_book.append(dc_date)
            object.save()
        state = '订餐成功'
        dc_status = dc_state(request.user)
        return render(request,'usercheck.html',{'state':state,'dc_status':dc_status})
    else:
        state = '请先登录'
        render(request,'userbook.html',{'state':state,'userdatetime':userdatetime()})

def userlogin_html(request):
    return render(request,'userlogin.html',{'userdatetime':userdatetime()})
def userregister_html(request):
    return render(request,'userregister.html',{'userdatetime':userdatetime()})
def userbook_html(request):
    return render(request,'userbook.html',{'userdatetime':userdatetime()})
def userhelp_html(request):
    return render(request,'userhelp.html',{'userdatetime':userdatetime()})
def usermeau_html(request):
    return render(request,'usermeau.html',{'userdatetime':userdatetime()})
def usercheck_html(request):

    dc_status = dc_state(request.user)
    return render(request,'usercheck.html',{'dc_status':dc_status,'userdatetime':userdatetime()})

multpro_start()#运行nfc监测

def pn532_register_read():
    pn532 = Pn532_i2c()
    pn532.SAMconfigure()
    card_data = pn532.read_mifare().get_data()
    return card_data

weekday = ['周一','周二','周三','周四','周五','周六','周日']

def dc_select():
    dc_now = datetime.now()
    list_select = []
    for x in range(7):
        dc_now_x = dc_now+timedelta(days=x+1)
        dc_date_x = dc_now_x.strftime('%Y-%m-%d')
        dc_time_x = dc_now_x.strftime('%H:%M:%S')
        dc_week_x = weekday[dc_now_x.weekday()]
        if x==0 and  '19:00:00'<dc_time_x:
            disable = 1
        else:
            disable = 0
        if x==0:
            dc_week_x=dc_week_x+' 明天'
        elif x==1:
            dc_week_x=dc_week_x+' 后天'
        else:
            dc_week_x=dc_week_x+''
        list_select.append((dc_date_x,dc_week_x,disable))
    return list_select

def islogin(request):
    if request.user.is_authenticated:
        return HttpResponse('YES')
    else:
        return HttpResponse('NO')

@csrf_exempt
def userlogout(request):#退出
    logout(request)
    state ='退出成功！'
    return render(request,'home.html',{'state':state,'userdatetime':userdatetime()})

@csrf_exempt
def usercheck(request):
    username = request.user
    ck_list = ckdate(username)
    return


value_dict = {0:'未订餐',1:'早餐',2:'中餐',4:'晚餐',3:'早中餐',5:'早晚餐',6:'中晚餐',7:'早中晚餐'}






