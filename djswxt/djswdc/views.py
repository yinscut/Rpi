from django.shortcuts import render,HttpResponse
from django.contrib.auth.models import User
from djswdc.models import dc_data
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.csrf import csrf_exempt
from djswdc.multipro import multpro_start
from py532lib.i2c import *
def home(request):
    return render(request,'userlogin.html')

multpro_start()

def pn532_read():
    pn532 = Pn532_i2c()
    pn532.SAMconfigure()
    card_data = pn532.read_mifare().get_data()
    print(card_data)
    return card_data

@csrf_exempt
def userregister(request):
    num = request.POST.get('num')
    password = request.POST.get('password')
    uid = str(pn532_read())
    try:
        dc_data.objects.create(user=User.objects.create_user(username=num,password=password),uid=uid)
    except:
        return HttpResponse('exist or error')
    else:
        return HttpResponse('create')

@csrf_exempt
def userlogin(request):
    print(request.user)
    num = request.POST.get('num')
    password = request.POST.get('password')
    user = authenticate(request,username=num,password=password)
    if user is not None:
        login(request,user)
        print('login')
        return HttpResponse('login')
    else:
        print('unlogin')
        return HttpResponse('unlogin')

def islogin(request):
    if request.user.is_authenticated:
        return HttpResponse('YES')
    else:
        return HttpResponse('NO')

@csrf_exempt
def userlogout(request):
    logout(request)
    print('logout')
    return HttpResponse('logout')


