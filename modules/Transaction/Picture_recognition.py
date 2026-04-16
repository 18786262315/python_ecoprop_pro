import cv2, hashlib
import numpy as np
import re, copy, requests, json, os, configparser, time, base64
from comm.logger import logger
from urllib.parse import urlparse


def FileDown(url, filepath=os.getcwd()):
    """网络文件保存到本地"""
    r = requests.get(url, verify=False)
    if r.status_code == 200:
        parsed_url = urlparse(url)
        file_path = parsed_url.path
        downFlie = os.path.join(filepath, 'down', os.path.split(file_path)[-1])
        if not os.path.exists(os.path.join(filepath, 'down')):
            os.makedirs(os.path.join(filepath, 'down'))
        with open(downFlie, 'ab') as f:
            f.write(r.content)
        logger.info("文件保存到本地=====>URL:{0},Path:{1}".format(url, downFlie))
        return downFlie
    else:
        logger.info("网络图片不存在:{}".format(url))
        raise Exception("网络图片不存在")


def set_signature(data):
    """Ecoprop API 加密方法"""
    logger.info('signature start=======>{}'.format(data))
    md5data = data.copy()
    a = list(md5data.items())
    a.sort(key=lambda x: x[0], reverse=False)
    keys = ''
    for item in a:
        if item[1]:
            keys += item[1]
        else:
            keys += ''
    keys = keys + 'c1d65f3667324592a071ebec5038f38c'
    signature = hashlib.md5(keys.encode(encoding='UTF-8')).hexdigest()
    logger.info('signature end=======>{}'.format(signature))
    md5data['signature'] = signature
    return md5data


# ==================== 在线表格识别 ====================

