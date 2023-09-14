

from fastapi import APIRouter,Form,HTTPException,Request
import re,copy,requests,json,os,configparser,time

from comm.logger import logger
from . import Picture_recognition as pic
from pydantic import BaseModel
"""

"""



router = APIRouter(prefix="/Transaction",tags=['Transaction'],responses={405: {"description": "Not found"}},)


class userInfo(BaseModel):
    userId:str
    token:str = ''
    brokeId:str

class get_siteplan(userInfo):
    sitePlanId:str
    filepath:str


class push_siteplan(userInfo):
    # 提交自动画图信息。
    sitePlanId:str
    content:str

@router.get('/mapping')
async def SetMapping(data: get_siteplan):


    try:
        print(0)

        content = pic.Picture_table_recognition(data.filepath)

        # 推送到服务器
        content = re.sub("'", '"', '%s' % content)  # 将单引号换成双引号
        content = re.sub("\n", '', '%s' % content)  # 去除换行符

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        Push_Url = "/broke-manager-service/siteplan/updateSiteContent"
        content = push_siteplan(**data.dict(),content=content)
        return pic.set_signature(content.dict())

        # ret = requests.post(Push_Url, data=pic.set_signature(content.dict()))
        # logger.info('提交内容成功=======>')
        # return ret.json()
    except BaseException as e:
        rtdata = {
            'code':'-1',
            'msg':'error',
            "datas":e
            }
        return rtdata


































