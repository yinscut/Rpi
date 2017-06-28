from django.http import HttpResponse
from channels.handler import AsgiHandler
import time
from channels import Group
#message.reply_channel    一个客户端通道的对象
#message.reply_channel.send(chunk)  用来唯一返回这个客户端

#一个管道大概会持续30s

#当连接上时，发回去一个connect字符串
def ws_connect(message):
    message.reply_channel.send({"text":"连接成功！"})
    Group('chat').add(message.reply_channel)

#将发来的信息原样返回
def ws_message(message):
    message.reply_channel.send({"text": "发送消息！"})
    Group('chat').send({"text":"chat send"})

#断开连接时发送一个disconnect字符串，当然，他已经收不到了
def ws_disconnect(message):
    message.reply_channel.send({"text":"断开连接！"})