

from fastapi import APIRouter, HTTPException, Query
import re, requests, json

from comm.logger import logger
from . import Picture_recognition as pic
from pydantic import BaseModel
from config import Config
"""

"""



router = APIRouter(prefix="/Transaction",tags=['Transaction'],responses={405: {"description": "Not found"}},)


class userInfo(BaseModel):
    userId:str
    agentId:str = ''
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
async def SetMapping(
    userId: str = Query(...),
    agentId: str = Query(''),
    token: str = Query(''),
    brokeId: str = Query(...),
    sitePlanId: str = Query(...),
    filepath: str = Query(...),
):
    logger.info('开始识别图片表格=======>')
    """
    图片表格识别
    """
    try:
        logger.info('开始识别图片表格=======>')
        # 判断图片地址是否是网络地址 如果不是 则拼接默认图片域名
        _filepath = filepath
        if not re.match(r'^https?://', _filepath):  # 判断是否是网络地址
            logger.info('图片地址非网络地址，拼接默认图片域名')
            _filepath = Config.imgpath + _filepath

        # 识别图片表格
        content = pic.Picture_table_recognition(_filepath)
        logger.info('图片表格识别完成=======>')
        # 推送到服务器（与旧版保持一致：json.dumps序列化）
        content_str = json.dumps(content, ensure_ascii=False)
        # 3. 构建提交数据（push_siteplan 继承 userInfo，包含 userId/token/brokeId）
        push_data = push_siteplan(
            userId=userId, agentId=agentId, token=token, brokeId=brokeId,
            sitePlanId=sitePlanId, content=content_str
        )
        # logger.info('提交内容开始=======>{0}'.format(push_data))
        # 4. 签名加密
        signed_data = pic.set_signature(push_data.model_dump())
        # 5. 提交到服务器（form表单格式）
        # Push_Url = "https://api.singmap.com/manager-service/siteplan/updateSiteContent"
        Push_Url =  Config.API_IP + "/manager-service/siteplan/updateSiteContent"
        ret = requests.post(Push_Url, data=signed_data)
        # print(f"POST响应状态码: {ret.status_code}")
        # print(f"POST响应内容: {ret.text}")
        if ret.status_code == 200:
            logger.info('图片表格识别完成=======>')
            return {
                'code':'0',
                'msg':'success',
                "datas":""
            }
        else:
            logger.error('图片表格识别失败=======>')
            return {
                'code':'-1',
                'msg':'error',
                "datas":ret.text
            }

    except BaseException as e:
        rtdata = {
            'code':'-1',
            'msg':'error',
            "datas":e
            }
        return rtdata





class Contract(BaseModel):
    # 买家信息
    BuyerName1: str = '' # 买家姓名
    BuyerName2: str = ''
    BuyerName3: str = ''
    BuyerName4: str = ''
    BuyerName5: str = ''
    BuyerId1: str = '' # 买家身份证号
    BuyerId2: str = ''
    BuyerId3: str = ''
    BuyerId4: str = ''
    BuyerId5: str = ''
    BuyerNationality1: str = '' # 买家国籍
    BuyerNationality2: str = ''
    BuyerNationality3: str = ''
    BuyerNationality4: str = ''
    BuyerNationality5: str = ''
    BuyerAddress1: str = '' # 买家地址
    BuyerAddress2: str = ''
    BuyerAddress3: str = ''
    BuyerAddress4: str = ''
    BuyerAddress5: str = ''
    BuyerBusinessNumber1: str = '' # 买家商业登记号码
    BuyerBusinessNumber2: str = ''
    BuyerBusinessNumber3: str = ''
    BuyerBusinessNumber4: str = ''
    BuyerBusinessNumber5: str = ''
    BuyerOccupation1: str = '' # 买家职业
    BuyerOccupation2: str = ''
    BuyerOccupation3: str = ''
    BuyerOccupation4: str = ''
    BuyerOccupation5: str = ''
    # 合同信息
    signData: str = '' # 签署日期
    signPlace: str = '' # 签署地点
    contractNumber: str = '' # 合同编号
    contractName: str = '' # 合同名称
    contractType: str = '' # 合同类型
    # 律师信息
    lawyerName: str = '' # 律师姓名
    lawyerId: str = '' # 律师身份证号
    lawyerNationality: str = '' # 律师国籍
    lawyerAddress: str = '' # 律师地址
    lawyerBusinessNumber: str = '' # 律师商业登记号码
    LawyerEmail: str = '' # 律师邮箱
    # 房产信息
    projectName: str = '' # 房产项目名称
    projectAddress: str = '' # 房产项目地址
    buildingName: str = '' # 房产楼栋名称
    buildingNumber: str = '' # 房产楼栋编号
    unitName: str = '' # 房产单元名称
    unitType: str = '' # 房产户型
    unitArea: str = '' # 房产面积
    unitPrice: str = '' # 房产单价
    totalPrice: str = '' # 房产总价
    brokerage: str = '' # 中介费
    brokerageRate: str = '' # 中介费率
    paymentMethod: str = '' # 付款方式
    paymentSchedule: str = '' # 付款时间表
    paymentAmount: str = '' # 付款金额
    paymentDate: str = '' # 付款日期
    
