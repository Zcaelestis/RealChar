import os
import warnings

from dotenv import load_dotenv
#从fastapi的子模块导入处理跨域资源共享的中间件、用于处理静态文件的模块和几种不同的响应类
from fastapi import FastAPI, Request  # 从fastapi中导入FastAPI类和Request类
from fastapi.middleware.cors import CORSMiddleware # 从fastapi.middleware.cors中导入CORSMiddleware
from fastapi.staticfiles import StaticFiles # 从fastapi.staticfiles 中导入StaticFiles
from fastapi.responses import FileResponse, RedirectResponse # 从fastapi.responses中导入FileResponse,RedirectResponse
#从项目中的其他模块导入需要的类和函数
from realtime_ai_character.audio.speech_to_text import get_speech_to_text
from realtime_ai_character.audio.text_to_speech import get_text_to_speech
from realtime_ai_character.character_catalog.catalog_manager import CatalogManager
from realtime_ai_character.memory.memory_manager import MemoryManager
from realtime_ai_character.restful_routes import router as restful_router
from realtime_ai_character.utils import ConnectionManager
from realtime_ai_character.websocket_routes import router as websocket_router

load_dotenv() # 加载环境变量

app = FastAPI() # 创建FastAPI instance
# 设置跨域资源共享的middleware,增加了一些corsmiddleware,以允许跨域请求
app.add_middleware(
    CORSMiddleware,
    # Change to domains if you deploy this to production
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 将restful_router和websocket_router添加到app中
app.include_router(restful_router)
app.include_router(websocket_router)

web_build_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                              '..', 'client', 'web', 'build') # set the path to the web app build directory
# 如果web app已经构建,则将web app的静态文件添加到app中,serve the static files from the web app build directory
if os.path.exists(web_build_path):
    #在app中设置静态文件目录,将web app的静态文件目录挂载到/static/router
    app.mount("/static/", 
              StaticFiles(directory=os.path.join(web_build_path, 'static')),  
              name="static")                                             #mount the static files dictory to the /static/ route
    # 在app中设置router,返回index.html文件
    @app.get("/", response_class=FileResponse)                           #set the root route to return the index.html file
    async def read_index():
        return FileResponse(os.path.join(web_build_path, 'index.html'))  #返回index.html文件

    # 在app中设置catchall route at their endpoints                    
    @app.get("/{catchall:path}", response_class=FileResponse)            
    
    def read_static(request: Request):
        path = request.path_params["catchall"]
        file = os.path.join(web_build_path, path)
    #如果文件存在,返回文件
        if os.path.exists(file):
            return FileResponse(file)
        return RedirectResponse("/") 
else:
    # If the web app is not built, 404 page and prompt the user to build it
    static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    app.mount("/static/", StaticFiles(directory=static_path), name="static") 
   # 在app中设置router,返回404.html文件
    @app.get("/", response_class=FileResponse)
    async def read_index():
        return FileResponse(os.path.join(static_path, '404.html'))

# initializations: initialize the catalog, connection, and memory managers
overwrite_chroma = os.getenv("OVERWRITE_CHROMA", 'True').lower() in ('true', '1')
CatalogManager.initialize(overwrite=overwrite_chroma)
ConnectionManager.initialize()
MemoryManager.initialize() 
get_text_to_speech() # initialize the text to speech engine
get_speech_to_text() # initialize the speech to text engine
  
# suppress deprecation warnings from the whisper module
warnings.filterwarnings("ignore", module="whisper")
