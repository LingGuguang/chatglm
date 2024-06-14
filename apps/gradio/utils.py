import json, os, time, jwt
from httpx import AsyncClient


def token_generator(exp_seconds: int) -> str:
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


async def stream_chat(history, max_length, top_p, temperature):
    messages = []
    for idx, (user_msg, model_msg) in enumerate(history):
        if idx == len(history) - 1 and not model_msg:
            messages.append({"role": "user", "content": user_msg})
            break
        if user_msg:
            messages.append({"role": "user", "content": user_msg})
        if model_msg:
            messages.append({"role": "assistant", "content": model_msg})

    token = token_generator(exp_seconds=10)    

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    }

    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    params = {
        "model": "glm-3-turbo",
        "messages": messages,
        "stream": True,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_length
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
                line = data.get('choices')[0].get('delta')
                
                new_token = line.get('content')
                if new_token != '':
                    history[-1][1] += new_token
                    yield history




def parse_text(text):
    lines = text.split("\n")
    lines = [line for line in lines if line != ""]
    count = 0
    for i, line in enumerate(lines):
        if "```" in line:
            count += 1
            items = line.split('`')
            if count % 2 == 1:
                lines[i] = f'<pre><code class="language-{items[-1]}">'
            else:
                lines[i] = f'<br></code></pre>'
        else:
            if i > 0:
                if count % 2 == 1:
                    line = line.replace("`", "\`")
                    line = line.replace("<", "&lt;")
                    line = line.replace(">", "&gt;")
                    line = line.replace(" ", "&nbsp;")
                    line = line.replace("*", "&ast;")
                    line = line.replace("_", "&lowbar;")
                    line = line.replace("-", "&#45;")
                    line = line.replace(".", "&#46;")
                    line = line.replace("!", "&#33;")
                    line = line.replace("(", "&#40;")
                    line = line.replace(")", "&#41;")
                    line = line.replace("$", "&#36;")
                lines[i] = "<br>" + line
    text = "".join(lines)
    return text