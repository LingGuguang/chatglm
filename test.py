from fastapi import FastAPI
import gradio as gr
from fastapi.middleware.cors import CORSMiddleware

CUSTOM_PATH = "/gradio"
app = FastAPI()

@app.get("/")
def read_main():
    return {"message": "This is your main app"}

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

io = gr.Interface(lambda x: "Hello, " + x + "!", "textbox", "textbox")
app = gr.mount_gradio_app(app, io, path=CUSTOM_PATH)
