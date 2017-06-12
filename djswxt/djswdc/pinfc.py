from py532lib.i2c import *
from py532lib.constants import *
from py532lib.frame import *
from multiprocessing import Process,Queue
from djswdc.models import dc_data
from datetime import datetime
import time

def led_book():
    pass
def led_nobook():
    pass
def led_other():
    print('error')
    pass

def pn532_deal(data):
    dc_objects = dc_data.objects.filter(uid=data)
    if len(dc_objects)==1:
        dc_object = dc_objects[0]
        dc_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dc_date = datetime.now().strftime('%Y-%m-%d ')
        dc_time = datetime.now().strftime('%H:%M:%S')
        if '06:00:00'<dc_time<'10:00:00':#早餐时间
            if dc_data in dc_object.breakfast_book:
                dc_object.breakfast_eat.append(dc_now)
                led_book()
            else:
                dc_object.breakfast_eat.append('*'+dc_now)
                led_nobook()
        elif '10:00:00'<dc_time<'14:00:00':#中餐时间
            if dc_data in dc_object.lunch_book:
                dc_object.lunch_eat.append(dc_now)
                led_book()
            else:
                dc_object.lunch_eat.append('*'+dc_now)
                led_nobook()
        elif '15:30:00'<dc_time<'19:30:00':#晚餐时间
            if dc_data in dc_object.dinner_book:
                dc_object.dinner_eat.append(dc_now)
                led_book()
            else:
                dc_object.dinner_eat.append('*'+dc_now)
                led_nobook()
        else:#其他时间
            dc_object.other_eat('*'+dc_now)
        dc_object.save()
    else:
        led_other()

def pn532_read(data):
    while True:
        pn532 = Pn532_i2c()
        pn532.SAMconfigure()
        card_data = pn532.read_mifare().get_data()
        data.put(card_data)
        time.sleep(3)

def pn532_data(data):
    while True:
        value = data.get(True)
        if value:
            pn532_deal(value)
            print(value)
