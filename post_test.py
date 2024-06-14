import requests, json

data = {
        'messages':[{
            'role': 'user',
            'content': '写一个一百字小作文'
        }],
        'stream': True
    }
json_data = json.dumps(data)
headers = {"Content-Type": "application/json"}
url = 'http://127.0.0.1:8000/chat/local'
response = requests.post(url=url,data=json_data, headers=headers)
print("status_code:",response.status_code)
print("response:", response.text)