class OnlineTableRecognizer:
    """
    在线表格识别器，调用在线API识别图片中的表格框线坐标。
    支持百度OCR表格识别API，也可扩展其他平台。
    """

    def __init__(self, api_key=None, secret_key=None, api_url=None):
        """
        初始化在线识别器
        Args:
            api_key: API Key (百度OCR)
            secret_key: Secret Key (百度OCR)
            api_url: 自定义API地址（如果使用自建服务）
        """
        self.api_key = api_key or os.environ.get('TABLE_OCR_API_KEY', '')
        self.secret_key = secret_key or os.environ.get('TABLE_OCR_SECRET_KEY', '')
        self.api_url = api_url or os.environ.get('TABLE_OCR_API_URL', '')
        self._access_token = None

    def _get_access_token(self):
        """获取百度OCR access_token"""
        if self._access_token:
            return self._access_token
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        try:
            resp = requests.post(url, params=params, timeout=10)
            result = resp.json()
            self._access_token = result.get("access_token")
            if not self._access_token:
                logger.error("获取access_token失败: {}".format(result))
                raise Exception("获取access_token失败")
            return self._access_token
        except Exception as e:
            logger.error("获取access_token异常: {}".format(e))
            raise

    def _image_to_base64(self, image_path):
        """将图片文件转为base64编码"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def recognize_table(self, image_path):
        """
        在线识别表格，返回表格单元格的框线坐标列表。
        
        Args:
            image_path: 本地图片路径
            
        Returns:
            list: 单元格坐标列表，每个元素为 dict:
                {
                    "width": str, "height": str,
                    "left": str, "top": str,
                    "name": str, "fill": str, "type": str,
                    "row": int, "col": int,  # 行列索引（如API返回）
                    "text": str              # 单元格文本（如API返回）
                }
        """
        if self.api_url:
            return self._recognize_custom_api(image_path)
        else:
            return self._recognize_baidu(image_path)

    def _recognize_baidu(self, image_path):
        """
        调用百度OCR表格识别API
        接口: https://aip.baidubce.com/rest/2.0/ocr/v1/table
        返回每个单元格的坐标和文本
        """
        access_token = self._get_access_token()
        url = "https://aip.baidubce.com/rest/2.0/ocr/v1/table"
        params = {"access_token": access_token}
        img_base64 = self._image_to_base64(image_path)
        payload = {"image": img_base64}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            resp = requests.post(url, params=params, data=payload, headers=headers, timeout=30)
            result = resp.json()
            logger.info("百度表格识别返回: tables_result count={}".format(
                len(result.get("tables_result", []))
            ))
            return self._parse_baidu_result(result)
        except Exception as e:
            logger.error("百度表格识别异常: {}".format(e))
            raise

    def _parse_baidu_result(self, result):
        """
        解析百度OCR表格识别结果，提取每个单元格的框线坐标。
        百度返回格式:
        {
            "tables_result": [{
                "body": [{
                    "cell_location": [
                        {"x": x1, "y": y1}, {"x": x2, "y": y2},
                        {"x": x3, "y": y3}, {"x": x4, "y": y4}
                    ],
                    "row_start": 0, "row_end": 0,
                    "col_start": 0, "col_end": 0,
                    "words": "文本内容"
                }, ...]
            }]
        }
        """
        content = []
        idx = 0
        tables = result.get("tables_result", [])
        for table in tables:
            body = table.get("body", [])
            for cell in body:
                cell_loc = cell.get("cell_location", [])
                if len(cell_loc) < 4:
                    continue
                # 取四个顶点的外接矩形
                xs = [p["x"] for p in cell_loc]
                ys = [p["y"] for p in cell_loc]
                x_min, x_max = min(xs), max(xs)
                y_min, y_max = min(ys), max(ys)
                w = x_max - x_min
                h = y_max - y_min
                if w <= 0 or h <= 0:
                    continue
                mb = {
                    "width": str(w),
                    "height": str(h),
                    "left": str(x_min),
                    "top": str(y_min),
                    "name": "Rect%s" % idx,
                    "fill": "rgba(220,20,60,0.4)",
                    "type": "rect",
                    "row": cell.get("row_start", 0),
                    "col": cell.get("col_start", 0),
                    "text": cell.get("words", "")
                }
                content.append(mb)
                idx += 1
        logger.info("百度表格识别解析完成, 共{}个单元格".format(len(content)))
        return content

    def _recognize_custom_api(self, image_path):
        """
        调用自定义在线表格识别API。
        
        要求API返回格式:
        {
            "code": 0,
            "data": {
                "tables": [{
                    "cells": [{
                        "x": int, "y": int, "w": int, "h": int,
                        "row": int, "col": int,
                        "text": str
                    }, ...]
                }]
            }
        }
        """
        img_base64 = self._image_to_base64(image_path)
        payload = {"image": img_base64}
        headers = {"Content-Type": "application/json"}

        try:
            resp = requests.post(
                self.api_url, json=payload, headers=headers, timeout=30
            )
            result = resp.json()
            logger.info("自定义API表格识别返回: {}".format(result.get("code")))
            return self._parse_custom_result(result)
        except Exception as e:
            logger.error("自定义API表格识别异常: {}".format(e))
            raise

    def _parse_custom_result(self, result):
        """解析自定义API返回结果"""
        content = []
        idx = 0
        tables = result.get("data", {}).get("tables", [])
        for table in tables:
            cells = table.get("cells", [])
            for cell in cells:
                x = cell.get("x", 0)
                y = cell.get("y", 0)
                w = cell.get("w", 0)
                h = cell.get("h", 0)
                if w <= 0 or h <= 0:
                    continue
                mb = {
                    "width": str(w),
                    "height": str(h),
                    "left": str(x),
                    "top": str(y),
                    "name": "Rect%s" % idx,
                    "fill": "rgba(220,20,60,0.4)",
                    "type": "rect",
                    "row": cell.get("row", 0),
                    "col": cell.get("col", 0),
                    "text": cell.get("text", "")
                }
                content.append(mb)
                idx += 1
        logger.info("自定义API解析完成, 共{}个单元格".format(len(content)))
        return content


# ==================== 本地表格识别（保留作为降级方案） ====================

class LocalTableRecognizer:
    """
    本地OpenCV表格识别器（从 run_tk.py ImageProcessor 优化而来）。
    当在线API不可用时作为降级方案。
    """

    @staticmethod
    def detect_tables(image_path, remove_headers=True, min_area_threshold=300, max_area_ratio=0.3):
        """
        本地识别图像中的表格并返回矩形坐标
        """
        try:
            image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), -1)
            if image is None:
                raise ValueError("无法读取图像文件")

            img_h, img_w = image.shape[0:2]
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            binary = cv2.adaptiveThreshold(
                ~gray, 250, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 7, -1
            )
            rows, cols = binary.shape

            # 膨胀
            kernel = np.ones((2, 2), np.uint8)
            binary = cv2.dilate(binary, kernel)

            # 识别横线
            h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (cols // 150, 1))
            eroded_h = cv2.erode(binary, h_kernel, iterations=1)
            dilated_h = cv2.dilate(eroded_h, h_kernel, iterations=1)

            # 识别竖线
            v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, rows // 250))
            eroded_v = cv2.erode(binary, v_kernel, iterations=1)
            dilated_v = cv2.dilate(eroded_v, v_kernel, iterations=1)

            # 合并横竖线
            merge = cv2.add(dilated_h, dilated_v)

            # 获取交点
            bitwise_and = cv2.bitwise_and(dilated_h, dilated_v)
            ys, xs = np.where(bitwise_and > 0)
            intersections = [(xs[i], ys[i]) for i in range(len(ys))]

            # 获取轮廓
            all_contours = cv2.findContours(merge, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]

            # 面积过滤
            min_area = min_area_threshold
            max_area = (img_h * img_w) * max_area_ratio

            filtered_contours = []
            contour_areas = []
            for contour in all_contours:
                area = cv2.contourArea(contour)
                if min_area <= area <= max_area:
                    filtered_contours.append(contour)
                    contour_areas.append(area)

            if not contour_areas:
                logger.warning("本地识别: 未找到有效轮廓")
                return []

            # IQR 四分位数过滤
            contour_areas_sorted = sorted(contour_areas)
            count = len(contour_areas_sorted)
            q1 = contour_areas_sorted[count // 4]
            q3 = contour_areas_sorted[3 * count // 4]
            iqr = q3 - q1

            lower_bound = max(q1 - 1.5 * iqr, min_area)
            upper_bound = min(q3 + 1.5 * iqr, max_area)

            if iqr < 1000:
                mean_area = np.mean(contour_areas)
                std_area = np.std(contour_areas)
                lower_bound = max(lower_bound, mean_area - 2 * std_area)
                upper_bound = min(upper_bound, mean_area + 2 * std_area)

            # 收集矩形
            raw_rectangles = []
            for contour in filtered_contours:
                area = cv2.contourArea(contour)
                if not (lower_bound <= area <= upper_bound):
                    continue
                x, y, w, h = cv2.boundingRect(contour)

                matched = not remove_headers
                if remove_headers:
                    for pt in intersections:
                        if 0 <= int(x - pt[0]) <= 10 and 0 <= int(y - pt[1]) <= 10:
                            matched = True
                            break

                if matched:
                    raw_rectangles.append({"x": x, "y": y, "w": w, "h": h, "size": area})

            # 过滤重叠矩形
            filtered = LocalTableRecognizer._filter_overlapping(raw_rectangles)

            content = []
            for idx, rect in enumerate(filtered):
                mb = {
                    "width": str(rect["w"] - 1),
                    "height": str(rect["h"] - 1),
                    "left": str(rect["x"]),
                    "top": str(rect["y"]),
                    "name": "Rect%s" % idx,
                    "fill": "rgba(220,20,60,0.4)",
                    "type": "rect"
                }
                content.append(mb)

            logger.info("本地识别完成, 共{}个矩形".format(len(content)))
            return content

        except Exception as e:
            logger.error("本地表格识别异常: {}".format(e))
            return []

    @staticmethod
    def _filter_overlapping(rectangles, overlap_threshold=0.5):
        """过滤重叠矩形，保留较大的"""
        if not rectangles:
            return []
        sorted_rects = sorted(rectangles, key=lambda r: r["size"], reverse=True)
        kept = []
        for cur in sorted_rects:
            overlapping = False
            for k in kept:
                x1 = max(cur["x"], k["x"])
                y1 = max(cur["y"], k["y"])
                x2 = min(cur["x"] + cur["w"], k["x"] + k["w"])
                y2 = min(cur["y"] + cur["h"], k["y"] + k["h"])
                if x1 < x2 and y1 < y2:
                    overlap_area = (x2 - x1) * (y2 - y1)
                    smaller = min(cur["w"] * cur["h"], k["w"] * k["h"])
                    if smaller > 0 and overlap_area / smaller > overlap_threshold:
                        overlapping = True
                        break
            if not overlapping:
                kept.append(cur)
        return kept


# ==================== 统一入口函数 ====================

def Picture_table_recognition(Img_path, use_online=True, api_key=None, secret_key=None, api_url=None):
    """
    图片表格识别统一入口。
    
    Args:
        Img_path: 图片URL地址
        use_online: 是否使用在线识别（默认True）
        api_key: 在线API Key
        secret_key: 在线API Secret Key
        api_url: 自定义API地址（优先级高于百度OCR）
        
    Returns:
        list: 表格单元格坐标列表
    """
    filepath = FileDown(Img_path)

    try:
        if use_online:
            logger.info("使用在线表格识别: {}".format(Img_path))
            recognizer = OnlineTableRecognizer(
                api_key=api_key, secret_key=secret_key, api_url=api_url
            )
            try:
                content = recognizer.recognize_table(filepath)
                if content:
                    logger.info("在线识别完成, 共{}个单元格".format(len(content)))
                    return content
                else:
                    logger.warning("在线识别未返回结果，降级到本地识别")
            except Exception as e:
                logger.warning("在线识别失败({}), 降级到本地识别".format(e))

        # 本地识别（降级方案）
        logger.info("使用本地表格识别: {}".format(Img_path))
        content = LocalTableRecognizer.detect_tables(filepath)
        logger.info("识别完成, 共{}个矩形".format(len(content)))
        return content

    finally:
        # 清理下载的临时文件
        if os.path.exists(filepath):
            os.remove(filepath)
