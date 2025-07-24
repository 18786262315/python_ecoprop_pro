from typing import List
from fastapi import Depends, HTTPException,FastAPI,Form,Query,UploadFile,File,Request,Header,Cookie,WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse,HTMLResponse
# from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

# 前置处理
from comm.logger import logger
# from config import Config
# conf = Config
# 模块引入

# from sql import database,models
from modules import Project,Transaction


'''
虚拟环境切换： conda activate FastAPI
FastAPI 程序启动 :
uvicorn manger:app --port 7777 --reload
正式环境后台运行 无需其他的管理工具 :
nohup uvicorn manger:app --host 0.0.0.0 --port 7777 --reload  > /home/mixgo/project/python/logs/log.txt 2>&1 &


PDF 有个字体需要传入到 安装包下 /usr/local/python3/lib/python3.7/site-packages/reportlab/fonts
线上 字体位置 /usr/local/lib/python3.9/site-packages/reportlab/fonts
'''

# models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# app.include_router(Users.router)
# app.include_router(Company.router)
app.include_router(Transaction.router)
app.include_router(Project.router)


# 跨域问题
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://47.88.212.170",
    "http://localhost:8080",
    "http://192.168.0.116:8080",
    "http://localhost:8081",
    "http://192.168.0.116:8081",
    "http://192.168.0.114",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求中间件，请求前后内容处理。
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # logger.info(f"处理前")
        response = await call_next(request)
        # print(f"Request: {request.method} {request.url} from {request.client.host}:{request.client.port} {request.body}")
        # logger.info(f"请求111{request.method} {request.url} from {request.client.host}:{request.client.port}")
        # 记录响应内容
        # if isinstance(response, StreamingResponse):
            # 对于流式响应，无法直接读取内容，所以这里可以记录其他信息
            # logger.info(f"请求111{request.method} {request.url} from {request.client.host}:{request.client.port}")
            # print(f"StreamingResponse: {response.media_type}, Status Code: {response.status_code}")
        # else:
            # 对于普通响应，可以直接获取内容
            # logger.info(f"请求222")
            # print(f"Response: {response.body}, Status Code: {response.status_code}")
        
        return response

# app.add_middleware(LoggingMiddleware)

# 参数检测
@app.exception_handler(RequestValidationError) 
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    # logger.info(f"{request.method} {request.url}")
    # logger.error(f"参数错误{request.method} {request.url}") # 记录请求信息,方便排错
    return JSONResponse({"code": "400", "message": exc.errors()})

# Dependency
# def get_db():
#     try:
#         db = database.SessionLocal()
#         yield db
#     finally:
#         db.close()



@app.get("/")
async def main():

    return 0






