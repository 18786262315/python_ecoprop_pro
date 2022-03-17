
# import imp
import imp
from logging import exception
# from msilib.schema import Error
from fastapi import APIRouter,Form,HTTPException
import os
# from PIL import Image
from .comm import MakeReportlab,getAPI
from comm.logger import logger

# reportlab
from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import PageBreak,Table
# from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.units import mm,cm
from reportlab.lib import colors
from reportlab.lib.colors import HexColor,black,red,PCMYKColor
from reportlab.graphics.shapes import Drawing,Rect
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
# from reportlab.graphics.charts.barcharts import HorizontalBarChart
# from reportlab.lib.formatters import DecimalFormatter
import requests,json,time,datetime
from hashlib import md5


router = APIRouter(prefix="/project",tags=['project'],responses={405: {"description": "Not found"}},)






@router.get("/")
def read_users():

    return "res_data"


@router.post('/pnd_pro_pdf')
async def GetPndPdfPro(agentId: str=Form(...) ,projectId:str=Form(...)):
    """
    项目ID
    用户ID
    """
    logger.info('创建PDF,%s'%projectId)
    if not agentId and not projectId :
        raise HTTPException(status_code=404, detail="参数错误")

    # rentunpath = MakePDF(agentId,projectId)
    # return rentunpath

    try:
        rentunpath = MakePDF(agentId,projectId)
        logger.info('PDF创建成功=======>{}'.format(rentunpath))
        rtdata = {
            'code':'0',
            'msg':'succeed',
            "datas":rentunpath
        }
        return rtdata
    except BaseException as e:
            rtdata = {
            'code':'-1',
            'msg':'error',
            "datas":e
            }
            return rtdata

