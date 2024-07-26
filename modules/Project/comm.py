from hashlib import md5
# from importlib_metadata import re
# from modules import Project
from reportlab.lib.colors import HexColor
from reportlab.graphics.shapes import Drawing
from reportlab.platypus import Paragraph,Table,Image as im
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.lib.formatters import DecimalFormatter
from reportlab.lib.styles import getSampleStyleSheet
from fastapi import HTTPException
from PIL import Image
import os,time,math,datetime
import requests,json
from io import BytesIO
from comm.logger import logger
from reportlab.lib.utils import ImageReader
from config import Config

class getDatetimes():
    def __init__(self):
        ...
    def Years(self):
        return datetime.datetime.now().strftime('%Y')
    def getDate(self):
        return datetime.datetime.now().strftime('%Y%m%d')
    def getDates(self):
        return datetime.datetime.now().strftime('%d/%m/%Y')
    def determine_am_pm(self,time_str):
        # Split the time string into hours and minutes
        hours, minutes = map(int, time_str.split(':'))

        # Determine if it's AM or PM
        if hours == 0 or (hours >= 1 and hours < 12):
            return "%s AM"%time_str
        elif hours == 12 or (hours >= 13 and hours <= 23):
            return "%s PM"%time_str
        else:
            return "Invalid time"

class getAPI(): # 网络请求
    def __init__(self):
        ...
    def setmd5(self,data,pro):
        # logger.info('Md5加密',data)
        a = list(data.items()) # 转列表
        a.sort(key=lambda x:x[0],reverse=False) # 排序
        keys = ''
        for item in a:
            if item[1] :
                keys+= str(item[1])
            else:
                keys+= ''
        if pro == "ReLoSG": # 处理不同项目标识不同
            keys = keys+'relo'
        else:
            keys = keys+'c1d65f3667324592a071ebec5038f38c'

        signature = md5(keys.encode(encoding='UTF-8')).hexdigest() #加密
        logger.info('signature=======>{}'.format(signature))
        # print(signature)
        return signature
    def requsetAPI(self,path,params,item='EcoProp'):
        params['signature'] = self.setmd5(params,item)
        res = requests.get(path,params=params)
        value = json.loads(res.text)
        # logger.info('data=======>{0}'.format(value['datas']))
        if int(value['code']) == 0:
            # eval(re.sub('None','\'\'',str(value['datas']))) # 去除None值
            if item == 'ReLoSG':
                # logger.info('data=======>{0}'.format(value['data']))
                return value['data']
            else:
                # logger.info('data=======>{0}'.format(value['datas']))
                return value['datas']
        else:
            raise HTTPException(status_code=404, detail="参数错误")
        
    def requsetAPI_POST(self,path,params,item='EcoProp'):
        params['signature'] = self.setmd5(params,item)
        # print('==========>',params)
        res = requests.post(path,data=params)
        value = json.loads(res.text)
        print(value)
        if int(value['code']) == 0:
            if item == 'ReLoSG':
                # logger.info('data=======>{0}'.format(value['data']))
                return value['data']
            else:
                # logger.info('data=======>{0}'.format(value['datas']))
                return value['datas']
        else:
            raise HTTPException(status_code=404, detail="参数错误")




