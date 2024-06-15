import requests, json
from typing import List, Union, Dict, Any, AsyncIterable
from httpx import AsyncClient
from collections import defaultdict
import asyncio
from time import time
import argparse 
import websockets

parser = argparse.ArgumentParser()
parser.add_argument('--u', type=int, default=1)
parser.add_argument('--q', type=str, default='你是谁')
parser.add_argument('--test', type=str, default='chat')
args = parser.parse_args()

params = {
        'messages':[{
            'role': 'user',
            'content': args.q
        }],
        'stream': True
    }
# params = json.dumps(params)
# print(type(params))

headers = {"Content-Type": "application/json"}

def wrapper(func):
    async def wrapper(*args, **kwargs):
        start_time = time()
        response = await func(*args, **kwargs)
        print(response)
        num_token = len(response)
        end_time = time()
        subtime = end_time-start_time
        return num_token, subtime
    return wrapper

@wrapper
async def stream_chat():
    async def post_stream_chat():
        global headers, params
        url = 'http://127.0.0.1:8000/chat/local/stream_chat'
        async with AsyncClient() as client:
            async with client.stream("POST", url=url, headers=headers, json=params, timeout=60) as response:
                async for line in response.aiter_lines():
                    if not line.strip():
                        #当前有输出就继续，否则跳过
                        continue 
                    data = line.replace("data: ", "")
                    yield data
    
    response = ''
    async for line in post_stream_chat(): #stream_request直接把params发给服务器，然后得到返回。
        response += line
    return response

@wrapper
async def chat():
    global headers, params
    url = 'http://127.0.0.1:8000/chat/local/chat'
    async with AsyncClient(timeout=10000) as client:
        response = await client.post(url, headers=headers, json=params)
    response = json.loads(response.text)
    response = response.get('response').get('content')
    return response

@wrapper
async def websocket_chat():
    global headers, params
    url = "ws://127.0.0.1:8000/chat/local/websocket_chat"
    response = ''
    async with websockets.connect(url) as websocket:
        await websocket.send(args.q)
        while True:
            stream_response = await websocket.recv()
            # print(type(stream_response))
            stream_response = json.loads(stream_response)
            if stream_response.get('finish'):
                await websocket.close()
                break
            stream_response = stream_response.get('response').get('content')
            # print(stream_response)
            response += stream_response
    return response

async def func_test(func: Union[Any, List[Any]]):
    if isinstance(func, list):
        tasks = [f() for f in func]
    else:
        tasks = [func() for _ in range(args.u)]
    info = await asyncio.gather(*tasks)
    show_info(info)

def show_info(info):
    token_count = 0
    max_time = 0
    latency = 0
    for count, subtime in info:
        token_count += count 
        max_time = max(max_time, subtime)
        latency += subtime
    avg_latency = round(latency/args.u, 3)
    throughtput = round(args.u/max_time, 3)
    flops = round(token_count/max_time, 2)
    avg_latency_per_output_token = round(latency/token_count, 2)
    print(f'TOTAL TIME: {max_time}')
    print(f'FLOPS:{flops} t/s')
    print(f'Throughtput: {throughtput} request/s')
    print(f'Average latency:{avg_latency} s ')
    # print(f'Average latency per token:{avg_latency_per_token} s/token ')
    print(f'Average latency per output token:{avg_latency_per_output_token} s/token')

async def chat_test():
    await func_test(chat)

async def stream_chat_test():
    await func_test(stream_chat)

async def websocket_chat_test():
    await func_test(websocket_chat)

async def test_all():
    await func_test(chat)
    await func_test(stream_chat)
    await func_test(websocket_chat)


# asyncio.run(main())
if args.test == 'websocket_chat':
    func = websocket_chat_test
if args.test == 'chat':
    func = chat_test
if args.test == 'stream_chat':
    func = stream_chat_test
if args.test == 'test':
    func = test_all

print(f"testing {func.__name__} ......")
asyncio.run(func())
        