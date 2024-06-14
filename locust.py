# OPLogin.py文件
import re, json, jsonlines
from locust import HttpUser,task,TaskSet,constant,between
# openstack登录
class MyTask(TaskSet):
    # on_start/on_stop是前置和后置操作方法，与jmeter中的setup/teardown类似，开始前后执行一次
    def on_start(self):
        self.url = '/chat/local'

        def read_jsonl(path):
            ret = []
            with  jsonlines.open(path, 'r') as f:
                for line in f.iter():
                    ret.append(line)
            return ret 
        
        # self.questions = read_jsonl('datasets/zhihu.jsonl')
        # self.question_count = 0


        
    def on_stop(self):
        print("********** 测试结束 **********")

    @task	# @task装饰器的作用是将opLogin标记为可被调用的方法
    def opLogin(self):
        # 登录参数

        # q = self.questions[self.question_count]
        # self.question_count += 1

        data = {
                'messages':[{
                    'role': 'user',
                    # 'content': q['问'],
                    'content': "写一个三百字小作文，题目自拟"

                }],
                'stream': True
            }
        json_data = json.dumps(data)
        # 发送登录请求，url与on_start中的一样，直接调用
        response = self.client.request(method="post",url=self.url,data=json_data)
        print(response.text)
        try:    # 断言，判断响应文本中是否包含指定内容，包含则返回“成功”，否则返回“失败”并打印异常
            assert response.status_code == 200
            print("成功, 返回:", response.text)
        except Exception as e:
            print("失败",e)

class OPlogin(HttpUser):
    tasks = [MyTask]				# 要执行的任务
    host = "http://127.0.0.1:8000"   # 被测网站域名
    wait_time = between(1,3)			# 请求间隔时间
