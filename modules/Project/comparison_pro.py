
from comm.logger import logger
from .comm import MakeReportlab,getAPI,getDatetimes
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
# from reportlab.pdfgen import canvas
# from reportlab.platypus import Table,Paragraph
from reportlab.lib.units import cm
# from reportlab.lib import colors
# from reportlab.lib.colors import HexColor
# from reportlab.lib.styles import getSampleStyleSheet
import os,re
from fastapi import APIRouter,Form,HTTPException,Body
import json,time,datetime
import jinja2,pdfkit,base64
from config import Config


gettime = getDatetimes()

def priceFormat(price):
    price_str = str(int(price))
    if len(price_str) > 6 :
        newPrice = str(round(price / 1000000,2))+"M"
    elif len(price_str) > 3 and len(price_str) <=6:
        newPrice = str(round(price / 1000,2))+"K"
    else:
        newPrice = str(price_str)
    return newPrice


def XHORIZON_Comparison_PDF(agentId,projectId):
    # XHORIZON 公司项目对比 PDF
    # 创建 项目对比PDF文件
    getapi = getAPI()
    datas = {
        "imgpath":Config.imgpath,
        "userInfo":None
    } 
    # agentId = "e73ca86d287143709c1450012bac9e9a"
    # projectId = "5b2216e95ef446bf853113450a0642f1,0c3cef5e77f547a99d61d6a2ccd37885"
    datas['userInfo'] = getapi.requsetAPI(Config.now_host+'/app-service/agent/queryShareAgentInfo',params={"agentId": agentId})
    logger.info('get User Info ====>>>>{0}',format(datas['userInfo']))

    UnitIdList = projectId.split(',')
    datas['pro_list'] = []
    no_room = 1
    proinfourl = Config.urlpath+"/app-service/other/queryProjectInfoByComparison"
    for item in UnitIdList:
        proinfo = getapi.requsetAPI(proinfourl,{"projectId":item,"agentId":agentId})[0]
        proinfo["min_price"] = priceFormat(proinfo["min_price"])
        proinfo["max_price"] = priceFormat(proinfo["max_price"])
        room_nb = len(proinfo['unitTypeList'])
        if room_nb > no_room : no_room = room_nb
        building = proinfo["blocks"].split(',')
        proinfo["blocks"] = len(building)
        if proinfo: datas['pro_list'].append(proinfo) 
        
    if not datas['pro_list'] :
        logger.error('Pro List Is None')
        raise HTTPException(status_code=404, detail="Pro Get Error")

    # 模板文件路径
    # temp_path = os.path.join(Config.ecoprop_temp_path,'ecoprop_pro_compare_share_temp.html').replace('\\','/')
    # 输出文件路径
    # str(datetime.datetime.now().strftime('%d-%m-%Y-%H%M%S'))

    new_file_name = datas['userInfo']['regNum']+"-"+str(datetime.datetime.now().strftime('%d-%m-%Y'))+'.pdf'
    re_path = os.path.join(Config.ecoprop_return_path,'user_pro_compare',new_file_name)
    
    
    if not os.path.exists(os.path.split(re_path)[0]):
        logger.info('ADD New folder ====>>>>'+os.path.split(re_path)[0])
        os.makedirs(os.path.split(re_path)[0])

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=Config.ecoprop_temp_path,encoding='utf-8'))
    template = env.get_template('xhoapp_pro_compare_share_temp.html')
    logger.info(datas)
    datas['openlink'] = "https://app.singmap.com/share/index.html#/vsProject?projectIds={0}&agentId={1}".format(projectId,agentId)
    datas['roomNo'] = no_room * 75
    # print(datas['roomNo'])

    # 模板填充参数
    options = {
        'page-size': 'A4',
        'margin-top': '5mm',
        'margin-right': '5mm',
        'margin-bottom': '5mm',
        'margin-left': '5mm',
        'orientation':'Landscape', #横向
        'encoding': "UTF-8",
        'no-outline': None,
    }
    try:
        logger.info('Set tmp Info ====>>>>')
        datas = eval(re.sub('None','\'\'',str(datas))) # 去除None值
        htmls = template.render(datas)
        # config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf') 
        pdfkit.from_string(htmls,re_path,options=options)
    except Exception as e:
        logger.error("File Padding Err ===>>>{0}".format(e))
        raise HTTPException(status_code=404, detail="PDF ADD Error")
        
    logger.info('PDF ADD Over ====>>>>')
    return re_path