def MakePDF(agentId,projectId):

    # 基础数据准备 =====================================================
    # envs = "test" #测试环境
    # envs = "" # 本地
    envs = "release" # 发布
    imgpath = 'http://192.168.0.145:8083'
    urlpath = 'http://192.168.0.145:9998' #API
    filepath = os.getcwd() # 当前文件路径 服务器文件路径 ：/home/upload/broke/pnd/file/report
    returnpaths = os.getcwd() # 当前文件路径 服务器文件路径 ：/home/upload/broke/pnd/file/report

    if envs == "test":
        imgpath = 'http://192.168.0.145:8083'
        urlpath = 'http://192.168.0.145:9998' #API
        filepath = '/home/upload/broke/pnd/file/report'
        returnpaths = "/home/upload/broke/pnd/file/report"
    if envs == 'release':
        imgpath = 'https://img.singmap.com'
        urlpath = 'https://api.singmap.com' #API
        filepath = '/home/upload/broke/pnd/file/report'
        returnpaths = "/home/upload/broke/pnd/file/report"

    
    getapi = getAPI()
    # 项目信息
    proinfourl = urlpath+"/pnd-api/project/queryProjectInfoById"
    proinfodata = {
        "projectId":projectId,
        "agentId":agentId
    }
    proinfo = getapi.requsetAPI(proinfourl,proinfodata)
    

    if "projectInfo" in proinfo and "unitInfo" in proinfo and "agentInfo" in proinfo:
        logger.info('项目信息查询成功--->>>projectId:%s,agentId:%s,projectInfo:%s,unitInfo:%s,agentInfo:%s'%(projectId,agentId,proinfo['projectInfo'],proinfo['unitInfo'],proinfo['agentInfo']))
    else:
        logger.info('项目信息查询失败--->>>projectId:%s,agentId:%s'%(projectId,agentId))
        raise HTTPException(status_code=404, detail="项目信息查询失败")

    prodatainfo = proinfo['projectInfo'] # 项目信息
    unitInfo = proinfo['unitInfo'] # 单位信息
    userinfo = proinfo['agentInfo'] #用户信息
    dealInfo = proinfo['dealInfo'] # 房间-信息
    Symbol = "$" #价格符
    if prodatainfo["currencySymbol"] != None:
        Symbol = prodatainfo["currencySymbol"]
    unitproce = [0,0,0,0,0] #单位售价


    # 项目PDF上传图片
    propdfurls = urlpath+"/pnd-api/pdf/queryPdfProjectList"
    propdfdatas = {
        "projectId":projectId,
        "type":""
    }
    propdfinfo = getapi.requsetAPI(propdfurls,propdfdatas)
    if propdfinfo == None :
        logger.info('项目PDF上传图片为空--->>>projectId:%s,agentId:%s'%(projectId,agentId))

    # 项目区域
    districturl = urlpath+"/pnd-api/pdf/queryPdfDistrictList"
    districtdata = {
        "district":prodatainfo['district'],
        "type":"1"
    }
    districtinfo = getapi.requsetAPI(districturl,districtdata)
    logger.info('项目区域销售图查询成功--->>>%s'%(districtinfo))

    # PDF文件　页面图片查询
    fileurl = urlpath+"/pnd-api/pdf/queryPdfList"
    filedata = {
        "fileName":"ProjectReport",
        "page":""
    }
    fileinfo = getapi.requsetAPI(fileurl,filedata)
    logger.info('PDF文件页面图片查询成功--->>>%s'%(fileinfo))

    #新加坡区间 销售统计
    regionurl = urlpath+"/pnd-api/project/queryRetailCount"
    RCRdata = {
        "region":"RCR"
    }
    RCRinfo = getapi.requsetAPI(regionurl,RCRdata)
    logger.info('RCR查询成功--->>>%s'%(RCRdata))

    CCRdata = {
        "region":"CCR"
    }
    CCRinfo = getapi.requsetAPI(regionurl,CCRdata)
    logger.info('CCR查询成功--->>>%s'%(CCRinfo))

    OCRdata = {
        "region":"OCR"
    }
    OCRinfo = getapi.requsetAPI(regionurl,OCRdata)
    logger.info('OCR查询成功--->>>%s'%(OCRinfo))

    # print("---->项目详情",proinfo)
    # print("---->区间详情RCRinfo",RCRinfo)
    # print("---->区间详情CCRinfo",CCRinfo)
    # print("---->区间详情OCRinfo",OCRinfo)
    # print("---->PDF文件列表",fileinfo)
    # print("---->区域图片",districtinfo)
    # print("---->项目详情PDF图片",propdfinfo)

    # 创建PDF文档 =====================================================
    song = "simsun"
    pdfmetrics.registerFont(TTFont(song, "simsun.ttc"))
    pdfmetrics.registerFont(TTFont('ARIALBD','ARIALBD.TTF')) #注册字体
    pdfmetrics.registerFont(TTFont('arial','arial.ttf')) #注册字体
    Imagepath = os.path.join(filepath,'file')
    # Imagepath = R"E:\新联国际\地产项目\需求\定制\HUTTONS 中介私人定制PND\2022\02\latest Pnd Image"
    pagesize = (1747,965) # 画布大小
    # pagesize = (A4[1],A4[0]) # 画布大小
    # PND文件夹+ 项目ID + 用户信息 + 文件名称
    uppath = os.path.join(filepath,agentId)
    if not os.path.exists(uppath):
        os.makedirs(uppath)
    savepath = os.path.join(uppath,projectId+'.pdf') 
    returnPath = os.path.join(returnpaths,agentId,projectId+'.pdf')
    doc = canvas.Canvas(savepath,pagesize=pagesize)
    makefunc = MakeReportlab(doc,Imagepath,pagesize,Symbol) # 加载方法

    

    ######################################################################
    # page1  ===============================================
    # 背景
    makefunc.background('0.jpg')
  
    # if userinfo['logo']:
    #     makefunc.AddURLImages(imgpath+userinfo['logo'],x=pagesize[0]-250,y=0,w=224,h=224) 

    # doc.drawImage(userlogo,x,y,width=image.width,height=image.height,mask='auto')

    # agentdata4 = [
    # [userinfo['email'], userinfo['agentName']],
    # [userinfo['mobile'],userinfo['regNum']]
    # ]

    # t = Table(agentdata4, style={
    # # ("FONT", (0, 0), (-1, -1), song, 20),
    # ("FONT", (0, 0), (-1, -1), "arial", 20),
    # ('LINEBEFORE', (0, 0), (-1, -1), 0.05 * cm, colors.black),
    # ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
    # })
    # t._argW[0] = 400
    # t._argW[1] = 400
    # t.wrapOn(doc, 0, 0)
    # t.drawOn(doc, 750, 20)
    if userinfo['logo']:
        ...
        makefunc.AddURLImages(imgpath+userinfo['logo'],x=650,y=150,w=224,h=224) 

    agentdata4 = [
    ["NAME",':', userinfo['agentName']],
    ["MOBILE",':', userinfo['mobile']],
    ["EMAIL",':',userinfo['email']],
    ["CEA",':', userinfo['regNum']]
    ]

    t = Table(agentdata4, style={
    # ("FONT", (0, 0), (-1, -1), song, 35,50),
    ("FONT", (0, 0), (-1, -1), 'arial', 35,50),
    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
    ('ALIGN', (1, 0), (1, -1), 'CENTER')
    })
    t._argW[1] = 20
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 880, 150)
    doc.showPage()  # 保存当前画布页面

    # Page2  ===============================================
    makefunc.AddImages('1.jpg',w=pagesize[0],h=pagesize[1])
    doc.showPage()





    # Page3 ===============================================
    # 背景颜色
    # makefunc.addBagecolor(0,0,pagesize[0],pagesize[1])
    #right Image 
    # makefunc.AddImages('RTD Intelligence Report3.png',x=pagesize[0]-500,y=0,w=500,h=pagesize[1]) 

    # LOGO
    makefunc.AddLogo()

    my_text = prodatainfo['projectName']
    doc.setFillColorRGB(0,0,0) #choose your font colour
    doc.setFont('ARIALBD', 60)
    textobject = doc.beginText(30, pagesize[1]-80)
    for line in my_text.splitlines(False):
        textobject.textLine(line.rstrip())
    doc.drawText(textobject)

    makefunc.addTesxts(fontsize=25,x=30,y=pagesize[1]-150,text="PROJECT SUMMARY",color=HexColor('#e37200'))

    # 项目主图
    makefunc.ImageAdaptive(imgpath+prodatainfo['mainImage'],x=pagesize[0]-400,y=pagesize[1]-400,w=400,h=200) 
    # doc.showPage()  # 保存当前画布页面

    # doc.save()  # 保存文件并关闭画布
    # return returnPath
    # 增加背景颜色
    # makefunc.addBagecolor(0,40,pagesize[0]-500,600,'0xF8F8FF')
    timeArray = time.strptime(prodatainfo['completionDate'], "%Y-%m-%d %H:%M:%S")
    otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
    prodata = [
    ["Developer",':', prodatainfo['brokeName']],
    ["Tenure",':', prodatainfo['tenure']],
    ["District",':', prodatainfo['district']],
    ["Region",':', prodatainfo['projectArea']],
    ["Top",':', otherStyleTime],
    ["Total Units",':', prodatainfo['unitsNum']]
    ]

    makefunc.drawUserInfoTable(prodata,30,600)

    # 单位类型价格统计表
    makefunc.addTesxts(fontsize=25,x=30,y=500,text="UNIT PRICE",color=HexColor('#e37200'))
    prodataroombed = [
    ["Types",'','Price from'],
    ]
    Pielist = []
    for item in unitInfo:
        # print(item['bedrooms'],prodatainfo['currencySymbol'],item['price'])
        if item['bedrooms'] == None :
            # print(2222222)
            continue
        else:   
            # print(type(item['bedrooms']))
            prodataroombed.append([str(item['bedrooms'])+" Bedroom",':',makefunc.priceset(item['price']),],)
            if item['bedrooms'] == 1:
                # print(1111111)
                unitproce[0] = item['price']
            if item['bedrooms'] == 2:
                unitproce[1] = item['price']

            if item['bedrooms'] == 3:
                unitproce[2] = item['price']
            if item['bedrooms'] == 4:
                unitproce[3] = item['price']
            if item['bedrooms'] == 5:
                unitproce[4] = item['price']

        # print(prodataroombed)
    makefunc.drawUserInfoTable(prodataroombed,30,300)


    makefunc.addTesxts(fontsize=25,x=pagesize[0]-1000,y=pagesize[1]-250,text="BEDROOM UNITS SHARES",color=HexColor('#e37200'))

    # 饼图
    makefunc.MakePie(unitInfo).drawOn(doc,620,180)

    # 底部内容
    page3_btm = [
        ['Within Mrt.','[Yes] Outram Park'],
        ['School(s) Within 1 KM','[-]'],
        ['Project Brochure','[-]'],
        ['360 Panorama','[-]'],
        # ['Within Mrt.','[Yes] Outram Park','Project Brochure','360 Panorama'],
        # ['School(s) Within 1 KM','','',''],
    ]
    # if proinfo['url']:
        # doc.linkURL(imgpath+proinfo['url'], (0,100,1050+447,176))

    t = Table(page3_btm, style={
    ("FONT", (0, 0), (-1, -1), "arial", 20),
    ("TEXTCOLOR", (0, 0), (0, -1), HexColor('#e37200')),
    # ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    })
    # t._argW[0] = 250
    # t._argW[1] = 250
    # t._argW[2] = 250
    # t._argW[3] = 250
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 30, 150)

    # 页脚
    makefunc.addTesxts(fontsize=16,x=10,y=10,text="Personalised Property Analytics Report • Value-adding Your Home Purchase")

    doc.showPage()  # 保存当前画布页面

    # Page4 项目周边===========================================================================

    # 背景图
    # makefunc.background('RTD Intelligence Report27.png')
    # LOGO
    makefunc.AddLogo()
    makefunc.addTesxts(fontsize=60,x=10,y=pagesize[1]-80,text=prodatainfo['projectName'],fontname='ARIALBD')

    makefunc.addTesxts(fontsize=40,x=pagesize[0]/2.6,y=pagesize[1]-270,text="LOCATION HIGHLIGHT",color=HexColor('#e37200'))

    if prodatainfo['snapshotLogo'] :
        ...
         # 地址Google 截图
        makefunc.AddURLImages(imgpath+prodatainfo['snapshotLogo'],x=100,y=100,w=700,h=550) 
    if propdfinfo != [] :
        ...
        # 周边截图
        makefunc.AddURLImages(imgpath+propdfinfo[0]['logo'],x=pagesize[0]/2,y=100,w=700,h=550)
        # makefunc.AddImages('RTD Intelligence Report7.png',x=pagesize[0]/2,y=100,w=700,h=550) 


    doc.showPage()  # 保存当前画布页面

    # Page5  项目周边截图、===========================================================================

    # # left
    # makefunc.AddImages('RTD Intelligence Report12.png',x=0,y=0,w=(pagesize[0]/3)*2,h=pagesize[1])

    # # right
    # makefunc.AddImages('RTD Intelligence Report13.png',x=(pagesize[0]/3)*2,y=0,w=pagesize[0]/3,h=pagesize[1])

    # doc.showPage()  # 保存当前画布页面

    # Page6 区域出租记录图片 ===========================================================================
    if districtinfo :
        # print(districtinfo)
        makefunc.AddURLImages(imgpath+districtinfo[0]['logo'],w=pagesize[0],h=pagesize[1])
        makefunc.addTesxts(fontsize=50,x=10,y=pagesize[1]-80,text='District Pricing (Rental)',color=HexColor('#e37200'))
        doc.showPage()  # 保存当前画布页面

    # Page7 中介信息===========================================================================

    makefunc.background('6.jpg')

    if userinfo['logo']:
        ...
        makefunc.AddURLImages(imgpath+userinfo['logo'],x=650,y=200,w=224,h=224) 

    agentdata2 = [
    ["NAME",':', userinfo['agentName']],
    ["MOBILE",':', userinfo['mobile']],
    ["EMAIL",':',userinfo['email']],
    ["CEA",':', userinfo['regNum']]
    ]

    t = Table(agentdata2, style={
    ("FONT", (0, 0), (-1, -1), "arial", 35,50),
    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
    ('ALIGN', (1, 0), (1, -1), 'CENTER')
    })
    t._argW[1] = 20
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 880, 195)

    # WhatsApp 聊天跳转按钮
    # makefunc.AddImages('RTD Intelligence Report29.png',x=1050,y=100,w=447,h=76) 
    doc.linkURL('https://api.whatsapp.com/send?phone= '+userinfo['mobile'], (1250,90,1250+447,150))

    doc.showPage()  # 保存当前画布页面

    # doc.showPage()  # 保存当前画布页面

    # Page8 ===========================================================================

    # makefunc.addBagecolor(0,0,pagesize[0],pagesize[1],color="0x40E0D0")
    # left Image
    # makefunc.AddImages('RTD Intelligence Report17.png',x=0,y=0,w=436,h=pagesize[1]) 
    # LOGO
    makefunc.AddLogo()
    # Guide to Financial Wellness

    makefunc.addTesxts(fontsize=40,x=pagesize[0]/3,y=650,text="Guide to Financial Wellness")
  
    # 单位统计表
    unittype2 = [
    ["Unit Type",'Price from', "Monthly Installment","Min. Monthly Income \n Required For The Purchase",""],
    ["",'','', "Employee","Self Employed"],
    # ["1 Bedroom",Symbol+str(unitproce[0]), makefunc.stages(unitproce[0]), '$'+str(round(unitproce[0]*0.6,2)), '$'+str(round(unitproce[0]*0.7,2))],
    # ["2 Bedroom",Symbol+str(unitproce[1]), makefunc.stages(unitproce[1]), '$'+str(round(unitproce[1]*0.6,2)), '$'+str(round(unitproce[1]*0.7,2))],
    # ["3 Bedroom",Symbol+str(unitproce[2]), makefunc.stages(unitproce[2]), '$'+str(round(unitproce[2]*0.6,2)), '$'+str(round(unitproce[2]*0.7,2))],
    # ["4 Bedroom",Symbol+str(unitproce[3]), makefunc.stages(unitproce[3]), '$'+str(round(unitproce[3]*0.6,2)), '$'+str(round(unitproce[3]*0.7,2))],
    # ["5 Bedroom",Symbol+str(unitproce[4]), makefunc.stages(unitproce[4]), '$'+str(round(unitproce[4]*0.6,2)), '$'+str(round(unitproce[4]*0.7,2))],
    ]
    for item in unitInfo:
        ...
        if item['bedrooms'] == None :
            continue
        else:
            # print(item['bedrooms'])
            unittype2.append([str(item['bedrooms'])+" Bedroom",makefunc.priceset(item['price']), makefunc.stages(item['price']), makefunc.priceset(item['price']*0.6), makefunc.priceset(item['price']*0.7)])
    t = Table(unittype2,(pagesize[0]-436)/5,50, style={
    ('SPAN', (-2, 0), (-1,0)), # 合并单元格(列,行)
    ('BACKGROUND',(1,2),(-1,-1), colors.white),
    ('LINEBEFORE', (0, 0), (-1, -1), 0.1 * cm, colors.black),
    ('BOX', (0, 0), (-1, -1), 0.1 * cm, colors.black),
    ('LINEABOVE', (0, 0), (-1, -1), 0.1 * cm, colors.black),
    ('LINEBELOW', (0,0), (-1,-1), 0.1 * cm, colors.black),
    # ("FONT", (0, 0), (-1, -1), song, 25),
    ("FONT", (0, 0), (-1, -1), "arial", 25),
    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    })
    t._argH[0] = 75 
    t._argH[1] = 65 
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 200, 200)

    # 免责声明
    makefunc.addTesxts(fontsize=18,x=200,y=145,text="*Calculation based on 30 years tensure, 1.6% bank interest rate. For your personal financial calculation, please approach our salesperson for assistance")
    # makefunc.addTesxts(fontsize=18,x=720,y=120,text=" financial calculation, please approach our salesperson for assistance.")

    # 页脚
    makefunc.addTesxts(fontsize=16,x=30,y=30,text=" PERSONALISED PROPERTY ANALYTICS REPORT. | 2020")

    doc.showPage()  # 保存当前画布页面
    
    # Page9 ===========================================================================
    # 背景
    makefunc.background('8.jpg')
    if userinfo['logo']:
        ...
        makefunc.AddURLImages(imgpath+userinfo['logo'],x=100,y=250,w=224,h=224) 

    agentdata5 = [
    ["NAME",':', userinfo['agentName']],
    ["MOBILE",':', userinfo['mobile']],
    ["EMAIL",':',userinfo['email']],
    ["CEA",':', userinfo['regNum']]
    ]

    t = Table(agentdata5, style={
    # ("FONT", (0, 0), (-1, -1), song, 35,50),
    ("FONT", (0, 0), (-1, -1), 'arial', 35,50),
    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
    ('ALIGN', (1, 0), (1, -1), 'CENTER')
    })
    t._argW[1] = 20
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 350, 250)
    # WhatsApp 聊天跳转按钮
    # makefunc.AddImages('RTD Intelligence Report29.png',x=1050,y=100,w=447,h=76) 
    doc.linkURL('https://api.whatsapp.com/send?phone='+userinfo['mobile'], (600,100,600+447,176))

    doc.showPage()  # 保存当前画布页面

    # Page10 ===========================================================================
    # makefunc.background('RTD Intelligence Report27.png')
    makefunc.background('9.jpg')

    # LOGO
    makefunc.AddLogo()

    makefunc.addTesxts(fontsize=60,x=400,y=pagesize[1]-100,text="PROGRESSIVE PAYMENT")

    # 贷款计算
    unitcalculator = [
        ['','','1 Bedroom','2 Bedroom','3 Bedroom','4 Bedroom','5 Bedroom'],
        ['PURCHASE PRICE','','-','-','-','-','-'],
        ['LOAN AMT (75%)','','-','-','-','-','-'],
        ['DOWN PAYMENTS & STAM DUTIES','','','','',''],
        [R'5% Upon Booking - Cash','','-','-','-','-','-'],
        ["Buyer's Stamp Duty - BSD",'','-','-','-','-','-'],
        ['15% Down Payment - Cash/CPF','','-','-','-','-','-'],
        ['Total Intial Down Payment (20% + BSD) ','','-','-','-','-','-'],
        ['DURING CONSTRUCTION PERIOD','','','','',''],
        ['10% Upon Foundation - 5% Cash/CPF','','-','-','-','-','-'],
        ['Grand Total for Cash + CPF','','-','-','-','-','-'],
    ]
    for y,data in enumerate(unitcalculator):
        # if item > 1:
        for x,data2 in enumerate(data):
            if x >1 :
                BSD = makefunc.priceBSD(unitproce[x-2])
                if y ==1:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]))
                if y ==2:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]*0.75))
                if y ==4:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]*0.05))
                if y ==5:
                    ...
                    unitcalculator[y][x] = makefunc.testNan(Symbol,BSD)
                if y ==6:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]*0.15))
                if y ==7:
                    ...
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round((unitproce[x-2]*0.2)+BSD))
                if y ==9:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]*0.5)) 
                if y ==10:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(((unitproce[x-2]*0.2)+BSD)+(unitproce[x-2]*0.5)))
    t = Table(unitcalculator,270,39)
    style={
    ('SPAN', (0, 0), (1,0)), # 合并单元格(列,行)
    # ("FONT", (0, 0), (-1, -1), song, 20),
    ("FONT", (0, 0), (-1, -1),'arial', 20),
    ('LINEBEFORE', (0, 0), (-1, -1), 0.05 * cm, colors.whitesmoke),
    ('BACKGROUND',(2,1),(-1,2), colors.white),
    ('BACKGROUND',(2,4),(-1,6), colors.white),
    ('BACKGROUND',(2,7),(-1,7), colors.orange),
    ('BACKGROUND',(2,9),(-1,9), colors.white),
    ('BACKGROUND',(2,10),(-1,10), colors.orange),
    ("TEXTCOLOR", (0,1), (-1, -1), colors.black),
    ('ALIGN', (1, 0), (-1, -1), 'CENTER')
    }
    # t._argH[0] = 45
    t._argW[0] = 200
    t._argW[1] = 200
    t.setStyle(style)
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 0, 420)


    unitcalculator1 = [
        ['','','Outstanding \n Loan','Monthly \n Installment','Outstanding \n Loan','Monthly \n Installment','Outstanding \n Loan','Monthly \n Installment','Outstanding \n Loan','Monthly \n Installment','Outstanding \n Loan','Monthly \n Installment'],
        ['10% Upon Foundation - Next 5%','',makefunc.counts(Symbol,unitproce[0],0.05),makefunc.counts(Symbol,unitproce[0],0.05,0.0035),
                                            makefunc.counts(Symbol,unitproce[1],0.05),makefunc.counts(Symbol,unitproce[1],0.05,0.0035),
                                            makefunc.counts(Symbol,unitproce[2],0.05),makefunc.counts(Symbol,unitproce[2],0.05,0.0035),
                                            makefunc.counts(Symbol,unitproce[3],0.05),makefunc.counts(Symbol,unitproce[3],0.05,0.0035),
                                            makefunc.counts(Symbol,unitproce[4],0.05),makefunc.counts(Symbol,unitproce[4],0.05,0.0035),],
        ['10% Upon Concrete Framework','',makefunc.counts(Symbol,unitproce[0],0.15),makefunc.counts(Symbol,unitproce[0],0.15,0.0035),
                                          makefunc.counts(Symbol,unitproce[1],0.15),makefunc.counts(Symbol,unitproce[1],0.15,0.0035),
                                          makefunc.counts(Symbol,unitproce[2],0.15),makefunc.counts(Symbol,unitproce[2],0.15,0.0035),
                                          makefunc.counts(Symbol,unitproce[3],0.15),makefunc.counts(Symbol,unitproce[3],0.15,0.0035),
                                          makefunc.counts(Symbol,unitproce[4],0.15),makefunc.counts(Symbol,unitproce[4],0.15,0.0035),],
        ['20% Upon Brick/Celling/Roads/Carparks','',makefunc.counts(Symbol,unitproce[0],0.35),makefunc.counts(Symbol,unitproce[0],0.35,0.0035),
                                                    makefunc.counts(Symbol,unitproce[1],0.35),makefunc.counts(Symbol,unitproce[1],0.35,0.0035),
                                                    makefunc.counts(Symbol,unitproce[2],0.35),makefunc.counts(Symbol,unitproce[2],0.35,0.0035),
                                                    makefunc.counts(Symbol,unitproce[3],0.35),makefunc.counts(Symbol,unitproce[3],0.35,0.0035),
                                                    makefunc.counts(Symbol,unitproce[4],0.35),makefunc.counts(Symbol,unitproce[4],0.35,0.0035),],
        ['UPON & AFTER T.O.P','','','',''],
        ['25% Upon T.O.P','',makefunc.counts(Symbol,unitproce[0],0.6),makefunc.counts(Symbol,unitproce[0],0.6,0.0035),
                            makefunc.counts(Symbol,unitproce[1],0.6),makefunc.counts(Symbol,unitproce[1],0.6,0.0035),
                            makefunc.counts(Symbol,unitproce[2],0.6),makefunc.counts(Symbol,unitproce[2],0.6,0.0035),
                            makefunc.counts(Symbol,unitproce[3],0.6),makefunc.counts(Symbol,unitproce[3],0.6,0.0035),
                            makefunc.counts(Symbol,unitproce[4],0.6),makefunc.counts(Symbol,unitproce[4],0.6,0.0035),],
        ['15% CSC','',makefunc.counts(Symbol,unitproce[0],0.75),makefunc.counts(Symbol,unitproce[0],0.75,0.0035),
                    makefunc.counts(Symbol,unitproce[1],0.75),makefunc.counts(Symbol,unitproce[1],0.75,0.0035),
                    makefunc.counts(Symbol,unitproce[2],0.75),makefunc.counts(Symbol,unitproce[2],0.75,0.0035),
                    makefunc.counts(Symbol,unitproce[3],0.75),makefunc.counts(Symbol,unitproce[3],0.75,0.0035),
                    makefunc.counts(Symbol,unitproce[4],0.75),makefunc.counts(Symbol,unitproce[4],0.75,0.0035),],


    ]
    
    unitcalculatortb1 = Table(unitcalculator1,135,39, style={
    ('SPAN', (0, 0), (1,0)), # 合并单元格(列,行)
    ('LINEBEFORE', (0, 0), (-1, -1), 0.05 * cm, colors.whitesmoke),
    # ("FONT", (0, 0), (-1, -1), song, 19),
    ("FONT", (0, 0), (-1, -1), 'arial', 19),
    ('FONTNAME', (0,0), (-1,0), 'Courier-Bold'),
    ('TEXTCOLOR',(2,0),(-1,0), colors.white),
    ('BACKGROUND',(2,0),(-1,0), colors.midnightblue),
    # ("FONT", (2,0),(-1,0), song, 16),
    ("FONT", (2,0),(-1,0), 'arial', 16),
    # ('LINEBELOW', (0, 0), (-1, -1), 0.05 * cm, colors.whitesmoke),

    ('BACKGROUND',(2,1),(-1,-1), colors.white),
    ("TEXTCOLOR", (0,1), (-1, -1), colors.black),
    ('ALIGN', (1, 0), (-1, -1), 'CENTER')
    })
    unitcalculatortb1._argH[0] = 50
    unitcalculatortb1._argW[0] = 200
    unitcalculatortb1._argW[1] = 200
    unitcalculatortb1.wrapOn(doc, 0, 0)
    unitcalculatortb1.drawOn(doc, 0, 135)

    # 免责声明
    makefunc.addTesxts(fontsize=16,x=600,y=100,text="*Calculation based on 30 years tenure, 1.6% bank interest rate. For your personal")
    makefunc.addTesxts(fontsize=16,x=620,y=80,text=" financial calculation, please approach our salesperson for assistance.")


    # 页脚
    makefunc.addTesxts(fontsize=16,x=30,y=30,text="Personalised Property Analytics Report • Value-adding Your Home Purchase")

    doc.showPage()  # 保存当前画布页面

    # Page10 ===========================================================================

    makefunc.background('10.jpg')
    if userinfo['logo']:
        ...
        makefunc.AddURLImages(imgpath+userinfo['logo'],x=100,y=270,w=224,h=224) 

    agentdata6 = [
    ["NAME",':', userinfo['agentName']],
    ["MOBILE",':', userinfo['mobile']],
    ["EMAIL",':',userinfo['email']],
    ["CEA",':', userinfo['regNum']]
    ]

    t = Table(agentdata6, style={
    # ("FONT", (0, 0), (-1, -1), song, 35,50),
    ("FONT", (0, 0), (-1, -1), 'arial', 35,50),
    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
    ('ALIGN', (1, 0), (1, -1), 'CENTER')
    })
    t._argW[1] = 20
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 350, 270)
    # makefunc.AddImages('RTD Intelligence Report30.png',x=370,y=370,w=530,h=76) 
    doc.linkURL('https://api.whatsapp.com/send?phone= '+userinfo['mobile'], (50,160,50+630,230))

    doc.showPage()  # 保存当前画布页面

    # Page11 ===========================================================================
    if fileinfo:
        for item in fileinfo:
            # print(item)
            if item["page"] == 10:
                makefunc.AddURLImages(imgpath+item['logo'],x=0,y=0,w=pagesize[0],h=pagesize[1]) 
                doc.showPage()  # 保存当前画布页面
    
    makefunc.background('11.jpg')
    doc.showPage()  # 保存当前画布页面

    # Page12 ===========================================================================

    # makefunc.addBagecolor(0,0,pagesize[0],pagesize[1])
    # right IMG
    makefunc.AddImages('14right.jpg',x=pagesize[0]-550,y=150,w=430,h=536)
    # LOGO
    makefunc.AddLogo()

    makefunc.addTesxts(fontsize=60,x=300,y=pagesize[1]-200,text="Sales Transactions",fontname='ARIALBD')

    
    # 单位销量统计
    unittransactions = [
        ['Date','Floor','Size(Sqft)','Price','Price(psf)'],
    ]
    for item in dealInfo:
        ...
        date = 'N/A'
        if item['transactionDate']:
            # print(item['transactionDate'])
            date = time.strftime('%Y-%m',time.localtime(item['transactionDate']/1000))

        unittransactions.append([date,item['floor'],item ['area'],makefunc.priceset(item['transactionPrice']),makefunc.priceset(item['price']),])
    t = Table(unittransactions,(pagesize[0]-560)/6,60, style={
    # ("FONT", (0, 0), (-1, -1), song, 22),
    ("FONT", (0, 0), (-1, -1), 'arial', 22),
    ('LINEABOVE', (0, 0), (-1, -1), 0.05 * cm, colors.whitesmoke),
    ('LINEBELOW', (0,-1), (-1,-1), 0.05 * cm, colors.whitesmoke),
    ('BACKGROUND',(0,0),(-1,0), colors.darkslateblue),
    ('TEXTCOLOR',(0,0),(-1,0), colors.white),
    ('BACKGROUND',(0,1),(-1,-1), colors.white),
    ("TEXTCOLOR", (0,1), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    })
    t._argH[0] = 45
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 100, 100)


    # 页脚
    makefunc.addTesxts(fontsize=16,x=30,y=30,text="Personalised Property Analytics Report • Value-adding Your Home Purchase")


    doc.showPage()  # 保存当前画布页面


    # Page13 ===========================================================================

    # makefunc.addBagecolor(0,0,pagesize[0],pagesize[1],color="0x40E0D0")
    # left Image
    # makefunc.AddImages('RTD Intelligence Report17.png',x=0,y=0,w=436,h=pagesize[1]) 
    # LOGO
    makefunc.AddLogo()
    # New Project Sales Progress
    # Core Central Region (CCR)
    makefunc.addTesxts(fontsize=40,x=pagesize[0]-600,y=500,text="New Project Sales Progress")
    makefunc.addTesxts(fontsize=25,x=pagesize[0]-600,y=450,text="Core Central Region (CCR)")

    RCRinfo
    makefunc.make_drawing(CCRinfo).drawOn(doc,0,100)

    makefunc.addTesxts(fontsize=16,x=30,y=30,text="Personalised Property Analytics Report • Value-adding Your Home Purchase")
    doc.showPage()  # 保存当前画布页面

    # Page14 ===========================================================================

    # makefunc.addBagecolor(0,0,pagesize[0],pagesize[1],color="0x40E0D0")
    # left Image
    # makefunc.AddImages('RTD Intelligence Report17.png',x=0,y=0,w=436,h=pagesize[1]) 
    # LOGO
    makefunc.AddLogo()
    # New Project Sales Progress
    # Core Central Region (RCR)
    makefunc.addTesxts(fontsize=40,x=pagesize[0]-600,y=500,text="New Project Sales Progress")
    makefunc.addTesxts(fontsize=25,x=pagesize[0]-600,y=450,text="Core Central Region (RCR)")

    makefunc.make_drawing(RCRinfo).drawOn(doc,0,100)

    makefunc.addTesxts(fontsize=16,x=30,y=30,text="Personalised Property Analytics Report • Value-adding Your Home Purchase")
    doc.showPage()  # 保存当前画布页面

    # Page15 ===========================================================================

    # makefunc.addBagecolor(0,0,pagesize[0],pagesize[1],color="0x40E0D0")
    # left Image
    # makefunc.AddImages('RTD Intelligence Report17.png',x=0,y=0,w=436,h=pagesize[1]) 
    # LOGO
    makefunc.AddLogo()
    # New Project Sales Progress
    # Core Central Region (OCR)

    '''
    柱状统计图 +++++++++++++
    '''
    
    makefunc.make_drawing(OCRinfo).drawOn(doc,0,100)
    makefunc.addTesxts(fontsize=40,x=pagesize[0]-600,y=500,text="New Project Sales Progress")
    makefunc.addTesxts(fontsize=25,x=pagesize[0]-600,y=450,text="Core Central Region (OCR)")

    makefunc.addTesxts(fontsize=16,x=30,y=30,text="Personalised Property Analytics Report • Value-adding Your Home Purchase")
    doc.showPage()  # 保存当前画布页面

    # Page16 ===========================================================================

    makefunc.background('16.jpg')

    # makefunc.AddImages('RTD Intelligence Report14.png',w=pagesize[0],h=pagesize[1])
    # makefunc.addTesxts(fontsize=60,x=500,y=pagesize[1]-200,text="NEW LAUNCH TIMELINE")

    # makefunc.AddImages('RTD Intelligence Report23.png',x=20,y=50,w=pagesize[0]-40,h=615)

    # makefunc.addTesxts(fontsize=16,x=pagesize[0]-750,y=10,text="Personalised Property Analytics Report • Value-adding Your Home Purchase")

    doc.showPage()  # 保存当前画布页面

    # Page16 ===========================================================================
    # makefunc.addBagecolor(0,0,pagesize[0],pagesize[1],color="0x40E0D0")

    makefunc.background('17.jpg')

    # makefunc.addTesxts(fontsize=40,x=500,y=pagesize[1]-200,text="THIS IN-DEPTH ANALYSIS ALLOWS YOU TO OBJECTIVELY")
    # makefunc.addTesxts(fontsize=40,x=520,y=pagesize[1]-250,text="UNDERSTAND YOUR FINANCIAL POSITION")

    # makefunc.addTesxts(fontsize=27,x=470,y=pagesize[1]-300,
    # text="""Our financial calculation process includes Exit Strategy for your property purchase. We use our""",
    # color=(116,230,217))
    # makefunc.addTesxts(fontsize=27,x=470,y=pagesize[1]-330,
    # text="""C.A.R.E analysis method to filter through the many options in the property market for you to""",
    # color=(116,230,217))
    # makefunc.addTesxts(fontsize=27,x=470,y=pagesize[1]-360,
    # text="""streamline your choices. This is a conservative & achievable asset progression plan, which allows""",
    # color=(116,230,217))
    # makefunc.addTesxts(fontsize=27,x=470,y=pagesize[1]-390,
    # text="""you to accumulate wealth earlier in your property portfolio.""",
    # color=(116,230,217))

    if userinfo['logo']:
        ...
        makefunc.AddURLImages(imgpath+userinfo['logo'],x=700,y=250,w=224,h=224) 

    agentdata3 = [
    ["NAME",':', userinfo['agentName']],
    ["MOBILE",':', userinfo['mobile']],
    ["EMAIL",':',userinfo['email']],
    ["CEA",':', userinfo['regNum']]
    ]

    t = Table(agentdata3, style={
    # ("FONT", (0, 0), (-1, -1), song, 35,50),
    ("FONT", (0, 0), (-1, -1), 'arial', 35,50),
    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
    ('ALIGN', (1, 0), (1, -1), 'CENTER')
    })
    t._argW[1] = 20
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 920, 250)

    # WhatsApp 聊天跳转按钮
    # makefunc.AddImages('RTD Intelligence Report29.png',x=1050,y=100,w=447,h=76) 
    doc.linkURL('https://api.whatsapp.com/send?phone= '+userinfo['mobile'], (1250,130,1250+350,200))
    # makefunc.addTesxts(fontsize=16,x=0,y=10,text="Personalised Property Analytics Report • Value-adding Your Home Purchase")
    doc.showPage()  # 保存当前画布页面

    # Page17 ===========================================================================
    makefunc.background('18.jpg')
    doc.showPage()  # 保存当前画布页面
    doc.save()  # 保存文件并关闭画布
    # time.sleep(3)
    return returnPath
    # return savepath 


