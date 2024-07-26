
from comm.logger import logger
from .comm import MakeReportlab,getAPI,getDatetimes
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Table
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
# from reportlab.lib.utils import ImageReader
# from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
import re,os,json,time
# from PIL import Image
from config import Config

"""
项目详情PDF报表
"""


gettime = getDatetimes()

# XHORIZON APP 项目报表 
def XHORIZON_APP_PRO_PDF(agentId,projectId):
    # 基础数据准备 =====================================================
    getapi = getAPI()
    # 项目信息
    proinfourl = Config.urlpath+"/pnd-api/project/queryProjectInfoById_big"
    proinfodata = {
        "projectId":projectId,
        "agentId":agentId
    }
    proinfo = getapi.requsetAPI(proinfourl,proinfodata)
    logger.info('查询项目信息--->>>%s'%proinfo)

    # if "projectInfo" in proinfo and "unitInfo" in proinfo and "agentInfo" in proinfo:
    #     logger.info('查询项目信息--->>>projectId:%s,agentId:%s,projectInfo:%s,unitInfo:%s,agentInfo:%s'%(projectId,agentId,proinfo['projectInfo'],proinfo['unitInfo'],proinfo['agentInfo']))
    # else:
    #     logger.info('项目信息查询失败--->>>projectId:%s,agentId:%s'%(projectId,agentId))
        # raise HTTPException(status_code=404, detail="项目信息查询失败")
    
    prodatainfo = proinfo['projectInfo'] # 项目信息
    unitInfo = proinfo['unitInfo'] # 单位信息
    userinfo = proinfo['agentInfo'] #用户信息
    dealInfo = proinfo['dealInfo'] # 房间-信息
    Symbol =  prodatainfo["currencySymbol"] if prodatainfo["currencySymbol"] else "$"
    unitproce = [0,0,0,0,0] #单位售价

    propdfinfo = getapi.requsetAPI( Config.urlpath+"/pnd-api/pdf/queryPdfProjectList",{
        "projectId":projectId,
        "type":""
    })

    if prodatainfo['district'] :
        districtinfo = getapi.requsetAPI(Config.urlpath+"/pnd-api/pdf/queryPdfDistrictList",{"district":prodatainfo['district'],"type":"1"})
        # logger.info('项目区域销售图查询成功--->>>%s'%(districtinfo))
    else:
        districtinfo = []

    # fileinfo = getapi.requsetAPI(Config.urlpath+"/pnd-api/pdf/queryPdfList",{
    #     "fileName":"ProjectReport",
    #     "page":""
    # })
    # logger.info('PDF文件页面图片查询成功--->>>%s'%(fileinfo))

    #新加坡区间 销售统计
    regionurl = Config.urlpath+"/pnd-api/project/queryRetailCount"
    # RCRdata = { "region":"RCR"}
    RCRinfo = getapi.requsetAPI(regionurl,{ "region":"RCR"})
    # logger.info('RCR查询成功--->>>%s'%(RCRinfo))

    # CCRdata = { "region":"CCR"}
    CCRinfo = getapi.requsetAPI(regionurl,{ "region":"CCR"})
    # logger.info('CCR查询成功--->>>%s'%(CCRinfo))

    # OCRdata = {"region":"OCR"}
    OCRinfo = getapi.requsetAPI(regionurl,{"region":"OCR"})
    # logger.info('OCR查询成功--->>>%s'%(OCRinfo))

    # 创建PDF文档 =====================================================

    # song = "simsun"
    # pdfmetrics.registerFont(TTFont(song, "simsun.ttc"))
    pdfmetrics.registerFont(TTFont('ARIALBD','ARIALBD.TTF')) #注册字体
    pdfmetrics.registerFont(TTFont('arial','arial.ttf')) #注册字体
    pdfmetrics.registerFont(TTFont('msyh','msyh.ttf')) #注册字体
    pdfmetrics.registerFont(TTFont('msyhbd','msyhbd.ttf')) #注册字体
    Imagepath = os.path.join(Config.filepath,'file')
    pagesize = (1747,965) # 画布大小
    # pagesize = (A4[1],A4[0]) # 画布大小
    # PND文件夹+ 项目ID + 用户信息 + 文件名称
    # gettime = getDatetimes()
    # tt = gettime.getDate()
    uppath = os.path.join(Config.filepath,agentId)
    if not os.path.exists(uppath):
        os.makedirs(uppath)
    
    savepath = os.path.join(uppath,str(int(time.time()))+'.pdf')
    returnPath = os.path.join(Config.returnpaths,agentId,str(int(time.time()))+'.pdf')
    doc = canvas.Canvas(savepath,pagesize=pagesize)
    doc.setTitle(prodatainfo['projectName'])
    makefunc = MakeReportlab(doc,Imagepath,pagesize,Symbol) # 加载方法
    # logger.info('---------->>>文档创建')

    

    ######################################################################
    # page1  ===============================================
    # 固定内容
    # 背景、 公司 LOGO、 右侧用户 LOGO
    makefunc.background('XHOAPPbg1.png')

    # makefunc.ImageAdaptive('XHOAPPlogo.png',x=10,y=750,w=280,h=595)
    if userinfo['logo'] and Config.envs == 'release':
        makefunc.AddRightIMG(Config.imgpath+userinfo['logo'],x=1550,y=770)

    if userinfo['logo'] and Config.envs == 'release':
        makefunc.AddURLImages(Config.imgpath+userinfo['logo'],x=750,y=100,w=224,h=224)
        
    agentdata4 = [
    ["NAME",':', userinfo['agentName']],
    ["MOBILE",':', userinfo['mobile']],
    ["EMAIL",':',userinfo['email']],
    ["CEA",':', userinfo['regNum']]
    ]

    t = Table(agentdata4, style={
    ("FONT", (0, 0), (-1, -1), 'arial', 35,50),
    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
    ('ALIGN', (1, 0), (1, -1), 'CENTER')
    })
    t._argW[1] = 20
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 1000, 100)
    doc.showPage()  # 保存当前画布页面
    logger.info('============>> 1 page')


    ######################################################################
    # Page2 ===============================================
    makefunc.background('XHOAPPbg.png')
    if userinfo['logo'] and Config.envs == 'release':
        makefunc.AddRightIMG(Config.imgpath+userinfo['logo'],x=pagesize[0]-200,y=770)

    my_text = prodatainfo['projectName']
    doc.setFillColorRGB(0,0,0) #choose your font colour
    doc.setFont('msyhbd', 35)
    textobject = doc.beginText(70, pagesize[1]-300)
    for line in my_text.splitlines(False):
        textobject.textLine(line.rstrip())
    doc.drawText(textobject)

    makefunc.addTesxts(fontsize=25,fontname='ARIALBD',x=70,y=550,text="PROJECT SUMMARY",color=HexColor('#A68E42'))
    # 项目主图
    if prodatainfo['mainImage'] and Config.envs == 'release':
        ...
        makefunc.ImageAdaptive(Config.imgpath+prodatainfo['mainImage'],x=pagesize[0]-380,y=pagesize[1]-450,w=400,h=200) 
    completionDate = ''
    if type(prodatainfo['completionDate']) is int:
        timeArray = time.strptime(prodatainfo['completionDate'], "%Y-%m-%d")
        completionDate = time.strftime("%Y", timeArray)
    if type(prodatainfo['completionDate']) is str and makefunc.isVaildDate(prodatainfo['completionDate']):
        a = time.strptime(prodatainfo['completionDate'], "%Y-%m-%d %H:%M:%S")
        completionDate = time.strftime("%Y", a)
    else:
        completionDate = prodatainfo['completionDate']
    prodata = [
    ["Developer",':', makefunc.create_body_text(prodatainfo['brokeName'],color=colors.black,font_size=22,font_name="arial",leading = 22) ],
    ["Tenure",':', prodatainfo['tenure']],
    ["District",':', prodatainfo['district']],
    ["Region",':', prodatainfo['projectArea']],
    ["Top",':', completionDate],
    ["Total Units",':', prodatainfo['unitsNum']]
    ]

    makefunc.drawUserInfoTable(prodata,70,285)
    logger.info('============>> Pro info OK !')

    # 单位类型价格统计表
    # makefunc.addTesxts(fontsize=25,fontname='ARIALBD',x=70,y=550,text="UNIT PRICE",color=HexColor('#A68E42'))
    prodataroombed = [
    ['UNIT PRICE'],
    ["Types",'','Size Range','Price From'],
    ]
    Pielist = []
    for item in unitInfo:
        logger.info(item)
        size = '-'
        if item['minArea'] != 0 and item['maxArea'] != 0: # 户型最大最小面积
            size = '{0}-{1}sqft'.format(item['minArea'],item['maxArea'])

        if item['type'] == None or item['type'] < 1 or item['type'] > 5:
            continue
        elif item['min_price1']:
            prodataroombed.append([str(item['type'])+" Bedroom",':',size,makefunc.priceset(item['min_price1'])])
            if item['type'] == 1:
                unitproce[0] = item['min_price1']
            if item['type'] == 2:
                unitproce[1] = item['min_price1']
            if item['type'] == 3:
                unitproce[2] = item['min_price1']
            if item['type'] == 4:
                unitproce[3] = item['min_price1']
            if item['type'] == 5:
                unitproce[4] = item['min_price1']
        else:
            prodataroombed.append([str(item['type'])+" Bedroom",':',size,makefunc.priceset(item['min_price1'])])

    t = Table(prodataroombed, style={
    ("FONT", (0, 0), (-1, 1), 'ARIALBD',25),
    # ("FONT", (0, 1), (-1, 1), 'ARIALBD',25),
    ("TEXTCOLOR", (0, 0), (-1, 0), HexColor('#A68E42')),
    ("FONT", (0, 1), (-1, -1), 'arial', 26),
    ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
    ('ALIGN', (1, 0), (1, -1), 'CENTER')
    })
    t._argW[1] = 20
    t._argW[2] = 250
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 500, 720)
    logger.info('============>> Pro unit Info OK !')

    makefunc.addTesxts(fontsize=25,fontname='ARIALBD',x=1350,y=400,text="BEDROOM UNITS SHARES",color=HexColor('#A68E42'))
    # 饼图
    makefunc.MakePie(unitInfo,200,200).drawOn(doc,1400,110,)
    logger.info('============>> Pro MakePie OK !')

    # 底部内容
    page3_btm = [
        ['Project Brochure','[-]'],
        ['360 Panorama','[-]'],
        ['School(s) Within 1 KM','[-]'],
        ['Nearby MRT within 2KM','[-]'],
    ]
    if prodatainfo['url'] != None:
        page3_btm[0][1] = 'CLICK HERE'
        doc.linkURL(Config.imgpath+prodatainfo['url'], (710,540,710+150,540+22))
    if prodatainfo['ivtList'] != []:
        page3_btm[1][1] = 'CLICK HERE'
        # print(prodatainfo['ivtList'][0])
        doc.linkURL(prodatainfo['ivtList'][0], (710,515,710+150,515+22))
    if prodatainfo['facilitiesMap']:
        facilities = json.loads(prodatainfo['facilitiesMap'])
        for item in facilities:
            if item['type'] == 'subway_station' and item['value']:
                # print(item)
                m =[re.sub('MRT Station|Station','',MRT['name']) for MRT in item['value']] #多个地铁
                # for MRT in item['value']:
                    # m.append(re.sub('MRT Station|Station','',MRT['name']))
                # print('/'.join(m))
                page3_btm[3][1] = makefunc.create_body_text('/'.join(m),color=colors.black) 
            if item['type'] == 'school' and item['value']:
                school =[MRT['name'] for MRT in item['value']]
                page3_btm[2][1] = makefunc.create_body_text('/'.join(school) if len(school)<3 else '/'.join(school[0:3]),color=colors.black)
                # page3_btm[0][1] = item['value'][0]['name']
                # for school in item['value']:
                #     print(school['name'])
    t = Table(page3_btm, style={
    ("FONT", (0, 0), (-1, -1), "msyhbd", 20),
    ("TEXTCOLOR", (0, 0), (0, -1), HexColor('#A68E42')),
    })
    t._argW[1] = 400
    t._argH[2] = 50 
    t._argH[3] = 60 
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 500, 400)
    # 项目 IVT跳转\楼书跳转
    logger.info('============>> Pro Bottom OK !')

    makefunc.addTesxts(fontsize=16,x=10,y=35,text="Source: Google Maps")
    # 页脚
    makefunc.addTesxts(fontsize=16,x=10,y=10,text="Personalised Property Analytics Report • Value-adding Your Home Purchase")
    doc.showPage()  # 保存当前画布页面
    logger.info('============>> PROJECT SUMMARY')

    ######################################################################
    # Page3 项目周边===========================================================================
    # 背景图
    makefunc.background('XHOAPPbg.png')
    if userinfo['logo'] and Config.envs == 'release':
        makefunc.AddRightIMG(Config.imgpath+userinfo['logo'],x=1550,y=770)

    # makefunc.addTesxts(fontsize=60,x=70,y=pagesize[1]-80,text=prodatainfo['projectName'],fontname='msyhbd')
    makefunc.addTesxts(fontsize=40,x=pagesize[0]/2.6,y=pagesize[1]-270,text="LOCATION HIGHLIGHT",color=HexColor('#A68E42'))
    if prodatainfo['snapshotLogo'] and Config.envs == 'release':
        # 地址Google 截图
        makefunc.AddURLImages(Config.imgpath+prodatainfo['snapshotLogo'],x=100,y=100,w=700,h=550) 
    if propdfinfo != [] :
        # 周边截图
        makefunc.AddURLImages(Config.imgpath+propdfinfo[0]['logo'],x=pagesize[0]/2,y=100,w=700,h=550)
    makefunc.addTesxts(fontsize=18,x=100,y=50,text="Source: Google Maps")
    makefunc.addTesxts(fontsize=18,x=pagesize[0]/2,y=50,text="Source: URA Map")
    doc.showPage()  # 保存当前画布页面
    logger.info('============>> LOCATION HIGHLIGHT')

    # Page4 区域出租记录图片 ===========================================================================
    if districtinfo != [] and Config.envs == 'release':
        makefunc.AddURLImages(Config.imgpath+districtinfo[0]['logo'],w=pagesize[0],h=pagesize[1])
        makefunc.addTesxts(fontsize=50,x=10,y=pagesize[1]-80,text='District Pricing (Rental)',color=HexColor('#A68E42'))
        doc.showPage()  # 保存当前画布页面
        logger.info('============>> District Pricing (Rental)')

    # Page5 ===========================================================================

    makefunc.background('XHOAPPbg.png')
    if userinfo['logo'] and Config.envs == 'release':
        makefunc.AddRightIMG(Config.imgpath+userinfo['logo'],x=1550,y=770)

    makefunc.addTesxts(fontsize=40,x=pagesize[0]/3,y=650,text="GUIDE TO FINANCIAL WELLNESS",fontname='ARIALBD',color=HexColor('#A68E42'))
    # 单位统计表
    unittype2 = [
    ["Unit Type",'Price from', "Monthly Installment","Min. Monthly Income \n Required For The Purchase",""],
    ["",'','', "Employee","Self Employed"],
    ]
    for item in unitInfo:
        if item['type'] == None  or item['type'] < 1 or item['type'] > 5:
            continue
        elif item['min_price1'] :
            stage = makefunc.stages_numb(item['min_price1'])
            if stage != '-':
                unittype2.append([str(item['type'])+\
                    " Bedroom",makefunc.priceset(item['min_price1']),\
                        makefunc.stages(item['min_price1'],4), \
                            makefunc.priceset(makefunc.stages_numb(item['min_price1'],4)/0.55), \
                                makefunc.priceset((makefunc.stages_numb(item['min_price1'],4)/0.55)/0.7)])
            else:
                unittype2.append([str(item['type'])+\
                    " Bedroom",makefunc.priceset(item['min_price1']),\
                        makefunc.stages(item['min_price1']), \
                            '---', \
                                '---'])
        else:
            unittype2.append([str(item['type'])+" Bedroom",'---','---','---','---'])
    
    t = Table(unittype2,(pagesize[0]-436)/5,50, style={
    ('SPAN', (-2, 0), (-1,0)), # 合并单元格(列,行)
    ('BACKGROUND',(1,2),(-1,-1), colors.white),
    ('LINEBEFORE', (0, 0), (-1, -1), 0.1 * cm, colors.whitesmoke),
    ('BOX', (0, 0), (-1, -1), 0.1 * cm, colors.whitesmoke),
    ('LINEABOVE', (0, 0), (-1, -1), 0.1 * cm, colors.whitesmoke),
    ('LINEBELOW', (0,0), (-1,-1), 0.1 * cm, colors.whitesmoke),
    # ("FONT", (0, 0), (-1, -1), song, 25),
    ("FONT", (0, 0), (-1, -1), "msyh", 25),
    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    })
    t._argH[0] = 75 
    t._argH[1] = 65 
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 200, 300)
    makefunc.addTesxts(fontsize=16,x=100,y=40,text="Personalised Property Analytics Report Value-adding Your Home Purchase")

    # 页脚
    # makefunc.addTesxts(fontsize=16,x=70,y=30,text=" PERSONALISED PROPERTY ANALYTICS REPORT. | 2022")
    makefunc.addTesxts(fontsize=16,x=300,y=200,text=R"*Calculation based on 30 years tenure, 75% LTV, 3.5% bank interest rate. For your personal financial calculation, please approach our sales person for assistance.")

    doc.showPage()  # 保存当前画布页面
    logger.info('============>>Guide to Financial Wellness')


    # Page7 ===========================================================================

    makefunc.background('XHOAPPbg.png')
    if userinfo['logo'] and Config.envs == 'release':
        makefunc.AddRightIMG(Config.imgpath+userinfo['logo'],x=1550,y=770)

    makefunc.addTesxts(fontsize=40,x=pagesize[0]/3,y=650,text="GUIDE TO FINANCIAL WELLNESS",fontname='ARIALBD',color=HexColor('#A68E42'))
    # 单位统计表
    unittype2 = [
    ["Unit Type",'Price from', "Monthly Installment","Min. Monthly Income \n Required For The Purchase",""],
    ["",'','', "Employee","Self Employed"],
    ]
    for item in unitInfo:
        if item['type'] == None  or item['type'] < 1 or item['type'] > 5:
            continue
        elif item['min_price1'] :
            stage = makefunc.stages_numb(item['min_price1'],4)
            if stage != '-':
                unittype2.append([str(item['type'])+\
                    " Bedroom",makefunc.priceset(item['min_price1']),\
                        makefunc.stages(item['min_price1'],4), \
                            makefunc.priceset(makefunc.stages_numb(item['min_price1'],4)/0.55), \
                                makefunc.priceset((makefunc.stages_numb(item['min_price1'],4)/0.55)/0.7)])
            else:
                unittype2.append([str(item['type'])+\
                    " Bedroom",makefunc.priceset(item['min_price1']),\
                        makefunc.stages(item['min_price1'],2.5), \
                            '---', \
                                '---'])
        else:
            unittype2.append([str(item['type'])+" Bedroom",'---','---','---','---'])
    
    t = Table(unittype2,(pagesize[0]-436)/5,50, style={
    ('SPAN', (-2, 0), (-1,0)), # 合并单元格(列,行)
    ('BACKGROUND',(1,2),(-1,-1), colors.white),
    ('LINEBEFORE', (0, 0), (-1, -1), 0.1 * cm, colors.whitesmoke),
    ('BOX', (0, 0), (-1, -1), 0.1 * cm, colors.whitesmoke),
    ('LINEABOVE', (0, 0), (-1, -1), 0.1 * cm, colors.whitesmoke),
    ('LINEBELOW', (0,0), (-1,-1), 0.1 * cm, colors.whitesmoke),
    # ("FONT", (0, 0), (-1, -1), song, 25),
    ("FONT", (0, 0), (-1, -1), "msyh", 25),
    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    })
    t._argH[0] = 75 
    t._argH[1] = 65 
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 200, 300)
    makefunc.addTesxts(fontsize=16,x=100,y=40,text="Personalised Property Analytics Report Value-adding Your Home Purchase")

    # 页脚
    # makefunc.addTesxts(fontsize=16,x=70,y=30,text=" PERSONALISED PROPERTY ANALYTICS REPORT. | 2022")
    makefunc.addTesxts(fontsize=16,x=300,y=200,text=R"*Calculation based on 30 years tenure, 75% LTV, 2.5% bank interest rate. For your personal financial calculation, please approach our sales person for assistance.")

    doc.showPage()  # 保存当前画布页面
    logger.info('============>>Guide to Financial Wellness')
    


    # Page6 ===========================================================================

    makefunc.background('XHOAPPbg.png')
    if userinfo['logo'] and Config.envs == 'release':
        makefunc.AddRightIMG(Config.imgpath+userinfo['logo'],x=1550,y=770)

    makefunc.addTesxts(fontsize=40,x=pagesize[0]/3,y=650,text="GUIDE TO FINANCIAL WELLNESS",fontname='ARIALBD',color=HexColor('#A68E42'))
    # 单位统计表
    unittype2 = [
    ["Unit Type",'Price from', "Monthly Installment","Min. Monthly Income \n Required For The Purchase",""],
    ["",'','', "Employee","Self Employed"],
    ]
    for item in unitInfo:
        if item['type'] == None  or item['type'] < 1 or item['type'] > 5:
            continue
        elif item['min_price1'] :
            stage = makefunc.stages_numb(item['min_price1'],1.5)
            if stage != '-':
                unittype2.append([str(item['type'])+\
                    " Bedroom",makefunc.priceset(item['min_price1']),\
                        makefunc.stages(item['min_price1'],4), \
                            makefunc.priceset(makefunc.stages_numb(item['min_price1'],4)/0.55), \
                                makefunc.priceset((makefunc.stages_numb(item['min_price1'],4)/0.55)/0.7)])
            else:
                unittype2.append([str(item['type'])+\
                    " Bedroom",makefunc.priceset(item['min_price1']),\
                        makefunc.stages(item['min_price1'],1.5), \
                            '---', \
                                '---'])
        else:
            unittype2.append([str(item['type'])+" Bedroom",'---','---','---','---'])
    
    t = Table(unittype2,(pagesize[0]-436)/5,50, style={
    ('SPAN', (-2, 0), (-1,0)), # 合并单元格(列,行)
    ('BACKGROUND',(1,2),(-1,-1), colors.white),
    ('LINEBEFORE', (0, 0), (-1, -1), 0.1 * cm, colors.whitesmoke),
    ('BOX', (0, 0), (-1, -1), 0.1 * cm, colors.whitesmoke),
    ('LINEABOVE', (0, 0), (-1, -1), 0.1 * cm, colors.whitesmoke),
    ('LINEBELOW', (0,0), (-1,-1), 0.1 * cm, colors.whitesmoke),
    # ("FONT", (0, 0), (-1, -1), song, 25),
    ("FONT", (0, 0), (-1, -1), "msyh", 25),
    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    })
    t._argH[0] = 75 
    t._argH[1] = 65 
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 200, 300)
    makefunc.addTesxts(fontsize=16,x=100,y=40,text="Personalised Property Analytics Report Value-adding Your Home Purchase")

    # 页脚
    # makefunc.addTesxts(fontsize=16,x=70,y=30,text=" PERSONALISED PROPERTY ANALYTICS REPORT. | 2022")
    makefunc.addTesxts(fontsize=16,x=300,y=200,text=R"*Calculation based on 30 years tenure, 75% LTV, 1.5% bank interest rate. For your personal financial calculation, please approach our sales person for assistance.")

    doc.showPage()  # 保存当前画布页面
    logger.info('============>>Guide to Financial Wellness')
    


    # Page8 ===========================================================================
    makefunc.background('9.jpg')
    makefunc.background('XHOAPPbg.png')
    if userinfo['logo'] and Config.envs == 'release':
        makefunc.AddRightIMG(Config.imgpath+userinfo['logo'],x=1550,y=770)

    makefunc.addTesxts(fontsize=46,x=600,y=pagesize[1]-200,text="PROGRESSIVE PAYMENT",fontname='ARIALBD',color=HexColor('#A68E42'))
    # 贷款计算
    unitcalculator = [
        ['','','1 Bedroom','2 Bedroom','3 Bedroom','4 Bedroom','5 Bedroom'],
        ['','','-','-','-','-','-'],
        ['','','-','-','-','-','-'],
        ['','','','','',''],
        ['','','-','-','-','-','-'],
        ['','','-','-','-','-','-'],
        ['','','-','-','-','-','-'],
        ['','','-','-','-','-','-'],
        ['','','','','',''],
        ['','','-','-','-','-','-'],
        ['','','-','-','-','-','-'],
    ]
    for y,data in enumerate(unitcalculator):
        # if item > 1:
        for x,data2 in enumerate(data):
            if x >1:
                BSD = makefunc.priceBSD(unitproce[x-2])
                if y ==1:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]))
                if y ==2:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]*0.75))
                if y ==4:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]*0.05))
                if y ==5:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,BSD)
                if y ==6:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]*0.15))
                if y ==7:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round((unitproce[x-2]*0.2)+BSD))
                if y ==9:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]*0.05)) 
                if y ==10:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(((unitproce[x-2]*0.2)+BSD)+(unitproce[x-2]*0.05)))
    t = Table(unitcalculator,220,32)
    style={
    ('SPAN', (0, 0), (1,0)), # 合并单元格(列,行)
    ('LINEBEFORE', (0, 0), (-1, -1), 0.05 * cm, colors.whitesmoke),



    ("TEXTCOLOR", (0,1), (-1, -1), '#1F5B73'),
    ('BACKGROUND',(2,1),(-1,2), colors.white),
    ('BACKGROUND',(2,4),(-1,6), colors.white),

    # 
    ("TEXTCOLOR", (2,0), (-1, 0), colors.white),
    ('BACKGROUND',(2,0),(-1,0), colors.black),

    # 
    ("FONT", (2,7),(-1,7),'ARIALBD', 16,25),
    ('BACKGROUND',(2,7),(-1,7), "#A68E42"),
    ("TEXTCOLOR", (2,7),(-1,7), colors.white),

    ('BACKGROUND',(2,9),(-1,9), colors.white),

    # 
    ("FONT", (2,10),(-1,10),'ARIALBD', 16,25),
    ('BACKGROUND',(2,10),(-1,10), "#A68E42"),
    ("TEXTCOLOR", (2,10),(-1,10), colors.white),


    ("FONT", (0, 0), (-1, -1),'arial', 16,25),

    ('ALIGN', (1, 0), (-1, -1), 'CENTER')
    }
    t._argW[0] = 100
    t._argW[1] = 200
    t.setStyle(style)
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 90, 382)

    unitcalculator1 = [
        ['','','Outstanding \n Loan','Monthly \n Installment','Outstanding \n Loan','Monthly \n Installment','Outstanding \n Loan','Monthly \n Installment','Outstanding \n Loan','Monthly \n Installment','Outstanding \n Loan','Monthly \n Installment'],
        ['','',makefunc.counts(Symbol,unitproce[0],0.05),makefunc.counts(Symbol,unitproce[0],0.05,0.0035),
                                            makefunc.counts(Symbol,unitproce[1],0.05),makefunc.counts(Symbol,unitproce[1],0.05,0.0035),
                                            makefunc.counts(Symbol,unitproce[2],0.05),makefunc.counts(Symbol,unitproce[2],0.05,0.0035),
                                            makefunc.counts(Symbol,unitproce[3],0.05),makefunc.counts(Symbol,unitproce[3],0.05,0.0035),
                                            makefunc.counts(Symbol,unitproce[4],0.05),makefunc.counts(Symbol,unitproce[4],0.05,0.0035),],
        ['','',makefunc.counts(Symbol,unitproce[0],0.15),makefunc.counts(Symbol,unitproce[0],0.15,0.0035),
                                            makefunc.counts(Symbol,unitproce[1],0.15),makefunc.counts(Symbol,unitproce[1],0.15,0.0035),
                                            makefunc.counts(Symbol,unitproce[2],0.15),makefunc.counts(Symbol,unitproce[2],0.15,0.0035),
                                            makefunc.counts(Symbol,unitproce[3],0.15),makefunc.counts(Symbol,unitproce[3],0.15,0.0035),
                                            makefunc.counts(Symbol,unitproce[4],0.15),makefunc.counts(Symbol,unitproce[4],0.15,0.0035),],
        ['','',makefunc.counts(Symbol,unitproce[0],0.35),makefunc.counts(Symbol,unitproce[0],0.35,0.0035),
                                                    makefunc.counts(Symbol,unitproce[1],0.35),makefunc.counts(Symbol,unitproce[1],0.35,0.0035),
                                                    makefunc.counts(Symbol,unitproce[2],0.35),makefunc.counts(Symbol,unitproce[2],0.35,0.0035),
                                                    makefunc.counts(Symbol,unitproce[3],0.35),makefunc.counts(Symbol,unitproce[3],0.35,0.0035),
                                                    makefunc.counts(Symbol,unitproce[4],0.35),makefunc.counts(Symbol,unitproce[4],0.35,0.0035),],
        ['','','','',''],
        ['','',makefunc.counts(Symbol,unitproce[0],0.6),makefunc.counts(Symbol,unitproce[0],0.6,0.0035),
                            makefunc.counts(Symbol,unitproce[1],0.6),makefunc.counts(Symbol,unitproce[1],0.6,0.0035),
                            makefunc.counts(Symbol,unitproce[2],0.6),makefunc.counts(Symbol,unitproce[2],0.6,0.0035),
                            makefunc.counts(Symbol,unitproce[3],0.6),makefunc.counts(Symbol,unitproce[3],0.6,0.0035),
                            makefunc.counts(Symbol,unitproce[4],0.6),makefunc.counts(Symbol,unitproce[4],0.6,0.0035),],
        ['','',makefunc.counts(Symbol,unitproce[0],0.75),makefunc.counts(Symbol,unitproce[0],0.75,0.0035),
                    makefunc.counts(Symbol,unitproce[1],0.75),makefunc.counts(Symbol,unitproce[1],0.75,0.0035),
                    makefunc.counts(Symbol,unitproce[2],0.75),makefunc.counts(Symbol,unitproce[2],0.75,0.0035),
                    makefunc.counts(Symbol,unitproce[3],0.75),makefunc.counts(Symbol,unitproce[3],0.75,0.0035),
                    makefunc.counts(Symbol,unitproce[4],0.75),makefunc.counts(Symbol,unitproce[4],0.75,0.0035),],

    ]
    logger.info('============>>Guide to Financial Wellness')
    
    unitcalculatortb1 = Table(unitcalculator1,110,35, style={
    ('SPAN', (0, 0), (1,0)), # 合并单元格(列,行)
    ('LINEBEFORE', (0, 0), (-1, -1), 0.05 * cm, colors.whitesmoke),
    ("FONT", (0, 0), (-1, -1), 'arial', 12),
    ('FONTNAME', (0,0), (-1,0), 'Courier-Bold'),
    ('TEXTCOLOR',(2,0),(-1,0), colors.white),
    ('BACKGROUND',(2,0),(-1,0), colors.black),
    ("FONT", (2,0),(-1,0), 'arial', 14),

    ('BACKGROUND',(2,1),(-1,3), colors.white),
    ('BACKGROUND',(2,5),(-1,6), colors.white),
    ("TEXTCOLOR", (0,1), (-1, -1), '#1F5B73'),
    ('ALIGN', (1, 0), (-1, -1), 'CENTER')
    })
    unitcalculatortb1._argH[0] = 50
    unitcalculatortb1._argW[0] = 100
    unitcalculatortb1._argW[1] = 200
    unitcalculatortb1.wrapOn(doc, 0, 0)
    unitcalculatortb1.drawOn(doc, 90, 100)

    makefunc.AddImages('left_report.png',x=90,y=95,w=280,h=595)
    # 免责声明
    makefunc.addTesxts(fontsize=12,x=100,y=40,text="Personalised Property Analytics Report Value-adding Your Home Purchase")

    makefunc.addTesxts(fontsize=16,x=600,y=50,text="*Calculation based on 30 years tenure, 3.5% bank interest rate. For your personal")
    makefunc.addTesxts(fontsize=16,x=620,y=30,text=" financial calculation, please approach our salesperson for assistance.")
    doc.showPage()  # 保存当前画布页面
    logger.info('============>>PROGRESSIVE PAYMENT')


    # Page9 ===========================================================================
    makefunc.background('9.jpg')
    makefunc.background('XHOAPPbg.png')
    if userinfo['logo'] and Config.envs == 'release':
        makefunc.AddRightIMG(Config.imgpath+userinfo['logo'],x=1550,y=770)

    makefunc.addTesxts(fontsize=46,x=600,y=pagesize[1]-200,text="PROGRESSIVE PAYMENT",fontname='ARIALBD',color=HexColor('#A68E42'))
    # 贷款计算
    unitcalculator = [
        ['','','1 Bedroom','2 Bedroom','3 Bedroom','4 Bedroom','5 Bedroom'],
        ['','','-','-','-','-','-'],
        ['','','-','-','-','-','-'],
        ['','','','','',''],
        ['','','-','-','-','-','-'],
        ['','','-','-','-','-','-'],
        ['','','-','-','-','-','-'],
        ['','','-','-','-','-','-'],
        ['','','','','',''],
        ['','','-','-','-','-','-'],
        ['','','-','-','-','-','-'],
    ]
    for y,data in enumerate(unitcalculator):
        # if item > 1:
        for x,data2 in enumerate(data):
            if x >1:
                BSD = makefunc.priceBSD(unitproce[x-2])
                if y ==1:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]))
                if y ==2:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]*0.75))
                if y ==4:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]*0.05))
                if y ==5:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,BSD)
                if y ==6:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]*0.15))
                if y ==7:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round((unitproce[x-2]*0.2)+BSD))
                if y ==9:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]*0.05)) 
                if y ==10:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(((unitproce[x-2]*0.2)+BSD)+(unitproce[x-2]*0.05)))
    t = Table(unitcalculator,220,32)
    style={
    ('SPAN', (0, 0), (1,0)), # 合并单元格(列,行)
    ('LINEBEFORE', (0, 0), (-1, -1), 0.05 * cm, colors.whitesmoke),

    ("TEXTCOLOR", (0,1), (-1, -1), '#1F5B73'),
    ('BACKGROUND',(2,1),(-1,2), colors.white),
    ('BACKGROUND',(2,4),(-1,6), colors.white),

    # 
    ("TEXTCOLOR", (2,0), (-1, 0), colors.white),
    ('BACKGROUND',(2,0),(-1,0), colors.black),

    # 
    ("FONT", (2,7),(-1,7),'ARIALBD', 16,25),
    ('BACKGROUND',(2,7),(-1,7), "#A68E42"),
    ("TEXTCOLOR", (2,7),(-1,7), colors.white),

    ('BACKGROUND',(2,9),(-1,9), colors.white),

    # 
    ("FONT", (2,10),(-1,10),'ARIALBD', 16,25),
    ('BACKGROUND',(2,10),(-1,10), "#A68E42"),
    ("TEXTCOLOR", (2,10),(-1,10), colors.white),

    ("FONT", (0, 0), (-1, -1),'arial', 16,25),

    ('ALIGN', (1, 0), (-1, -1), 'CENTER')
    }
    t._argW[0] = 100
    t._argW[1] = 200
    t.setStyle(style)
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 90, 382)

    unitcalculator1 = [
        ['','','Outstanding \n Loan','Monthly \n Installment','Outstanding \n Loan','Monthly \n Installment','Outstanding \n Loan','Monthly \n Installment','Outstanding \n Loan','Monthly \n Installment','Outstanding \n Loan','Monthly \n Installment'],
        ['','',makefunc.counts(Symbol,unitproce[0],0.05),makefunc.counts(Symbol,unitproce[0],0.05,0.0025),
                                            makefunc.counts(Symbol,unitproce[1],0.05),makefunc.counts(Symbol,unitproce[1],0.05,0.0025),
                                            makefunc.counts(Symbol,unitproce[2],0.05),makefunc.counts(Symbol,unitproce[2],0.05,0.0025),
                                            makefunc.counts(Symbol,unitproce[3],0.05),makefunc.counts(Symbol,unitproce[3],0.05,0.0025),
                                            makefunc.counts(Symbol,unitproce[4],0.05),makefunc.counts(Symbol,unitproce[4],0.05,0.0025),],
        ['','',makefunc.counts(Symbol,unitproce[0],0.15),makefunc.counts(Symbol,unitproce[0],0.15,0.0025),
                                            makefunc.counts(Symbol,unitproce[1],0.15),makefunc.counts(Symbol,unitproce[1],0.15,0.0025),
                                            makefunc.counts(Symbol,unitproce[2],0.15),makefunc.counts(Symbol,unitproce[2],0.15,0.0025),
                                            makefunc.counts(Symbol,unitproce[3],0.15),makefunc.counts(Symbol,unitproce[3],0.15,0.0025),
                                            makefunc.counts(Symbol,unitproce[4],0.15),makefunc.counts(Symbol,unitproce[4],0.15,0.0025),],
        ['','',makefunc.counts(Symbol,unitproce[0],0.35),makefunc.counts(Symbol,unitproce[0],0.35,0.0025),
                                                    makefunc.counts(Symbol,unitproce[1],0.35),makefunc.counts(Symbol,unitproce[1],0.35,0.0025),
                                                    makefunc.counts(Symbol,unitproce[2],0.35),makefunc.counts(Symbol,unitproce[2],0.35,0.0025),
                                                    makefunc.counts(Symbol,unitproce[3],0.35),makefunc.counts(Symbol,unitproce[3],0.35,0.0025),
                                                    makefunc.counts(Symbol,unitproce[4],0.35),makefunc.counts(Symbol,unitproce[4],0.35,0.0025),],
        ['','','','',''],
        ['','',makefunc.counts(Symbol,unitproce[0],0.6),makefunc.counts(Symbol,unitproce[0],0.6,0.0025),
                            makefunc.counts(Symbol,unitproce[1],0.6),makefunc.counts(Symbol,unitproce[1],0.6,0.0025),
                            makefunc.counts(Symbol,unitproce[2],0.6),makefunc.counts(Symbol,unitproce[2],0.6,0.0025),
                            makefunc.counts(Symbol,unitproce[3],0.6),makefunc.counts(Symbol,unitproce[3],0.6,0.0025),
                            makefunc.counts(Symbol,unitproce[4],0.6),makefunc.counts(Symbol,unitproce[4],0.6,0.0025),],
        ['','',makefunc.counts(Symbol,unitproce[0],0.75),makefunc.counts(Symbol,unitproce[0],0.75,0.0025),
                    makefunc.counts(Symbol,unitproce[1],0.75),makefunc.counts(Symbol,unitproce[1],0.75,0.0025),
                    makefunc.counts(Symbol,unitproce[2],0.75),makefunc.counts(Symbol,unitproce[2],0.75,0.0025),
                    makefunc.counts(Symbol,unitproce[3],0.75),makefunc.counts(Symbol,unitproce[3],0.75,0.0025),
                    makefunc.counts(Symbol,unitproce[4],0.75),makefunc.counts(Symbol,unitproce[4],0.75,0.0025),],

    ]
    logger.info('============>>Guide to Financial Wellness')
    
    unitcalculatortb1 = Table(unitcalculator1,110,35, style={
    ('SPAN', (0, 0), (1,0)), # 合并单元格(列,行)
    ('LINEBEFORE', (0, 0), (-1, -1), 0.05 * cm, colors.whitesmoke),
    ("FONT", (0, 0), (-1, -1), 'arial', 12),
    ('FONTNAME', (0,0), (-1,0), 'Courier-Bold'),
    ('TEXTCOLOR',(2,0),(-1,0), colors.white),
    ('BACKGROUND',(2,0),(-1,0), colors.black),
    ("FONT", (2,0),(-1,0), 'arial', 14),

    ('BACKGROUND',(2,1),(-1,3), colors.white),
    ('BACKGROUND',(2,5),(-1,6), colors.white),
    ("TEXTCOLOR", (0,1), (-1, -1), '#1F5B73'),
    ('ALIGN', (1, 0), (-1, -1), 'CENTER')
    })
    unitcalculatortb1._argH[0] = 50
    unitcalculatortb1._argW[0] = 100
    unitcalculatortb1._argW[1] = 200
    unitcalculatortb1.wrapOn(doc, 0, 0)
    unitcalculatortb1.drawOn(doc, 90, 100)

    makefunc.AddImages('left_report.png',x=90,y=95,w=280,h=595)
    # 免责声明
    makefunc.addTesxts(fontsize=12,x=100,y=40,text="Personalised Property Analytics Report Value-adding Your Home Purchase")

    makefunc.addTesxts(fontsize=16,x=600,y=50,text="*Calculation based on 30 years tenure, 2.5% bank interest rate. For your personal")
    makefunc.addTesxts(fontsize=16,x=620,y=30,text=" financial calculation, please approach our salesperson for assistance.")
    doc.showPage()  # 保存当前画布页面
    logger.info('============>>PROGRESSIVE PAYMENT')



    # Page10 ===========================================================================
    makefunc.background('9.jpg')
    makefunc.background('XHOAPPbg.png')
    if userinfo['logo'] and Config.envs == 'release':
        makefunc.AddRightIMG(Config.imgpath+userinfo['logo'],x=1550,y=770)

    makefunc.addTesxts(fontsize=46,x=600,y=pagesize[1]-200,text="PROGRESSIVE PAYMENT",fontname='ARIALBD',color=HexColor('#A68E42'))
    # 贷款计算
    unitcalculator = [
        ['','','1 Bedroom','2 Bedroom','3 Bedroom','4 Bedroom','5 Bedroom'],
        ['','','-','-','-','-','-'],
        ['','','-','-','-','-','-'],
        ['','','','','',''],
        ['','','-','-','-','-','-'],
        ['','','-','-','-','-','-'],
        ['','','-','-','-','-','-'],
        ['','','-','-','-','-','-'],
        ['','','','','',''],
        ['','','-','-','-','-','-'],
        ['','','-','-','-','-','-'],
    ]
    for y,data in enumerate(unitcalculator):
        # if item > 1:
        for x,data2 in enumerate(data):
            if x >1:
                BSD = makefunc.priceBSD(unitproce[x-2])
                if y ==1:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]))
                if y ==2:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]*0.75))
                if y ==4:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]*0.05))
                if y ==5:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,BSD)
                if y ==6:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]*0.15))
                if y ==7:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round((unitproce[x-2]*0.2)+BSD))
                if y ==9:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(unitproce[x-2]*0.05)) 
                if y ==10:
                    unitcalculator[y][x] = makefunc.testNan(Symbol,round(((unitproce[x-2]*0.2)+BSD)+(unitproce[x-2]*0.05)))
    t = Table(unitcalculator,220,32)
    style={
    ('SPAN', (0, 0), (1,0)), # 合并单元格(列,行)
    ('LINEBEFORE', (0, 0), (-1, -1), 0.05 * cm, colors.whitesmoke),



    ("TEXTCOLOR", (0,1), (-1, -1), '#1F5B73'),
    ('BACKGROUND',(2,1),(-1,2), colors.white),
    ('BACKGROUND',(2,4),(-1,6), colors.white),

    # 
    ("TEXTCOLOR", (2,0), (-1, 0), colors.white),
    ('BACKGROUND',(2,0),(-1,0), colors.black),

    # 
    ("FONT", (2,7),(-1,7),'ARIALBD', 16,25),
    ('BACKGROUND',(2,7),(-1,7), "#A68E42"),
    ("TEXTCOLOR", (2,7),(-1,7), colors.white),

    ('BACKGROUND',(2,9),(-1,9), colors.white),

    # 
    ("FONT", (2,10),(-1,10),'ARIALBD', 16,25),
    ('BACKGROUND',(2,10),(-1,10), "#A68E42"),
    ("TEXTCOLOR", (2,10),(-1,10), colors.white),


    ("FONT", (0, 0), (-1, -1),'arial', 16,25),

    ('ALIGN', (1, 0), (-1, -1), 'CENTER')
    }
    t._argW[0] = 100
    t._argW[1] = 200
    t.setStyle(style)
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 90, 382)

    unitcalculator1 = [
        ['','','Outstanding \n Loan','Monthly \n Installment','Outstanding \n Loan','Monthly \n Installment','Outstanding \n Loan','Monthly \n Installment','Outstanding \n Loan','Monthly \n Installment','Outstanding \n Loan','Monthly \n Installment'],
        ['','',makefunc.counts(Symbol,unitproce[0],0.05),makefunc.counts(Symbol,unitproce[0],0.05,0.0015),
                                            makefunc.counts(Symbol,unitproce[1],0.05),makefunc.counts(Symbol,unitproce[1],0.05,0.0015),
                                            makefunc.counts(Symbol,unitproce[2],0.05),makefunc.counts(Symbol,unitproce[2],0.05,0.0015),
                                            makefunc.counts(Symbol,unitproce[3],0.05),makefunc.counts(Symbol,unitproce[3],0.05,0.0015),
                                            makefunc.counts(Symbol,unitproce[4],0.05),makefunc.counts(Symbol,unitproce[4],0.05,0.0015),],
        ['','',makefunc.counts(Symbol,unitproce[0],0.15),makefunc.counts(Symbol,unitproce[0],0.15,0.0015),
                                            makefunc.counts(Symbol,unitproce[1],0.15),makefunc.counts(Symbol,unitproce[1],0.15,0.0015),
                                            makefunc.counts(Symbol,unitproce[2],0.15),makefunc.counts(Symbol,unitproce[2],0.15,0.0015),
                                            makefunc.counts(Symbol,unitproce[3],0.15),makefunc.counts(Symbol,unitproce[3],0.15,0.0015),
                                            makefunc.counts(Symbol,unitproce[4],0.15),makefunc.counts(Symbol,unitproce[4],0.15,0.0015),],
        ['','',makefunc.counts(Symbol,unitproce[0],0.35),makefunc.counts(Symbol,unitproce[0],0.35,0.0015),
                                                    makefunc.counts(Symbol,unitproce[1],0.35),makefunc.counts(Symbol,unitproce[1],0.35,0.0015),
                                                    makefunc.counts(Symbol,unitproce[2],0.35),makefunc.counts(Symbol,unitproce[2],0.35,0.0015),
                                                    makefunc.counts(Symbol,unitproce[3],0.35),makefunc.counts(Symbol,unitproce[3],0.35,0.0015),
                                                    makefunc.counts(Symbol,unitproce[4],0.35),makefunc.counts(Symbol,unitproce[4],0.35,0.0015),],
        ['','','','',''],
        ['','',makefunc.counts(Symbol,unitproce[0],0.6),makefunc.counts(Symbol,unitproce[0],0.6,0.0015),
                            makefunc.counts(Symbol,unitproce[1],0.6),makefunc.counts(Symbol,unitproce[1],0.6,0.0015),
                            makefunc.counts(Symbol,unitproce[2],0.6),makefunc.counts(Symbol,unitproce[2],0.6,0.0015),
                            makefunc.counts(Symbol,unitproce[3],0.6),makefunc.counts(Symbol,unitproce[3],0.6,0.0015),
                            makefunc.counts(Symbol,unitproce[4],0.6),makefunc.counts(Symbol,unitproce[4],0.6,0.0015),],
        ['','',makefunc.counts(Symbol,unitproce[0],0.75),makefunc.counts(Symbol,unitproce[0],0.75,0.0015),
                    makefunc.counts(Symbol,unitproce[1],0.75),makefunc.counts(Symbol,unitproce[1],0.75,0.0015),
                    makefunc.counts(Symbol,unitproce[2],0.75),makefunc.counts(Symbol,unitproce[2],0.75,0.0015),
                    makefunc.counts(Symbol,unitproce[3],0.75),makefunc.counts(Symbol,unitproce[3],0.75,0.0015),
                    makefunc.counts(Symbol,unitproce[4],0.75),makefunc.counts(Symbol,unitproce[4],0.75,0.0015),],

    ]
    logger.info('============>>Guide to Financial Wellness')
    
    unitcalculatortb1 = Table(unitcalculator1,110,35, style={
    ('SPAN', (0, 0), (1,0)), # 合并单元格(列,行)
    ('LINEBEFORE', (0, 0), (-1, -1), 0.05 * cm, colors.whitesmoke),
    ("FONT", (0, 0), (-1, -1), 'arial', 12),
    ('FONTNAME', (0,0), (-1,0), 'Courier-Bold'),
    ('TEXTCOLOR',(2,0),(-1,0), colors.white),
    ('BACKGROUND',(2,0),(-1,0), colors.black),
    ("FONT", (2,0),(-1,0), 'arial', 14),

    ('BACKGROUND',(2,1),(-1,3), colors.white),
    ('BACKGROUND',(2,5),(-1,6), colors.white),
    ("TEXTCOLOR", (0,1), (-1, -1), '#1F5B73'),
    ('ALIGN', (1, 0), (-1, -1), 'CENTER')
    })
    unitcalculatortb1._argH[0] = 50
    unitcalculatortb1._argW[0] = 100
    unitcalculatortb1._argW[1] = 200
    unitcalculatortb1.wrapOn(doc, 0, 0)
    unitcalculatortb1.drawOn(doc, 90, 100)

    makefunc.AddImages('left_report.png',x=90,y=95,w=280,h=595)
    # 免责声明
    makefunc.addTesxts(fontsize=12,x=100,y=40,text="Personalised Property Analytics Report Value-adding Your Home Purchase")

    makefunc.addTesxts(fontsize=16,x=600,y=50,text="*Calculation based on 30 years tenure, 1.5% bank interest rate. For your personal")
    makefunc.addTesxts(fontsize=16,x=620,y=30,text=" financial calculation, please approach our salesperson for assistance.")
    doc.showPage()  # 保存当前画布页面
    logger.info('============>>PROGRESSIVE PAYMENT')


    # Page12 ===========================================================================
    makefunc.background('XHOAPPbg2.png')
    makefunc.AddImages('XHOAPP14right.jpg',x=pagesize[0]-550,y=160,w=430,h=536)
    # 项目单位总数
    makefunc.addTesxts(fontsize=40,x=pagesize[0]-535,y=610,text=str(prodatainfo['unitsNum']),fontname='ARIALBD',color=colors.white)
    # 项目已释放单位数
    makefunc.addTesxts(fontsize=40,x=pagesize[0]-535,y=410,text=str(int(prodatainfo['unitsNum'])-int(prodatainfo['released'])),fontname='ARIALBD',color=colors.white)
    # 项目已售单位数
    makefunc.addTesxts(fontsize=40,x=pagesize[0]-535,y=215,text=str(prodatainfo['sold']),fontname='ARIALBD',color=colors.white)

    makefunc.addTesxts(fontsize=60,x=200,y=pagesize[1]-190,text="SALES TRANSACTIONS",fontname='ARIALBD',color=HexColor('#A68E42'))

    # 单位销量统计
    unittransactions = [
        ['Date','Floor','Size(Sqft)','Price','Price(psf)'],
        ['','','','',''],
        ['','','','',''],
        ['','','','',''],
        ['','','','',''],
        ['','','','',''],
        ['','','','',''],
        ['','','','',''],
        ['','','','',''],
        ['','','','',''],
        ['','','','',''],
    ]
    for i,item in enumerate(dealInfo):
        date = '-'
        unitprice = 0
        transactionPrice = 0
        if item['transactionDate']:
            date = time.strftime('%Y-%m',time.localtime(item['transactionDate']/1000))
        if item['price']:
            unitprice = item['price']
        if item['transactionPrice']:
            transactionPrice = item['transactionPrice']
        unittransactions[i+1] =  [date,item['floor'],item['area'],makefunc.priceset(transactionPrice),makefunc.priceset(unitprice)]
        # unittransactions.append([date,item['floor'],item['area'],makefunc.priceset(transactionPrice),makefunc.priceset(unitprice),])
    
    t = Table(unittransactions,(pagesize[0]-560)/6,60, style={
    # ("FONT", (0, 0), (-1, -1), song, 22),
    ("FONT", (0, 0), (-1, -1), 'arial', 22),
    ('LINEABOVE', (0, 0), (-1, -1), 0.05 * cm, colors.whitesmoke),
    ('LINEBELOW', (0,-1), (-1,-1), 0.05 * cm, colors.whitesmoke),
    ('BACKGROUND',(0,0),(-1,0), colors.black),
    ('TEXTCOLOR',(0,0),(-1,0), colors.white),
    ('BACKGROUND',(0,1),(-1,-1), colors.white),
    ("TEXTCOLOR", (0,1), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    })
    t._argH[0] = 35
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 100, 85)
    logger.info('============>>transactionDate')
    doc.showPage()  # 保存当前画布页面

    # Page8 ===========================================================================
    makefunc.background('XHOAPPbg2.png')

    # New Project Sales Progress
    # Core Central Region (CCR)
    makefunc.addTesxts(fontsize=40,x=pagesize[0]-600,y=500,text="New Project Sales Progress",color=HexColor('#A68E42'))
    makefunc.addTesxts(fontsize=25,x=pagesize[0]-600,y=450,text="Core Central Region (CCR)")
    
    makefunc.make_drawing(CCRinfo,make_drawing_color=HexColor('#A68E42')).drawOn(doc,0,125)
    makefunc.AddImages('XHOAPPtotal_sold.png',x=pagesize[0]-600,y=700,w=60,h=50)

    doc.showPage()  # 保存当前画布页面
    logger.info('============>>Core Central Region (CCR)')

    # Page9 ===========================================================================
    makefunc.background('XHOAPPbg2.png')

    # New Project Sales Progress
    # Core Central Region (RCR)
    makefunc.addTesxts(fontsize=40,x=pagesize[0]-600,y=500,text="New Project Sales Progress",color=HexColor('#A68E42'))
    makefunc.addTesxts(fontsize=25,x=pagesize[0]-600,y=450,text="Core Central Region (RCR)")
    makefunc.make_drawing(RCRinfo,make_drawing_color=HexColor('#A68E42')).drawOn(doc,0,125)
    makefunc.AddImages('XHOAPPtotal_sold.png',x=pagesize[0]-600,y=700,w=60,h=50)
    doc.showPage()  # 保存当前画布页面
    logger.info('============>>Core Central Region (RCR)')

    # Page10 ===========================================================================
    makefunc.background('XHOAPPbg2.png')


    # New Project Sales Progress
    # Core Central Region (OCR)
    makefunc.make_drawing(OCRinfo,make_drawing_color=HexColor('#A68E42')).drawOn(doc,0,125)
    makefunc.addTesxts(fontsize=40,x=pagesize[0]-600,y=500,text="New Project Sales Progress",color=HexColor('#A68E42'))
    makefunc.addTesxts(fontsize=25,x=pagesize[0]-600,y=450,text="Core Central Region (OCR)")
    makefunc.AddImages('XHOAPPtotal_sold.png',x=pagesize[0]-600,y=700,w=60,h=50)
    doc.showPage()  # 保存当前画布页面
    logger.info('============>>Core Central Region (OCR)')



    # Page11 ===========================================================================
    makefunc.background('XHOAPPbg3.png')
    # makefunc.addTesxts(fontsize=40,x=pagesize[0]/4,y=800,text="DISCLAIMER")
    # logger.info(gettime.getDates())
    text_n1 = """
    While Xhorizon has endeavoured to ensure that the information and materials
    contained herein are accurate and up to date as at [{0}], Xhorizon is 
    not responsible for any errors or omissions,or for the results obtained from 
    their use or the reliance placed on them.All information is provided 'as is',with 
    no guarantee of completeness, and accuracy. In no event will Xhorizon and/or
    salespersons thereof be liable in contract or in tort,to any party for any decision
    made or action taken in reliance on the information in this document or for any
    direct, indirect, consequential, special or similar damages.
    """.format(str(gettime.getDates()))
    data_text = [['DISCLAIMER'],[makefunc.create_body_text(text_n1,font_size=36,color=colors.black,leading=46)]]
    # makefunc.addTesxts(fontsize=40,x=pagesize[0]/5,y=700,text=)
    t = Table(data_text, style={
    ('TEXTCOLOR',(0,0),(-1,-1), colors.black),
    ("FONT", (0, 0), (-1, -1), 'arial', 40,65),
    # ('BACKGROUND',(0,0),(-1,0), colors.darkslateblue),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), 
    })
    t._argW[0] = pagesize[0]-400
    t.wrapOn(doc, 0, 0)
    t.drawOn(doc, 200, 250)

    doc.showPage()  # 保存当前画布页面
    doc.save()  # 保存文件并关闭画布
    # time.sleep(3)
    return returnPath
    # return savepath 





