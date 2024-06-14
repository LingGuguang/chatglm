
from pydantic import BaseModel, Field
from typing import List, Union, Dict, Any, AsyncIterable
from httpx import AsyncClient
import jwt, time, os, json
from typing_extensions import Annotated
from fastapi import Query

class Response(BaseModel):
    role: str
    content: str
    id: Union[int, None] = Field(default=None, description="返回的对话id")

class Request(BaseModel):
    role: str 
    content: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "role": "user",
                    "content": "早上好中国"
                }
            ]
        }
    }

def token_generator(exp_seconds:Annotated[int, Query()]) -> str:
    api_key = os.getenv("ZHIPUAI_API_KEY")
    try:
        id, secret = api_key.split(".")
    except Exception as e:
        raise Exception("invaild apikey", e)
    
    payload = {
        "api_key": id,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }
    token = jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )
    return token


async def request(url: str, params: Union[str, Dict[str, Any]], exp_seconds: int=10) -> Dict[str, Any]:
    token = token_generator(exp_seconds)    

    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    }

    async with AsyncClient() as client:
        response = await client.post(url=url, headers=headers, json=params)
        return response.json()
    

async def stream_request(url: str, params: Union[str, Dict[str, Any]], exp_seconds: int=10) -> AsyncIterable[Dict[str, Any]]:
    token = token_generator(exp_seconds)    

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    }

    async with AsyncClient() as client:
        async with client.stream("POST", url=url, headers=headers, json=params, timeout=60) as response:
            # 做一个stream结尾判断
            async for line in response.aiter_lines():
                if not line.strip():
                    #当前有输出就继续，否则跳过
                    continue 
                line = line.replace("data: ", "")
                try:
                    data = json.loads(line)
                except Exception:
                    data = {"choices":[{"finish_reason": "stop"}]}
                if data.get('choices')[0].get('finish_reason', None) is not None:
                    return 
                yield data.get('choices')[0].get('delta')



                