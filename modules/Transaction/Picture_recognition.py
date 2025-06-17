import cv2,hashlib
import numpy as np
import re,copy,requests,json,os,configparser,time
from comm.logger import logger
from urllib.parse import urlparse




def FileDown(url,filepath=os.getcwd()):
    # 网络文件保存

    # logger.info('网络文件保存到本地=====>{}'.format(url))
    r = requests.get(url,verify=False)
    if r.status_code == 200:
        parsed_url = urlparse(url)
        file_path = parsed_url.path
        downFlie = os.path.join(filepath,'down',os.path.split(file_path)[-1])
        # print(downFlie)
        if not os.path.exists(os.path.join(filepath,'down')):
            os.makedirs(os.path.join(filepath,'down'))
        with open(downFlie, 'ab') as f:
            f.write(r.content)
            f.close()
        logger.info("文件保存到本地=====>URL:{0},Path:{1}".format(url,downFlie))
        return downFlie
    else:
      logger.info("网络图片不存在:{}".format(url))
      raise Exception("网络图片不存在")


def set_signature(data):
    # Ecoprop API 加密方法
    logger.info('signature start=======>{}'.format(data))
    md5data = data.copy()
    # md5data['token'] =''
    a = list(md5data.items()) # 转列表
    a.sort(key=lambda x:x[0],reverse=False) # 排序
    keys = ''
    for item in a:
        if item[1] :
            keys+= item[1]
        else:
            keys+= ''
    keys = keys+'c1d65f3667324592a071ebec5038f38c'
    signature = hashlib.md5(keys.encode(encoding='UTF-8')).hexdigest() #加密
    logger.info('signature end=======>{}'.format(signature))
    md5data['signature'] = signature #请求参数追加签名
    return md5data


def Picture_table_recognition(Img_path):
        """
        图片识别
        """
        filepath = FileDown(Img_path)

        image=cv2.imdecode(np.fromfile(filepath,dtype=np.uint8),-1) # 中文路径问题解决
        # y1, x1 = image.shape[0:2]
        # 二值化
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(~gray, 250,
                                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 7, -1)
        rows, cols = binary.shape
        scale = 150
                
        # 膨胀腐化
        kernel = np.ones((2, 2), np.uint8)
        binary = cv2.dilate(binary, kernel) 
        # binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel) 

        # 识别横线
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (cols // scale, 1))
        eroded = cv2.erode(binary, kernel, iterations=1)
        dilatedcol = cv2.dilate(eroded, kernel, iterations=1)
        # contours, hierarchy = cv2.findContours(
        #     dilatedcol, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # cv2.drawContours(image,contours,-1,(0,0,255),2)

        # 识别竖线
        scale = 250
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, rows // scale))
        eroded1 = cv2.erode(binary, kernel, iterations=1)
        dilatedrow = cv2.dilate(eroded1, kernel, iterations=1)

        # 标识表格
        merge = cv2.add(dilatedcol, dilatedrow)

        # #获取交点
        bitwiseAnd = cv2.bitwise_and(dilatedcol, dilatedrow)

        ys, xs = np.where(bitwiseAnd > 0)
        ll = [ (xs[i],ys[i]) for i in range(len(ys))] #获取交点

        #  findContours 获取轮廓
        contours, hierarchy = cv2.findContours(merge, cv2.RETR_LIST,
                                            cv2.CHAIN_APPROX_SIMPLE)
        # cv2.drawContours(image,contours,-1,(0,0,255),2)


        cv2.waitKey(0)
        content = []
        name = 0
        mean_size = np.mean([cv2.contourArea(i) for i in contours])  #获取平均面积
        for i, contour in enumerate(contours):
            f = 0
            x, y, w, h = cv2.boundingRect(contour)
            size = cv2.contourArea(contour)  #获取面积
            # 这个代码是干嘛的？
            # for i in ll:
            #     if 0 <= int(x-i[0])<= 10 and 0 <= int(y-i[1])<= 10 :
            #         f = 1
            #         break

            if f != 0 and  600 < size < mean_size*100: 
                # 需要调整平均面积计算方式， 当前此方法不能满足全部情况。
                # print("平均面积：",mean_size,size)
                mb = {
                    "width": "%s" % (w -1),
                    "height": "%s" % (h -1),
                    "left": "%s" % (x ),
                    "top": "%s" % (y ),
                    "name": "Rect%s" % name,
                    "fill": "rgba(220,20,60,0.4)",
                    "type": "rect"
                }
                content.append(mb)
                name += 1
        logger.info('完成识别=======>')
        os.remove(filepath)




        return content
