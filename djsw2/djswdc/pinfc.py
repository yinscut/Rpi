from py532lib.i2c import *
from py532lib.constants import *
from py532lib.frame import *
from djswdc.models import dc_data,dc_conf
from datetime import datetime
import time,os

pn532 = Pn532_i2c()
pn532.SAMconfigure()

def led(state):#显示效果
    if state == 'book':
       print('book')
    elif state == 'nobook':
       print('nobook')
    elif state == 'other':
       print('other')
    else:
       print('error')

def pn532_deal(data):#处理pn532数据
    dc_objects = dc_data.objects.filter(uid=data)
    nfcobject = dc_conf.objects.get(conf=1)
    if len(dc_objects)==1 and nfcobject.mode == 'eat':
        print('eatting')
        dc_object = dc_objects[0]
        dc_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dc_date = datetime.now().strftime('%Y-%m-%d')
        dc_time = datetime.now().strftime('%H:%M:%S')
        if '06:00:00'<dc_time<'10:00:00' and not isindata(dc_date,dc_object.breakfast_eat):#早餐时间
            if dc_date in dc_object.breakfast_book:
                dc_object.breakfast_eat.append(dc_now)
                isreponse(1)
                led('book')
           else:
               dc_object.breakfast_eat.append('*'+dc_now)
               isreponse(2)
               led('nobook')
        elif '10:00:00'<dc_time<'14:00:00' and not isindata(dc_date,dc_object.lunch_eat):#中餐时间
           if dc_date in dc_object.lunch_book:
               dc_object.lunch_eat.append(dc_now)
               isreponse(1)
               led('book')
           else:
               dc_object.lunch_eat.append('*'+dc_now)
               isreponse(2)
               led('nobook')
        elif '15:30:00'<dc_time<'19:30:00' and not isindata(dc_date,dc_object.dinner_eat):#晚餐时间
           if dc_date in dc_object.dinner_book:
               dc_object.dinner_eat.append(dc_now)
               isreponse(1)
               led('book')
           else:
               dc_object.dinner_eat.append('*'+dc_now)
               isreponse(2)
               led('nobook')
        else:#其他
           dc_object.other_eat.append('*'+dc_now)
           isreponse(3)
           led('other')
        dc_object.save()
    else:
        led('error')

def pn532_read(data):#pn532循环接收
    card_data = ''
    card_data_last = ''
    while True:
        card_data = str(pn532.read_mifare().get_data())
        print(card_data)
        nfcobject = dc_conf.objects.get(conf=1)
        if card_data != card_data_last:
            if nfcobject.mode == 'eat':
                nfcobject.eat = card_data
                nfcobject.save()
                data.put(card_data)
            elif nfcobject.mode == 'register':
                nfcobject.register = card_data
                nfcobject.mode = 'eat'
                nfcobject.save()
            elif nfcobject.mode == 'change':
                nfcobject.change = card_data
                nfcobject.mode = 'eat'
                nfcobject.save()
            else:
                nfcobject.mode = 'eat'
                nfcobject.save()
            card_data_last = card_data
        time.sleep(1)

def pn532_data(data):#转发pn532数据
    while True:
        value = data.get(True)
        if value:
            pn532_deal(value)

def isindata(dte,lst):#判断是否已经录入
    for x in lst:
        if dte in x :
            return 1
    return 0

def isreponse(state):
    nfcobject = dc_conf.objects.get(conf=1)
    if state == 1:
        nfcobject.response = 'book'
    elif state == 2:
        nfcobject.response = 'nobook'
    else:
        nfcobject.response = 'other'
    nfcobject.save()
