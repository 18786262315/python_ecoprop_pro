
from fastapi import APIRouter,Depends,Header,HTTPException,Form,Body
from comm.logger import logger
from config import Config
from typing import Optional, List
from pydantic import BaseModel
from .comm import WordTemplateFiller,HtmlTemplateFiller

router = APIRouter(prefix="/temp",tags=['temp'],responses={405: {"description": "Not found"}},)


class Person(BaseModel):
    tmp_path: str
    doc_path: str
    excluded_fields: Optional[List[str]] = []
    data: Optional[dict] = {}


@router.post("/word_to_pdf")
def word_to_pdf( Data: Person):
    if not Data.tmp_path: return {"code": 400, "msg": "请上传模板文件"}
    if not Data.doc_path: return {"code": 400, "msg": "请上传生成文件路径"}
    if not Data.data: return {"code": 400, "msg": "请上传填充数据"}
    logger.info(f'Temp Word to PDF Data ====>>>>{Data}')
    word_filler = WordTemplateFiller(Data.tmp_path)
    word_filler.fill(Data.data, Data.excluded_fields)
    word_filler.save_pdf(Data.doc_path)
    logger.info("Word模板填充完成")
    return {"code": 200, "msg": "Word模板填充完成", "data": Data.doc_path}


@router.post("/word_to_word")
def word_to_word( Data: Person):
    logger.info(f'Temp Word to PDF Data ====>>>>{Data}')
    word_filler = WordTemplateFiller(Data.tmp_path)
    word_filler.fill(Data.data, Data.excluded_fields)
    word_filler.save(Data.doc_path)
    logger.info("Word模板填充完成")
    return "word_to_pdf"

@router.post("/html_to_pdf")
def html_to_pdf( Data: Person):
    logger.info(f'Temp Word to PDF Data ====>>>>{Data}')
    word_filler = HtmlTemplateFiller(Data.tmp_path,use_jinja2=True)
    word_filler.fill(Data.data, Data.excluded_fields)
    word_filler.save_pdf(Data.doc_path)
    logger.info("Word模板填充完成")
    return "word_to_pdf"