import requests, json
from typing import List, Union, Dict, Any, AsyncIterable
from httpx import AsyncClient
from collections import defaultdict
import asyncio
from time import time

params = {
        'messages':[{
            'role': 'user',
            'content': '你好'
        }],
        'stream': True
    }
# params = json.dumps(params)
# print(type(params))

url = 'http://127.0.0.1:8000/chat/local'
headers = {"Content-Type": "application/json"}

async def stream_request(params):
    async with AsyncClient() as client:
        async with client.stream("POST", url=url, headers=headers, json=params, timeout=60) as response:
            # 做一个stream结尾判断
            async for line in response.aiter_lines():
                if not line.strip():
                    #当前有输出就继续，否则跳过
                    continue 
                data = line.replace("data: ", "")
                yield data

async def chat(params):
    start = time()
    count = 0
    async for line in stream_request(params): #stream_request直接把params发给服务器，然后得到返回。
        print(line, end='', flush=True)
        count += len(line)
    end = time()
    print(f'    speed:{round(count/(end-start), 2)} it/s | token: {count} | sec: {end-start}')

asyncio.run(chat(params))