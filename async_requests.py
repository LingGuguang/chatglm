import requests, json
from typing import List, Union, Dict, Any, AsyncIterable
from httpx import AsyncClient
from collections import defaultdict
import asyncio
from time import time
import argparse 
import websockets

parser = argparse.ArgumentParser()
parser.add_argument('--u', type=int, default=8)
parser.add_argument('--q', type=str, default='你是谁')
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

url = 'http://127.0.0.1:8000/chat/local'
uri = 'ws://127.0.0.1:8000/chat/local'
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

async def chat():
    start = time()
    response = ''
    async for line in stream_request(params): #stream_request直接把params发给服务器，然后得到返回。
        response += line
    
    count = len(response)
    end = time()
    speed = round(count/(end-start), 2)
    subtime = end-start
    print(f'{response} | speed:{speed} it/s | token: {count} | sec: {subtime}')
    return count, subtime


async def websocket_chat():
    start_time = time()
    response = ''
    async with websockets.connect(uri) as websocket:
        await websocket.send(args.q)
        while True:
            stream_response = await websocket.recv()
            # print(type(stream_response))
            stream_response = json.loads(stream_response)
            if stream_response.get('finish'):
                websocket.close()
                break
            stream_response = stream_response.get('response').get('content')
            # print(stream_response)
            response += stream_response

    end_time = time()
    num_token = len(response)
    subtime = end_time - start_time
    # print(f'{response} | token count: {num_token} | time: {subtime} ')
    return num_token, subtime


async def main():
    tasks = [chat() for _ in range(args.u)]
    info = await asyncio.gather(*tasks)
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

async def gather_websocket_chat():
    tasks = [websocket_chat() for _ in range(args.u)]
    info = await asyncio.gather(*tasks)
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
    # print(f'Average latency per output token:{avg_latency_per_token} s/token ')
    print(f'Average latency per output token:{avg_latency_per_output_token} s/token')

# asyncio.run(main())
    
asyncio.run(gather_websocket_chat())
    