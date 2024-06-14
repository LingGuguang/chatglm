from fastapi import FastAPI
import os 
import dotenv 
from contextlib import asynccontextmanager

from apps.server import router as server_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

import gradio as gr 
from apps.gradio import get_gradio



@asynccontextmanager
async def lifespan(app: FastAPI):
    # yield之前是程序执行之前的工作
    app.state.api_key = os.getenv("API_KEY")
    yield 
    app.state.api_key = None


fs_app = FastAPI(lifespan=lifespan)
fs_app.include_router(server_router)

dotenv.load_dotenv(dotenv_path=dotenv.find_dotenv(), verbose=True)

fs_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
fs_app.mount("/static", StaticFiles(directory="static"), name="static")

@fs_app.get("/")
async def redirect_to_html():
    # 重定向到静态文件夹中的 HTML 文件
    return RedirectResponse(url="/static/index.html")

# gradio
gr_app = get_gradio()

GR_PATH = "/gradio"
app = gr.mount_gradio_app(fs_app, gr_app, path=GR_PATH)
# app.launch(server_name="127.0.0.1", server_port=7870, inbrowser=True, share=False)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host='127.0.0.1', port=8000)