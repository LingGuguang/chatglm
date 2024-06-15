# OPLogin.py文件
import re, json, jsonlines
from locust import HttpUser,task,TaskSet,between
import asyncio
from httpx import AsyncClient
import requests
from async_requests import chat_test
import websocket, time


class WebSocketClient(object):

    def __init__(self, host):
        self.host = host
        self.ws = websocket.WebSocket()

    def connect(self, burl):
        start_time = time.time()
        try:
            self.conn = self.ws.connect(url=burl)
        except websocket.WebSocketTimeoutException as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type="websockt", name='urlweb', response_time=total_time, exception=e)
        else:
            total_time = int((time.time() - start_time) * 1000)
            events.request_success.fire(request_type="websockt", name='urlweb', response_time=total_time, response_length=0)
        return self.conn

    def recv(self):
        return self.ws.recv()

    def send(self, msg):
        self.ws.send(msg)


class MyTask(TaskSet):
    def on_start(self):
        print("********** 测试开始 **********")
   
    def on_stop(self):
        print("********** 测试结束 **********")

    @task
    async def task(self):
        try:    
            chat_test()
            print("成功")
        except Exception as e:
            print("失败",e)
            

class OPlogin(HttpUser):
    tasks = [MyTask]				# 要执行的任务
    host = "http://127.0.0.1:8000"   # 被测网站域名
    wait_time = between(1,3)			# 请求间隔时间
