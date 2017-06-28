from py532lib.i2c import *
from py532lib.constants import *
from py532lib.frame import *
from multiprocessing import Process,Queue
from djswdc.models import dc_data,dc_conf
from datetime import datetime
from channels import Group
import time,os
from omxplayer import OMXPlayer

pn532 = Pn532_i2c()
pn532.SAMconfigure()

def play(url='/home/pi/nihao.mp3'):
    OMXPlayer(url).play()
    print(os.getcwd())

def chat(state,uid):#显示效果
    if state == 'book':
        play()
        Group('chat').send({'text':'book'})
        print('book')
    elif state == 'nobook':
        play()
        Group('chat').send({'text': 'nobook'})
        print('nobook')
    elif state == 'other':
        play()
        Group('chat').send({'text': 'other'})
        print('other')
    else:
        play()
        Group('chat').send({'text': 'error'})
        print('error')

def pn532_deal(data):#处理nfc数据过程
    uid = data
    dc_objects = dc_data.objects.filter(uid=uid)
    nfcobject = dc_conf.objects.get(conf=1)
    if len(dc_objects)==1 and nfcobject.mode == 'eat':
        print('eat')
        dc_object = dc_objects[0]
        dc_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dc_date = datetime.now().strftime('%Y-%m-%d')
        dc_time = datetime.now().strftime('%H:%M:%S')
        if '06:00:00'<dc_time<'10:00:00' and not isindata(dc_date,dc_object.breakfast_eat):#早餐时间
           if dc_date in dc_object.breakfast_book:
               dc_object.breakfast_eat.append(dc_now)
               chat('book',uid)
           else:
               dc_object.breakfast_eat.append('*'+dc_now)
               chat('nobook',uid)
        elif '10:00:00'<dc_time<'14:00:00' and not isindata(dc_date,dc_object.lunch_eat):#中餐时间
           if dc_date in dc_object.lunch_book:
               dc_object.lunch_eat.append(dc_now)
               chat('book',uid)
           else:
               dc_object.lunch_eat.append('*'+dc_now)
               chat('nobook',uid)
        elif '15:30:00'<dc_time<'19:30:00' and not isindata(dc_date,dc_object.dinner_eat):#晚餐时间
           if dc_date in dc_object.dinner_book:
               dc_object.dinner_eat.append(dc_now)
               chat('book',uid)
           else:
               dc_object.dinner_eat.append('*'+dc_now)
               chat('nobook',uid)
        else:#其他
           dc_object.other_eat.append('*'+dc_now)
           chat('other',uid)
        dc_object.save()
    else:
        chat('error',uid)

def pn532_read(data):#循环监测pn532
    card_data_last = ''
    while True:
        card_data = str(pn532.read_mifare().get_data())
        nfcobject = dc_conf.objects.get(conf=1)
        if card_data != card_data_last:
            if nfcobject.mode == 'eat':
                nfcobject.eat = card_data
                nfcobject.save()
                data.put(str(card_data))
            elif nfcobject.mode == 'register':
                nfcobject.register = card_data
                nfcobject.mode = 'eat'
                nfcobject.save()
            elif nfcobject.mode == 'change':
                nfcobject.change = card_data
                nfcobject.mode = 'eat'
                nfcobject.save()
            card_data_last = card_data
        time.sleep(1)

def pn532_data(data):#循环获取nfc数据
   while True:
       value = data.get(True)
       if value:
           pn532_deal(value)
           print(value)

def isindata(dte,lst):#判断是否已经录入
   for x in lst:
       if dte in x :
           return 1
   return 0