class MakeReportlab():
    def __init__(self, doc,imgpaths,pagesize,S='$'):
        self.doc = doc
        self.imgpaths = imgpaths
        self.pagesize = pagesize
        # 中文宋体
        self.song = "simsun"
        self.S = S
        pdfmetrics.registerFont(TTFont(self.song, "simsun.ttc"))
        # pdfmetrics.registerFont(TTFont('ARIALBD','ARIALBD.TTF')) #注册字体
        pdfmetrics.registerFont(TTFont('arial','arial.ttf')) #注册字体
        pdfmetrics.registerFont(TTFont('msyh','msyh.ttf')) #注册字体
        pdfmetrics.registerFont(TTFont('msyhbd','msyhbd.ttf')) #注册字体
    
    def priceBSD(self,price):
        ...
        BSD = 0
        # if price >180000:
        #     BSD +=1800
        # if price >360000:
        #     BSD+=3600
        # if price >640000:
        #     BSD+=19200
        # if price >1000000:
        #     BSD += (price-1000000) * 0.04
        if price > 180000 and price <= 360000:
            BSD = 1800 +(price-180000)*0.02
        elif price > 360000 and price <= 1000000:
            BSD = 5400 + (price-360000)*0.03
        elif price > 1000000 and price <= 1500000:
            BSD = 24600 + (price-1000000)*0.04
        elif price >1500000 and price <= 3000000:
            BSD = 44600 + (price-1500000)*0.05
        elif price > 3000000:
            BSD = 119600 + (price-3000000)*0.06
        # print(BSD)
        return round(BSD)
        
    def testNan(self,S,price):
        if price >0:
            return S+format(price,',')
        else:
            return '-'
    def setmd5(self,data):
        # logger.info('Md5加密',data)
        a = list(data.items()) # 转列表
        a.sort(key=lambda x:x[0],reverse=False) # 排序
        keys = ''
        for item in a:
            keys+= item[1]
        keys = keys+'c1d65f3667324592a071ebec5038f38c'
        signature = md5(keys.encode(encoding='UTF-8')).hexdigest() #加密
        # print(signature)
        return signature
    def requsetAPI(self,path,params):
        params['signature'] = self.setmd5(params)
        res = requests.get(path,params=params)
        value = json.loads(res.text)
        # print(value)
        if value['code'] == '0':
            return value['datas']
        else:
            raise HTTPException(status_code=404, detail="参数错误")

    def requsetImg(self,path):
        # 获取网络图片内容
        # print(path)
        response = requests.get(path)
        # print(response)
        response = response.content
        # print(response)
        BytesIOObj = BytesIO()
        BytesIOObj.write(response)
        # print(BytesIOObj)
        return BytesIOObj
    def addBagecolor(self,x=0,y=0,w=0,h=0,color='0xEBFDFF'):
        # 添加色块
        self.doc.setFillColor(HexColor(color)) # RGB
        self.doc.rect(x,y,w,h,stroke=0, fill=1) #x,y,w,h,stroke=边框,fill=颜色透明度



    def img_circle(self,img_path):
        # 图片切圆角
        im = Image.open(img_path).convert("RGBA")
        im.convert('RGB')
        ima = im.resize((320, 320))
        size = ima.size
        # 要使用圆形，所以使用刚才处理好的正方形的图片
        r2 = min(size[0], size[1])
        if size[0] != size[1]:
            ima = ima.resize((r2, r2), Image.ANTIALIAS)
        # 最后生成圆的半径
        r3 = int(r2/2)
        imb = Image.new('RGBA', (r3*2, r3*2),(255,255,255,0))
        pima = ima.load() # 像素的访问对象
        pimb = imb.load()
        r = float(r2/2) #圆心横坐标
        for i in range(r2):
            for j in range(r2):
                lx = abs(i-r) #到圆心距离的横坐标
                ly = abs(j-r) #到圆心距离的纵坐标
                l = (pow(lx,2) + pow(ly,2))** 0.5 # 三角函数 半径
                if l < r3:
                    pimb[i-(r-r3),j-(r-r3)] = pima[i,j]

        return imb

    def AddImages(self,imgName,x=0,y=0,w=None,h=None):
        """
        向文档添加图片
        imgName :文件名称
        x，y:图片起始坐标
        w,h : 图片大小
        """
        I_path = os.path.join(self.imgpaths,imgName)
        if not w or not h:
            image = Image.open(I_path)
            self.doc.drawImage(I_path,x,y,width=image.width,height=image.height,mask='auto')
        else:
            self.doc.drawImage(I_path,x,y,width=w,height=h,mask='auto') #mask=auto 背景透明
    
    def AddRightIMG(self,imgName,x=0,y=0):
        # 圆形图片
        imgdata = self.img_circle(self.requsetImg(imgName))
        self.doc.drawImage(ImageReader(imgdata),x,y,width=120,height=120,mask='auto')

    def AddURLImages(self,imgName,x=0,y=0,w=None,h=None):
        """
        向文档添加网络图片
        imgName :文件名称
        x，y:图片起始坐标
        w,h : 图片大小
        """

        I_path = os.path.join(imgName)
        # print(I_path)

        if not w or not h:
            # print(555555555)
            image = Image.open(self.requsetImg(imgName))
            imgdata = self.requsetImg(imgName)  

            # print(333333333)
            self.doc.drawImage(ImageReader(imgdata),x,y,width=image.width,height=image.height,mask='auto')
        else:
            # print(444444444444)
            # image = Image.open(self.requsetImg(imgName))
            imgdata = self.requsetImg(imgName)  
            # fig.savefig(imgdata, format='png')
            # imgdata.seek(0)
            # imgdata = ImageReader(imgdata)
            # print(image)
            self.doc.drawImage(ImageReader(imgdata),x,y,width=w,height=h,mask='auto') #mask=auto 背景透明

    def ImageAdaptive(self,imgName,x=0,y=0,w=None,h=None):
        """
        图片自适应不拉伸
        w,h 最大宽高
        """
        # I_path = os.path.join(imgName)
        img = Image.open(self.requsetImg(imgName))
        imgs = self.requsetImg(imgName)
        imgw,imgh = img.size
        if w < imgw :
            new = imgw - w
            sizes = imgw/new
            imgw = imgw-(imgw/sizes)
            imgh = imgh-(imgh/sizes)
        if h < imgh:
            new = imgh - h
            sizes = imgh/new
            imgw = imgw-(imgw/sizes)
            imgh = imgh-(imgh/sizes)
        self.doc.drawImage(ImageReader(imgs),x,y,width=imgw,height=imgh,mask='auto') #mask=auto 背景透明

    def AddLogo(self):
        # LOGO
        # self.AddImages('pndlogo.jpg',x=0,y=self.pagesize[1]-90,w=200,h=80) 
        self.AddImages('huttonslogo.png',x=self.pagesize[0]-318,y=self.pagesize[1]-110,w=300,h=100) 
    def AddLogoleft(self):
        # LOGO
        self.AddImages('pndlogo.jpg',x=0,y=self.pagesize[1]-90,w=200,h=80) 
        # self.AddImages('huttonslogo.png',x=self.pagesize[0]-318,y=self.pagesize[1]-110,w=300,h=100) 

    def background(self,imgName):
        '''页面背景图片'''
        I_path = os.path.join(self.imgpaths,imgName)
        # print(I_path)
        self.doc.drawImage(I_path,0,0,width=self.pagesize[0],height=self.pagesize[1],mask='auto') #mask=auto 背景透明

    def addTesxts(self,fontsize=16,x=0,y=0,text='',color='',fontname='Helvetica'):
        '''
        -- 向画布添加文本
        self.doc 文档画布
        fontsize 字体大小
        x y 文本位置
        text 文本内容
        color 文本颜色
        '''
        if color:
            self.doc.setFillColor(color) #choose your font colour
        else:
            # print(text)
            self.doc.setFillColorRGB(0,0,0) #choose your font colour

        self.doc.setFont(fontname, fontsize) #choose your font type and font size
        self.doc.drawString(x,y,text)

    def drawUserInfoTable(self,data, x, y):
        """绘制表格"""
        t = Table(data, style={
        ("FONT", (0, 0), (-1, -1), 'arial', 26),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ('ALIGN', (1, 0), (1, -1), 'CENTER')
        })
        t._argW[1] = 20
        t._argW[2] = 200
        t.wrapOn(self.doc, 0, 0)
        t.drawOn(self.doc, x, y)

    def make_drawing(self,drawdata,make_drawing_color=HexColor('#e57200')):
        # 横向柱状图 
        datas = [] # 数据初始集
        data =[(),()]
        sold = []
        available = []
        names = []
        for keys in drawdata:
            ...
            data[1] += (keys['available'],)
            data[0] += (keys['sold'],)
            names.append(keys['projectName'].upper())
        # self.addBagecolor(436,100,self.pagesize[0]-436,700,color="0xFFFFFF")
        drawing = Drawing(self.pagesize[0]-600, 400)
        # for keys,i in enumerate(datas):
        #     data[1][i] = keys['可售']
        #     data[0][i] = keys['已售']
        #     names[i] = keys['名称']
        # ------- 测试数据
        # data = [
        #     (37, 86, 23, 114, 192, 165, 1, 87,3,93),
        #     (44, 96, 119, 154, 378, 638, 14, 340,60,376),
        #     ]
        # names = ["Cat %s" % i for i in range(1, len(data[0])+1)]

        maxAvailable = max(data[1])
        maxsold = max(data[0])
        bc = HorizontalBarChart()
        bc.x = 200
        bc.y = 30
        bc.height = 600
        bc.width = self.pagesize[0]-900
        bc.data = data
        bc.strokeColor = colors.white

        # 数据指标列
        bc.valueAxis.valueMin = 0
        if maxAvailable >maxsold:
            bc.valueAxis.valueMax = maxAvailable + 100
        else:
            bc.valueAxis.valueMax = maxsold + 100
        if maxAvailable > 1000 or maxsold > 1000:
            if maxsold > maxAvailable :
                bc.valueAxis.valueStep = maxsold/10
            else:
                bc.valueAxis.valueStep = maxAvailable/10
        else:
            bc.valueAxis.valueStep = 50
        bc.valueAxis.gridStrokeColor    = colors.whitesmoke
        # bc.valueAxis.gridStrokeWidth    = 0.25
        bc.valueAxis.visibleGrid        = 1

        # 数据 数量展示
        bc.barLabels.angle         = 0
        bc.barLabelFormat          = DecimalFormatter(0)
        bc.barLabels.boxAnchor     ='w'
        bc.barLabels.boxFillColor  = None
        bc.barLabels.boxStrokeColor= None
        bc.barLabels.dx            = 5
        bc.barLabels.dy            = 0
        bc.barLabels.boxTarget     = 'hi'

        # chart bars 数据颜色、展示内容等 #041e42 #e57200
        bc.bars[1].fillColor = 	HexColor('0x041e42')
        bc.bars[0].fillColor = make_drawing_color
        bc.bars.strokeColor = None

        # 数据名称
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.dx = -10
        bc.categoryAxis.labels.fontName = 'msyh'
        bc.categoryAxis.categoryNames = names

        drawing.add(bc)
        return drawing
    def MakePie_PND(self,dataold,w=350,h=350):
        """ 饼图"""
        # print(datas)
        datas = []
        for item in dataold:
            if item['bedrooms'] == None or item['bedrooms'] <1 or item['bedrooms'] > 5:
                continue
            else:
                datas.append(item)
        my_colors = [
            HexColor(0xe3c84c),
            HexColor(0xd87e33),
            HexColor(0x3075c7),
            HexColor(0x58a045),
            HexColor(0x7751a1)
            ]
        pie_data = []
        pie_label = []
        # sizedata = [0.6,0.6,0.6,0.6,0.6]
        for item in datas:
            pie_data.append(item['number'])
            pie_label.append(str(item['bedrooms'])+' Bedroom (' +str(item['number'])+')')

        d = Drawing(0,0)
        pc = Pie()
        pc.x = 0
        pc.y = 0
        pc.width = w 
        pc.height = h
        pc.data = pie_data
        pc.labels = pie_label

        pc.slices.strokeWidth=0.5
        pc.slices.fontSize = 16


        for i,keys in enumerate(datas):
            pc.slices[i].fillColor = my_colors[i]
            pc.slices[i].strokeColor = my_colors[i]
            # pc.slices[i].labelRadius =sizedata[i]

        d.add(pc)
        return d
    def MakePie(self,dataold,w=350,h=350):

        """ 饼图"""
        # print(datas)
        datas = []
        for item in dataold:
            if item['type'] == None or item['type'] <1 or item['type'] > 5:
                continue
            else:
                datas.append(item)
        my_colors = [
            HexColor(0xe3c84c),
            HexColor(0xd87e33),
            HexColor(0x3075c7),
            HexColor(0x58a045),
            HexColor(0x7751a1)
            ]
        pie_data = []
        pie_label = []
        # sizedata = [0.6,0.6,0.6,0.6,0.6]
        for item in datas:
            pie_data.append(item['number'])
            pie_label.append(str(item['type'])+' Bedroom (' +str(item['number'])+')')

        d = Drawing(0,0)
        pc = Pie()
        pc.x = 0
        pc.y = 0
        pc.width = w 
        pc.height = h
        pc.data = pie_data
        pc.labels = pie_label

        pc.slices.strokeWidth=0.5
        pc.slices.fontSize = 16


        for i,keys in enumerate(datas):
            pc.slices[i].fillColor = my_colors[i]
            pc.slices[i].strokeColor = my_colors[i]
            # pc.slices[i].labelRadius =sizedata[i]

        d.add(pc)
        return d
    def TableImageAdaptive(self,imgName,x=0,y=0,w=None,h=None):
        """
        表格图片自适应不拉伸
        w,h 最大宽高
        """
        img = Image.open(self.requsetImg(imgName))
        imgs = self.requsetImg(imgName)
        imgw,imgh = img.size
        if w < imgw :
            new = imgw - w
            sizes = imgw/new
            imgw = imgw-(imgw/sizes)
            imgh = imgh-(imgh/sizes)
        if h < imgh:
            new = imgh - h
            sizes = imgh/new
            imgw = imgw-(imgw/sizes)
            imgh = imgh-(imgh/sizes)
        imgs = im(imgs,imgw,imgh)
        return imgs

    def create_body_text(self,text, font_name="msyh", font_size=16, color=HexColor("0x335C72"),leading = 18):
        # 表格文本自动换行效果
        style = getSampleStyleSheet()['BodyText']
        style.fontSize = font_size
        style.fontName = font_name
        style.textColor = color
        style.leading = leading
        return Paragraph(text, style=style)

    def counts(self,S,price,scale,scaletwo=0):
        if price == 0:
            return '-'
        if scaletwo:
            return S+format(round((price*scale)*scaletwo), ',')
        else:
            return S+format(round(price*scale),',')


    def stages(self,LoanAmount,Interest_nb=3.5):
        if LoanAmount == None or LoanAmount == 0 :
            return '-'
        Loan = 0.75
        LoanAmount = LoanAmount * Loan
        LoanTenure = 30 * 12
        InterestRate = Interest_nb / 100
        data = round((
          (LoanAmount *
            (InterestRate / 12) *
            math.pow(1 + InterestRate / 12, LoanTenure)) /
          (math.pow(1 + InterestRate / 12, LoanTenure) - 1)
        ))
        return self.S+format(data, ',')

    def stages_numb(self,LoanAmount,Interest_nb=3.5):
        # 计算 每月还款金额 不做格式化
        if LoanAmount == None or LoanAmount == 0 :
            return '-'
        Loan = 0.75
        LoanAmount = LoanAmount * Loan
        LoanTenure = 30 * 12
        InterestRate = Interest_nb / 100
        data = round((
          (LoanAmount *
            (InterestRate / 12) *
            math.pow(1 + InterestRate / 12, LoanTenure)) /
          (math.pow(1 + InterestRate / 12, LoanTenure) - 1)
        ))
        return data

    def priceset(self,price):
        if price !=0 and price != None:
            price1 = format(round(price), ',')
            return str(self.S+price1)
        else:
            return str('-')
    def isVaildDate(self, date):
        # 
            try:
                if ":" in date:
                    time.strptime(date, "%Y-%m-%d %H:%M:%S")
                else:
                    time.strptime(date, "%Y-%m-%d")
                return True
            except:
                return False