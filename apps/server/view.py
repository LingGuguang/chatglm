from fastapi import Query, Body, WebSocket
from pydantic import BaseModel
from enum import Enum
from typing import List, Union, Dict, Literal
from typing_extensions import Annotated
import json


from collections import defaultdict
from fastapi import APIRouter
from starlette.websockets import WebSocketDisconnect
from .utils import Request, request, stream_request
from model import Qwen
import time, asyncio
# from ...main import llm
from sse_starlette.sse import EventSourceResponse

EventSourceResponse.DEFAULT_PING_INTERVAL = 1000
router = APIRouter(prefix="/chat")

llm = Qwen()

class BasicMessage(BaseModel):
    role: Literal['user', 'assistant']
    content: str = None

class CompletionRequestMessages(BaseModel):
    messages: List[BasicMessage]
    stream: bool = False

class CompletionResponseMessages(BaseModel):
    messages: List[BasicMessage]
    response: Union[BasicMessage] 
    # finish_reason: Literal['stop']
    finish: bool



@router.post('/zhipu')
async def chat(inp: str, exp_seconds: Annotated[int, Query()]=10):
    
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    params = {
        "model": "glm-3-turbo",
        "messages": [
            {
                "role": "user",
                "content": inp
            }
        ],
        "stream": False
    }
    response = await request(url, params, exp_seconds)

    return response.get('choices')[0].get('message').get('content')



@router.websocket('/zhipu')
async def stream_chat(websocket: WebSocket):
    try:
        await websocket.accept() 
        messages = list() # 存储记忆 
        while True:
            data = await websocket.receive_text()
            if data == "quit":
                await websocket.close()
                break 
            if data == 'clear':
                messages = list()
                continue
            messages.append({"role":"user", "content": data})
            url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            params = {
                "model": "glm-3-turbo",
                "messages": messages,
                "stream": True
            }
            result = defaultdict(str)
            async for line in stream_request(url, params):
                role = line.get('role')
                content = line.get('content')
                if role:
                    result['role'] = role 
                if content:
                    await websocket.send_text(content)
                    result['content'] += content
            messages.append(dict(result))
    except WebSocketDisconnect:
        return
        
    
@router.post('/local')
async def chat(data: CompletionRequestMessages):
    # print('post data:', type(data), data)

    global llm 
    if not data.stream:
        response = llm.chat(data.messages)
        print('chat response:', response)
        return response
    
    response = llm.stream_chat(data.messages)
    return EventSourceResponse(response, media_type="text/event-stream")
    

@router.websocket('/local')
async def stream_chat(websocket: WebSocket):
    global llm
    try:
        await websocket.accept() 
        messages = list()
        while True:
            data = await websocket.receive_text()
            print('data:', data)
            messages += [{'role':'user', 'content': data}]
            if data == "quit":
                await websocket.close()
                break
            if data == 'clear':
                messages = list()
                continue

            response_buffer = ''
            for response in llm.stream_chat(messages):
                # print('response:', response)
                if response in [None, '']:
                    continue
                response_buffer += response
                response = wrapper_response(messages, response)

                await websocket.send_json(response)
                # await asyncio.sleep(0.05)
            stop = wrapper_response()
            await websocket.send_json(stop)
            messages += [{'role': 'assistant', 'content': response_buffer}]
    except WebSocketDisconnect:
        return
    
def wrapper_response(messages=None, response=None):
    if messages and response:
        response = {
            'role': 'assistant',
            'content': response 
        }
        response = {
            'messages': messages,
            'response': response,
            'finish': False
        }
        return response
    else:
        response = {
            'messages': None,
            'response': None,
            'finish': True
        }
        return response

if __name__ == "__main__":
    asyncio.run()