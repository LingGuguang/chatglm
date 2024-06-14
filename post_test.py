import requests, json

data = {
        'messages':[{
            'role': 'user',
            'content': '1+1=?'
        }]
    }
json_data = json.dumps(data)
headers = {"Content-Type": "application/json"}
url = 'http://127.0.0.1:8000/chat/local'
response = requests.post(url=url,data=json_data, headers=headers)
print("post_test:",response.status_code)