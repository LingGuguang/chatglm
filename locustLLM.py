# OPLogin.py文件
import re, json, jsonlines
from locust import HttpUser,task,TaskSet,constant,between
import asyncio
from httpx import AsyncClient
import requests


# def read_jsonl(path):
#     ret = []
#     with  jsonlines.open(path, 'r') as f:
#         for line in f.iter():
#             ret.append(line)
#     return ret 
# questions = read_jsonl('datasets/zhihu.jsonl')

# openstack登录
class MyTask(TaskSet):
    # on_start/on_stop是前置和后置操作方法，与jmeter中的setup/teardown类似，开始前后执行一次
    def on_start(self):
        self.url = '/chat/local'
        self.headers = {"Content-Type": "application/json"}
   
    def on_stop(self):
        print("********** 测试结束 **********")
    
    async def stream_request(self, params):
        url = 'http://127.0.0.1:8000/chat/local'
        headers = {"Content-Type": "application/json"}
        async with AsyncClient() as client:
            async with client.stream("POST", url=url, headers=headers, json=params, timeout=60) as response:
                # 做一个stream结尾判断
                async for line in response.aiter_lines():
                    if not line.strip():
                        #当前有输出就继续，否则跳过
                        continue 
                    data = line.replace("data: ", "")
                    yield data

    async def async_chat(self, params):
        async for line in self.stream_request(params): #stream_request直接把params发给服务器，然后得到返回。
            print(line, end='', flush=True)

    def chat(self, params):
        url = 'http://127.0.0.1:8000/chat/local'
        headers = {"Content-Type": "application/json"}
        # response = requests.post(url=url, headers=headers,json=params)
        response = self.client.post(url=url, headers=headers,json=params)
        text = response.text 
        text = text.replace('data: ', '').split('\r\n\r\n')
        text = [t.strip() for t in text]
        text = ''.join(text)
        print(text)
        # for r in response.text:
        #     # r = binary.decode('utf-8')
        #     # r = r.replace("data: ", "").replace('\r\n\r\n', '').strip()
        #     if not r:
        #         #当前有输出就继续，否则跳过
        #         print('空|',r,'|')
        #     else:
        #         # print('binary:',binary,'|', flush=True)
        #         print(r, end='\n', flush=True)
        print('\n','+'*30,'\n')
        return response

    @task
    def chat_task(self):
        params = {
                'messages':[{
                    'role': 'user',
                    # 'content': q['问'],
                    'content': "你好"

                }],
                'stream': True
            }
        # 发送登录请求，url与on_start中的一样，直接调用
        try:    # 断言，判断响应文本中是否包含指定内容，包含则返回“成功”，否则返回“失败”并打印异常
            # loop = asyncio.new_event_loop()
            # loop.create_task(self.async_chat(params))
            response = self.chat(params)
            assert response.status_code==200
            # await task
            print("成功")
        except Exception as e:
            print("失败",e)
            

class OPlogin(HttpUser):
    tasks = [MyTask]				# 要执行的任务
    host = "http://127.0.0.1:8000"   # 被测网站域名
    wait_time = between(1,3)			# 请求间隔时间
