from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TextIteratorStreamer, TextStreamer 
import torch, os, sys 
from typing import List, Dict, Tuple, Union
from enum import Enum
from threading import Thread

class Role(Enum):
    system = 'system'
    user = 'user'
    assistant = 'assistant'
    content = 'content'



class basicLLMInfo:
    abs_path: str = os.path.dirname(os.path.abspath(__file__))
    device: str = "cuda" if torch.cuda.is_available() else 'cpu'
    # messages: List[Dict[Role, str]] = [{"role": "system", "content": "You are a helpful assistant."}]


class Qwen(basicLLMInfo):
    

    running: bool = False

    def __init__(self, model_name: str="Qwen1.5-1.8B-Chat"):
        model_path = os.path.join(self.abs_path, model_name)
        bnb_config = BitsAndBytesConfig(
            load_in_8bit=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto",
            quantization_config=bnb_config
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
        self.count = 0

    def isrunning(self):
        return self.running

    def _on(self):
        print(f'+++++++++ 推理中 {self.count} ++++++++++\n\n\n')
        self.running = True
    
    def _off(self):
        print(f'+++++++++ 推理结束{self.count} ++++++++++\n\n\n')
        self.count += 1
        self.running = False

    def chat(self, query: List[Dict[Role, str]]):
        self._on()
        
        messages = self._messages(query)

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

        generated_ids = self.model.generate(
            model_inputs.input_ids,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        self._off()
        return response 
    
    def stream_chat(self, query: List[Dict[Role, str]]):
        messages = self._messages(query)

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

        generation_kwargs = dict(model_inputs, streamer=self.streamer, max_new_tokens=512)

        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)

        thread.start()
        return self.streamer 
    
    def _messages(self, query):
        messages = [{'role':'system', 'content':'you are a helpful ai chatbot'}]
        # messages = []

        messages += query 
        return messages



if __name__ == "__main__":
    llm = Qwen()
    while True:
        query = input("user:")
        print("response:", end='', flush=True)
        for response in llm.stream_chat(query):
            if response in [None, '']:
                continue
            print(response, end='', flush=True)
        print()

