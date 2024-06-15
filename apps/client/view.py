from httpx import AsyncClient
import requests, websockets, json


headers = {"Content-Type": "application/json"}
query = "你是谁"
params = {
        'messages':[{
            'role': 'user',
            'content': query
        }],
        'stream': True
    }
host = "127.0.0.1"
port = '8000'

async def stream_chat():
    global headers, params, host, port
    url = 'http://' + host + ':' + port + '/chat/local/stream_chat'
    async with AsyncClient() as client:
        async with client.stream("POST", url=url, headers=headers, json=params, timeout=60) as response:
            async for line in response.aiter_lines():
                if not line.strip():
                    #当前有输出就继续，否则跳过
                    continue 
                response = line.replace("data: ", "")
                yield response


async def chat():
    global headers, params, host, port
    url = 'http:/' + host + ':' + port + '/chat/local/chat'
    async with AsyncClient(timeout=100) as client:
        response = await client.post(url, headers=headers, json=params)
    try:
        assert response.status_code == 200
        response = response.get('response').get('content')
        return response
    except Exception:
        return f"http error: code {response.status_code}"



async def websocket_chat():
    global headers, params, host, port
    url = 'ws://' + host + ':' + port + '/chat/local/websocket_chat'
    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps(params))
        while True:
            response = await websocket.recv()
            # print(type(stream_response))
            response = json.loads(response)
            if response.get('finish'):
                await websocket.close()
                break
            yield  response.get('response').get('content')

