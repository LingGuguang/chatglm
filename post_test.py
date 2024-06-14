import requests, json
from typing import List, Union, Dict, Any, AsyncIterable
from httpx import AsyncClient
from collections import defaultdict
import asyncio

params = {
        'messages':[{
            'role': 'user',
            'content': 'write a 100 words novel'
        }],
        'stream': True
    }
params = json.dumps(params)

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
                print('async:', data)
                yield data


async def chat(params):
    async for line in stream_request(params): #stream_request直接把params发给服务器，然后得到返回。
        print('return:', line)

asyncio.run(chat(params))