class Document(BaseModel):
    # 合同内容填充参数
    userId: str = ''
    token: str = ''
    brokeId: str
    documentId: str
    TmpPath: str
    docPath: str = ''  # 临时文件路径
    Content: Contract




# 合同内容动态填充
@router.get('/contract')
def Contract_Content(data: Document):
    """
    合同内容动态填充
    """
    try:
        # print(data)
        # print(data.model_dump())
        content = pic.Contract_Content(data.model_dump())
        content = re.sub("'", '"', '%s' % content)  # 将单引号换成双引号
        content = re.sub("\n", '', '%s' % content)  # 去除换行符
        return content
    except BaseException as e:
        logger.error('合同内容填充失败=====>{0}'.format(e))
        raise HTTPException(status_code=404, detail="Contract Content Error")




# #  多字段替换工具
# from typing import Dict, List, Optional,Callable
# class ReMultiReplacer:
#     """基于re模块的多字段替换工具，支持占位符格式和字段排除"""
    
#     def __init__(self, placeholder_pattern: str = r'{{\s*(\w+)\s*}}'):
#         """
#         初始化替换器
#         :param placeholder_pattern: 占位符正则模式，默认为{{field}}格式
#         """
#         self.pattern = re.compile(placeholder_pattern)
    
#     def replace(self, 
#                 text: str, 
#                 data: Dict[str, str], 
#                 exclude_fields: List[str] = None,
#                 missing_handler: Callable  = None ) -> str:
#         """
#         替换文本中的多个字段
#         :param text: 原始文本
#         :param data: 替换数据字典 {字段名: 替换值}
#         :param exclude_fields: 需要排除的字段列表
#         :param missing_handler: 处理缺失字段的函数，默认保留原始占位符
#         :return: 替换后的文本
#         """
#         exclude_fields = exclude_fields or []
        
#         def _replace_match(match):
#             # 获取匹配到的字段名（如从{{company}}中提取company）
#             field = match.group(1)
            
#             # 处理排除字段
#             if field in exclude_fields:
#                 return match.group(0)  # 返回原始占位符
            
#             # 处理存在的字段
#             if field in data:
#                 return str(data[field])
            
#             # 处理缺失的字段
#             if missing_handler:
#                 return missing_handler(field, match.group(0))
#             return match.group(0)  # 默认保留原始占位符
        
#         return self.pattern.sub(_replace_match, text)

# # text = "客户：{{customer_name}}（等级：{{customer_level}}），缺失：{{customer_level1}}"
# # replacer = ReMultiReplacer()
# # data = {"customer_level": "A","customer_name":"444"} 
# # exclude_fields = ["customer_level"]
# # def missing_handler(field, placeholder):
# #     return f"{placeholder}（未定义）"

# # result2 = replacer.replace(text, data, exclude_fields,missing_handler)










