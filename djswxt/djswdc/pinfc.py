from py532lib.i2c import *
from py532lib.constants import *
from py532lib.frame import *
from multiprocessing import Process,Queue
from djswdc.models import dc_data
from datetime import datetime
import time,pigpio,os

pi1 = pigpio.pi()
pn532 = Pn532_i2c()
pn532.SAMconfigure()

def set_gpioout(gpio_list,ontime,offtime,times):
    for i in range(times-1):
        for x in gpio_list:
            pi1.set_mode(x,pigpio.OUTPUT)
        for x in gpio_list:
            pi1.write(x,pigpio.HIGH)
        time.sleep(ontime)
        for x in gpio_list:
            pi1.write(x,pigpio.LOW)
        time.sleep(offtime)

def led(state):#显示效果
    if state == 'book':
        gpio_list = []
        set_gpioout(gpio_list,2,1,1)
    elif state == 'nobook':
        gpio_list = []
        set_gpioout(gpio_list,5,1,1)
    elif state == 'other':
        gpio_list = []
        set_gpioout(gpio_list,5,1,1)
    else:
        gpio_list = []
        set_gpioout(gpio_list,5,1,5)

def pn532_deal(data):#处理nfc数据过程
    dc_objects = dc_data.objects.filter(uid=data)
    if len(dc_objects)==1:
        dc_object = dc_objects[0]
        dc_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dc_date = datetime.now().strftime('%Y-%m-%d')
        dc_time = datetime.now().strftime('%H:%M:%S')
        if '06:00:00'<dc_time<'10:00:00' and not isindata(dc_date,dc_object.breakfast_eat):#早餐时间
            if dc_date in dc_object.breakfast_book:
                dc_object.breakfast_eat.append(dc_now)
                led('book')
            else:
                dc_object.breakfast_eat.append('*'+dc_now)
                led('nobook')
        elif '10:00:00'<dc_time<'14:00:00' and not isindata(dc_date,dc_object.lunch_eat):#中餐时间
            if dc_date in dc_object.lunch_book:
                dc_object.lunch_eat.append(dc_now)
                led('book')
            else:
                dc_object.lunch_eat.append('*'+dc_now)
                led('nobook')
        elif '15:30:00'<dc_time<'19:30:00' and not isindata(dc_date,dc_object.dinner_eat):#晚餐时间
            if dc_date in dc_object.dinner_book:
                dc_object.dinner_eat.append(dc_now)
                led('book')
            else:
                dc_object.dinner_eat.append('*'+dc_now)
                led('nobook')
        else:#其他时间
            dc_object.other_eat.append('*'+dc_now)
            led('other')
        dc_object.save()
    else:
        led('error')

def pn532_read(data):#循环监测pn532
    while True:
        card_data = pn532.read_mifare().get_data()
        data.put(card_data)
        time.sleep(2)

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