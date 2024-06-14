
import gradio as gr 
import json, os, time, jwt
from httpx import AsyncClient

from .utils import *



def get_gradio():
    with gr.Blocks() as gr_app:
        gr.HTML("""<h1 align="center">LLM Gradio Simple Demo</h1>""")
        chatbot = gr.Chatbot()

        with gr.Row():
            with gr.Column(scale=4):
                with gr.Column(scale=12):
                    user_input = gr.Textbox(show_label=False, placeholder="Input...", lines=10, container=False)
                with gr.Column(min_width=32, scale=1):
                    submitBtn = gr.Button("Submit")
            with gr.Column(scale=1):
                emptyBtn = gr.Button("Clear History")
                max_length = gr.Slider(0, 32768, value=8192, step=1.0, label="Maximum length", interactive=True)
                top_p = gr.Slider(0, 1, value=0.8, step=0.01, label="Top P", interactive=True)
                temperature = gr.Slider(0.01, 1, value=0.6, step=0.01, label="Temperature", interactive=True)


        def user(query, history):
            return "", history + [[parse_text(query), ""]]


        submitBtn.click(user, [user_input, chatbot], [user_input, chatbot], queue=False).then(
            stream_chat, [chatbot, max_length, top_p, temperature], chatbot
        )
        emptyBtn.click(lambda: None, None, chatbot, queue=False)
    gr_app.queue()
    return gr_app