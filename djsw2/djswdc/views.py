from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from djswdc.models import dc_data,dc_conf
from djswdc.multipro import multpro_start
import time,re

weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
value_dict = ['未订餐',  '早餐',  '中餐', '晚餐', '早中餐', '早晚餐', '中晚餐', '早中晚餐']

@csrf_exempt
def home(request):
    return render(request,'home.html',{})

@csrf_exempt
def register_form(request):#注册表单
    num = request.POST.get('num')
    name = request.POST.get('name')
    password = request.POST.get('password')
    password2 = request.POST.get('password2')
    nfcobject = dc_conf.objects.get(conf=1)
    nfcobject.mode = 'register'
    nfcobject.save()
    time.sleep(10)
    nfcobject = dc_conf.objects.get(conf=1)
    if nfcobject.mode == 'register':
        status = '注册超时，请重试！！'
        nfcobject.mode = 'eat'
        nfcobject.save()
        return render(request,'/static/register.html',{'status':status})
    elif nfcobject.mode == 'eat':
        uid = nfcobject.register
        nfcobject.register = ''
        nfcobject.save()
        if re.match(r'^\d{4}$',num) and re.match(r'^\d{4}$',password) and name and uid and password==password2:
            try:
                dc_data.objects.create(user=User.objects.create_user(username=num,password=password),uid=uid,name=name)
                status = '注册成功，请登陆！'
                return render(request, '/static/home.html', {'status': status})
            except:
                status = '注册失败，用户已存在或者其他问题！'
            return render(request, '/static/register.html', {'status': status})
        else:
            status = '注册失败，数据输入错误！'
            return render(request, '/static/register.html', {'status': status})
        
@csrf_exempt
def login_form(request):#登陆表单
    num = request.POST.get('num')
    password = request.POST.get('password')
    user = authenticate(request,username=num,password=password)
    if user:
        login(request,user)
        status = '登入成功！'
        return render(request, '/static/book.html', {'status': status})
    else:
        status = '登入失败，请重试！'
        print('登陆失败')
        return render(request, '/static/home.html', {'status': status})

@csrf_exempt
def userlogout(request):#退出
    logout(request)
    state ='退出成功！'
    return render(request,'home.html', {'status': status})

@csrf_exempt
def user_form(request):#修改资料表单
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
        return render(request,'/static/register.html',{'status':status})
    elif nfcobject.mode == 'eat':
        uid = nfcobject.change
        nfcobject.change = ''
        nfcobject.save()
        if user and re.match(r'^\d{4}$',newpassword) and newpassword==newpassword2 and uid:
            dcobject = dc_data.objects.get(user=user)
            user.set_password(newpassword)
            dcobject.uid = uid
            if name:
                object.name = name
            user.save()
            dcobject.save()
            userlogout(request)
            status = '资料修改成功，请重新登陆！'
            return render(request,'/static/home.html',{'status':status})
        else:
            status = '密码输入错误！请重新输入!'
            return render(request,'/static/user.html',{'status':status})
        
@csrf_exempt
def admin_form(request):#修改信息表单
    num = request.POST.get('num')
    password = request.POST.get('password')
    usermenu = request.POST.get('menu')
    userhelp = request.POST.get('help')
    user = authenticate(username='0000',password=password)
    if user and num=='0000':
        nfcobject = dc_conf.objects.get(conf=1)
        if menu:
            nfcobject.menu = menu
        if userhelp:
            nfcobject.help = userhelp
        nfcobject.save()
        status = '修改成功'
        return render(request, '/static/register.html', {'status':status})
    else:
        status = '输入数据错误，请重试！'
        return render(request, '/static/register.html', {'status': status})

@csrf_exempt
def book_form(request):#订餐表单
    book_data = request.POST
    book_dict = dict(book_data)
    del book_dict['csrfmiddlewaretoken']
    try:
        username = str(request.user)
        user_object = User.objects.get(username=username)
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
        return render(request,'/static/book.html',{'status':status})
    except:
        status = '用户不存在或者其他错误，请重试！'
        return render(request,'/static/book.html',{'status':status})
    
@csrf_exempt
def check_dc_data(request):#查询订餐情况
    username = str(request.user)
    dc_now = datetime.now()
    dc_data_list = []
    try:
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
            dc_data_list.append((dc_date_x, dc_week_x, value_dict[value]))
        status = '查询成功'
        return render(request,'/static/check.html',{'select':dc_data_list'}
    except:
        status = '用户不存在或者其他错误，请重试！'
        return render(request,'/static/book.html',{'status':status})

multpro_start()