def FunctionName():
    ##################################################################
    # 项目对比报表
    ##################################################################
    pagesize = (1747,965) # 画布大小
    # pagesize = (A4[1],A4[0]) # 画布大小
    # PND文件夹+ 项目ID + 用户信息 + 文件名称
    filepath = os.getcwd() # 当前文件路径 服务器文件路径 ：/home/upload/broke/pnd/file/report
    Imagepath = os.path.join(filepath,'file')
    savepath = os.path.join(Imagepath,'test.pdf') 
    doc = canvas.Canvas(savepath,pagesize=pagesize)

    makefunc = MakeReportlab(doc,Imagepath,pagesize) # 加载方法

    # page 1
    userinfo = {
        "name":"Toh Chai Lin Chantelle",
        "email":"chantelletoh9777@gmail.com",
        "mobile":"97779009",
        "cea":"R008284A",
        "id":"",
    }

    makefunc.background('Project Comparison Report1.png')
    makefunc.AddImages('RTD Intelligence Report1.png',x=20,y=20,w=224,h=224) 

    agentdata2 = [
    [userinfo['agentName']],
    [userinfo['mobile']],
    [userinfo['email']],
    [userinfo['regNum']]
    ]

    t = Table(agentdata2, style={
    ("FONT", (0, 0), (-1, -1), 'arial', 35,40),
    ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
    # ('ALIGN', (1, 0), (1, -1), 'CENTER')
    })
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 255, 40)





    doc.showPage()  # 保存当前画布页面


    # makefunc.addBagecolor(0,0,pagesize[0],pagesize[1],color="0x335C72")

    my_text = "PROJECT\nCOMPARISON"
    doc.setFillColorRGB(255,255,255) #choose your font colour
    doc.setFont("arial", 30)
    textobject = doc.beginText(10, pagesize[1]-30)
    for line in my_text.splitlines(False):
        textobject.textLine(line.rstrip())
    doc.drawText(textobject)

 
    img = makefunc.TableImageAdaptive("RTD Intelligence Report4.png",w=355,h=180) # 项目图片自适应

    procomparison = [
        ["",img,img,img,img],
        ["PROJECT","PROJECT","PROJECT","PROJECT","PROJECT"],
        ["DISTRICT","DISTRICT","DISTRICT","DISTRICT","DISTRICT"],
        ["TOTAL UNITS","UNITS","UNITS","UNITS","UNITS"],
        ["TOP","TOP","TOP","TOP","TOP"],
        ["TENURE","TENURE","TENURE","TENURE","TENURE"],
        ["DEVELOPER","DEVELOPER","DEVELOPER","DEVELOPER","DEVELOPER"],
        ["1 BR","$1,591,000","$1,591,000","$1,591,000","$1,591,000"],
        ["2 BR","$1,591,000","$1,591,000","$1,591,000","$1,591,000"],
        ["3 BR","$1,591,000","$1,591,000","$1,591,000","$1,591,000"],
        ["4 BR","$1,591,000","$1,591,000","$1,591,000","$1,591,000"],
        ["5 BR","$1,591,000","$1,591,000","$1,591,000","$1,591,000"],
        ["DISTANCE \n FRM MRT","[Yes]WoodleighMRT","[Yes]WoodleighMRT","[Yes]WoodleighMRT","[Yes]WoodleighMRT"],
        ["SCHOOLS","Cedar PrimarySchool\nMarisStella High School","","",makefunc.create_body_text('Cedar PrimarySchool MarisStella High School')],
        ["DOWNLOAD \n BROCHURE","CLICK HERE","CLICK HERE","CLICK HERE","CLICK HERE"],

    ]

    t = Table(procomparison,385,45, style={
    ("FONT", (0, 0), (-1, -1), 'arial', 16,25),
    ("TEXTCOLOR", (0, 0), (-1, -1), HexColor("0x335C72")),
    ('BACKGROUND',(0,0),(-1,-1), colors.white),
    ('LINEBEFORE', (0, 0), (-1, -1), 0.5* cm, HexColor("0x335C72")),
    ('LINEBELOW', (0, 7), (-1, 11), 0.05* cm, HexColor("0x335C72")),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), 
    })
    t._argH[0] = 200
    t._argH[12] = 52
    t._argH[13] = 60
    t._argH[14] = 52
    t._argW[0] = 150
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 20, 20)
    doc.showPage()  # 保存当前画布页面
    doc.save()  # 保存文件并关闭画布
