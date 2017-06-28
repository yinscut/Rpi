from multiprocessing import Process,Queue
from djswdc/pinfc import pn532_read,pn532_data

def multpro_start():
    q = Queue()
    pw = Process(target=pn532_read,args=(q,))
    pr = Process(target=pn532_data,args=(q,))
    pw.start()
    pr.start()
