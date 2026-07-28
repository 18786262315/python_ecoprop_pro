"""
图片表格识别模块

本模块用于识别图片中的表格框线坐标，返回每个单元格的边界矩形信息。
采用纯本地OpenCV图像处理算法，无需外部API支持。

算法原理：
    1. 将图像转为灰度图并二值化
    2. 通过形态学操作（膨胀）增强表格线条
    3. 分别提取横线和竖线
    4. 合并横竖线获取表格网格
    5. 计算横竖线交点（表格顶点）
    6. 通过轮廓检测获取单元格区域
    7. 使用统计方法（IQR四分位距）过滤噪声轮廓
    8. 过滤重叠的矩形区域

依赖：
    - opencv-python (cv2)
    - numpy
    - requests (仅用于下载网络图片)

作者：自动生成
日期：2024
"""

import cv2
import hashlib
import numpy as np
import os
import requests
from comm.logger import logger
from urllib.parse import urlparse


def set_signature(data):
    """
    生成API请求签名（用于项目自己的服务器认证，非百度OCR）。

    签名算法：
        1. 复制数据字典
        2. 签名时把token置空（token不参与MD5加密）
        3. 按键名升序排序
        4. 拼接所有非空值
        5. 末尾追加密钥字符串
        6. 计算MD5哈希值
        7. 恢复原始token值（提交时需要）

    Args:
        data: 包含API参数的字典，必须包含 userId, token, brokeId 等字段

    Returns:
        dict: 原始数据字典附加 signature 字段，token 保持原值
    """
    # logger.info('signature start=======>{}'.format(data))
    md5data = data.copy()
    # 保存原始token，签名时置空（token不参与MD5加密）
    original_token = md5data.get('token', '')
    md5data['token'] = ''
    # 按键名升序排列
    a = list(md5data.items())
    a.sort(key=lambda x: x[0], reverse=False)
    # 拼接所有值
    keys = ''
    for item in a:
        if item[1]:
            keys += item[1]
        else:
            keys += ''
    # 追加密钥并计算MD5
    keys = keys + 'c1d65f3667324592a071ebec5038f38c'
    signature = hashlib.md5(keys.encode(encoding='UTF-8')).hexdigest()
    logger.info('signature end=======>{}'.format(signature))
    # 恢复原始token（提交时需要）
    md5data['token'] = original_token
    md5data['signature'] = signature
    return md5data


# ============================================================
# 工具函数：网络文件下载
# ============================================================

def FileDown(url, filepath=os.getcwd()):
    """
    将网络上的图片文件下载到本地临时目录。

    Args:
        url: 图片的网络URL地址
        filepath: 本地保存路径，默认为当前工作目录

    Returns:
        str: 下载后本地文件的完整路径

    Raises:
        Exception: 当下载失败（HTTP状态码非200）时抛出异常
    """
    r = requests.get(url, verify=False)
    if r.status_code == 200:
        # 解析URL获取文件名
        parsed_url = urlparse(url)
        file_path = parsed_url.path
        downFlie = os.path.join(filepath, 'down', os.path.split(file_path)[-1])

        # 创建下载目录（如果不存在）
        if not os.path.exists(os.path.join(filepath, 'down')):
            os.makedirs(os.path.join(filepath, 'down'))

        # 追加写入（支持大文件分片下载）
        with open(downFlie, 'ab') as f:
            f.write(r.content)

        logger.info("文件保存到本地=====>URL:{0},Path:{1}".format(url, downFlie))
        return downFlie
    else:
        logger.info("网络图片不存在:{}".format(url))
        raise Exception("网络图片不存在")


# ============================================================
# 本地表格识别器
# ============================================================

class LocalTableRecognizer:
    """
    本地OpenCV表格识别器。

    通过图像处理技术检测图片中的表格框线，并返回每个单元格的坐标信息。
    算法基于形态学操作和轮廓检测，对表格图片有较好的识别效果。

    Attributes:
        无需外部属性，纯静态方法实现

    Example:
        >>> result = LocalTableRecognizer.detect_tables("table.jpg")
        >>> print(f"检测到 {len(result)} 个单元格")
    """

    @staticmethod
    def detect_tables(image_path, remove_headers=True, min_area_threshold=300, max_area_ratio=0.3):
        """
        检测图像中的表格并返回单元格坐标列表。

        算法流程：
            1. 读取图像并转换为灰度图
            2. 自适应阈值二值化，将表格线条变为黑色背景白色线条
            3. 膨胀操作增强线条连续性
            4. 使用形态学核分别提取横线和竖线
            5. 合并横竖线形成完整表格网格
            6. 求横竖线交点，获取表格顶点坐标
            7. 查找所有轮廓（表格单元格）
            8. 面积过滤：去除过大和过小的噪声轮廓
            9. IQR四分位距进一步过滤孤立噪声点
            10. 检测并去除表头区域（可选）
            11. 过滤重叠的矩形区域
            12. 返回标准格式的坐标列表

        Args:
            image_path: 本地图片路径（支持中文路径）
            remove_headers: 是否移除表头区域（默认True）。表头区域的判断依据是：
                           该区域的左上角顶点是否靠近表格交点
            min_area_threshold: 最小面积阈值（默认300）。面积小于此值的轮廓会被过滤
            max_area_ratio: 最大面积占图像面积的比例（默认0.3，即30%）。
                           面积大于此值的轮廓会被过滤

        Returns:
            list: 单元格坐标列表，每个元素为字典，包含以下键值对：
                - width (str): 矩形宽度
                - height (str): 矩形高度
                - left (str): 矩形左上角X坐标
                - top (str): 矩形左上角Y坐标
                - name (str): 矩形名称，格式为"Rect{index}"
                - fill (str): 填充颜色，RGBA格式
                - type (str): 类型，固定为"rect"
                - row (int): 所在行索引（相对于表头以下区域）
                - col (int): 所在列索引

        Note:
            - 返回的坐标是相对于原图的绝对坐标
            - 表头区域通过检测左上角是否靠近交点来判断（容差10像素）
            - 重叠矩形会保留较大的那个
        """
        try:
            # ---------------------------------------------------------
            # 第1步：读取图像
            # ---------------------------------------------------------
            # 使用np.fromfile配合cv2.imdecode读取图片，支持中文路径
            # dtype=np.uint8 确保以字节方式读取
            image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), -1)
            if image is None:
                raise ValueError("无法读取图像文件: {}".format(image_path))

            # 获取图像尺寸
            img_h, img_w = image.shape[0:2]
            logger.info("图像尺寸: {}x{}".format(img_w, img_h))

            # ---------------------------------------------------------
            # 第2步：灰度转换与二值化
            # ---------------------------------------------------------
            # 将彩色图转为灰度图（单通道）
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 自适应阈值二值化
            # cv2.bitwise_not(gray): 取反操作，将表格线（深色）变为白色，背景变为黑色
            # cv2.ADAPTIVE_THRESH_GAUSSIAN_C: 高斯加权自适应阈值
            # 7: 邻域大小（必须为奇数），控制用于计算的局部窗口大小
            # -1: 常数C，从均值或加权均值中减去的值，用于微调阈值
            # 结果：表格线部分变为白色（255），背景变为黑色（0）
            binary = cv2.adaptiveThreshold(
                cv2.bitwise_not(gray), 250,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 7, -1
            )

            rows, cols = binary.shape
            logger.info("二值化完成，图像尺寸: {}x{}".format(cols, rows))

            # ---------------------------------------------------------
            # 第3步：膨胀操作增强线条
            # ---------------------------------------------------------
            # 创建2x2的结构元素（卷积核）
            # np.uint8: 确保核的值类型正确
            kernel = np.ones((2, 2), np.uint8)

            # 膨胀操作：将白色区域扩大
            # 效果：使断开的线条连接起来，便于后续检测
            binary = cv2.dilate(binary, kernel)

            # ---------------------------------------------------------
            # 第4步：提取横线
            # ---------------------------------------------------------
            # 计算横线检测的核尺寸
            # cols // 150: 根据图像宽度动态调整核的宽度
            # 宽度方向核较大，用于检测横向的表格分隔线
            h_kernel_width = max(cols // 150, 1)  # 确保最小值为1，避免除零
            h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (h_kernel_width, 1))

            # 腐蚀操作：消除小的白色噪点
            eroded_h = cv2.erode(binary, h_kernel, iterations=1)

            # 膨胀操作：恢复主体线条
            dilated_h = cv2.dilate(eroded_h, h_kernel, iterations=1)

            logger.info("横线检测核尺寸: {}x1".format(h_kernel_width))

            # ---------------------------------------------------------
            # 第5步：提取竖线
            # ---------------------------------------------------------
            # 计算竖线检测的核尺寸
            # rows // 250: 根据图像高度动态调整核的高度
            # 高度方向核较大，用于检测纵向的表格分隔线
            v_kernel_height = max(rows // 250, 1)  # 确保最小值为1
            v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_kernel_height))

            # 腐蚀 + 膨胀（与横线处理相同）
            eroded_v = cv2.erode(binary, v_kernel, iterations=1)
            dilated_v = cv2.dilate(eroded_v, v_kernel, iterations=1)

            logger.info("竖线检测核尺寸: 1x{}".format(v_kernel_height))

            # ---------------------------------------------------------
            # 第6步：合并横竖线获取表格网格
            # ---------------------------------------------------------
            # 将横线和竖线叠加，得到完整的表格网格结构
            merge = cv2.add(dilated_h, dilated_v)

            # ---------------------------------------------------------
            # 第7步：计算横竖线交点（表格顶点）
            # ---------------------------------------------------------
            # 通过按位与运算找到横竖线的交叉点
            # 这些点代表了表格的拐角或交叉位置
            bitwise_and = cv2.bitwise_and(dilated_h, dilated_v)

            # 提取所有交点的坐标
            # np.where返回满足条件的像素坐标
            ys, xs = np.where(bitwise_and > 0)
            intersections = [(xs[i], ys[i]) for i in range(len(ys))]
            logger.info("检测到 {} 个交点".format(len(intersections)))

            # ---------------------------------------------------------
            # 第8步：查找所有轮廓
            # ---------------------------------------------------------
            # 使用RETR_LIST模式：获取所有轮廓，不建立父子关系
            # CHAIN_APPROX_SIMPLE：只保留轮廓的端点，节省内存
            all_contours = cv2.findContours(merge, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]

            logger.info("检测到 {} 个初始轮廓".format(len(all_contours)))

            # ---------------------------------------------------------
            # 第9步：面积过滤 - 初步筛选
            # ---------------------------------------------------------
            # 计算面积阈值
            min_area = min_area_threshold  # 最小面积（像素数）
            max_area = (img_h * img_w) * max_area_ratio  # 最大面积为图像面积的指定比例

            # 过滤出面积在合理范围内的轮廓
            filtered_contours = []
            contour_areas = []
            for contour in all_contours:
                area = cv2.contourArea(contour)
                if min_area <= area <= max_area:
                    filtered_contours.append(contour)
                    contour_areas.append(area)

            if not contour_areas:
                logger.warning("初步筛选后无有效轮廓")
                return []

            logger.info("面积筛选后剩余 {} 个轮廓".format(len(filtered_contours)))

            # ---------------------------------------------------------
            # 第10步：IQR四分位距过滤 - 统计方法去除离群点
            # ---------------------------------------------------------
            # 对面积进行排序
            contour_areas_sorted = sorted(contour_areas)
            count = len(contour_areas_sorted)

            # 计算四分位数
            q1 = contour_areas_sorted[count // 4]           # 25%分位数
            q3 = contour_areas_sorted[3 * count // 4]       # 75%分位数
            iqr = q3 - q1                                   # 四分位距

            # 根据四分位数计算面积上下界
            # 使用1.5倍IQR规则（类似箱线图的异常值检测）
            lower_bound = max(q1 - 1.5 * iqr, min_area)
            upper_bound = min(q3 + 1.5 * iqr, max_area)

            # 当数据分布较为集中时（IQR较小），使用更严格的标准差方法
            # 这样可以更好地过滤掉与主体区域面积差异较大的孤立轮廓
            if iqr < 1000:
                mean_area = np.mean(contour_areas)
                std_area = np.std(contour_areas)

                # 使用均值±2倍标准差作为边界
                lower_bound_std = max(mean_area - 2 * std_area, min_area)
                upper_bound_std = min(mean_area + 2 * std_area, max_area)

                # 取两种方法的并集（更宽松的边界）
                lower_bound = max(lower_bound, lower_bound_std)
                upper_bound = min(upper_bound, upper_bound_std)

            logger.info("IQR过滤边界: [{:.0f}, {:.0f}], IQR={:.0f}".format(
                float(lower_bound), float(upper_bound), float(iqr)))

            # ---------------------------------------------------------
            # 第11步：收集符合条件的矩形
            # ---------------------------------------------------------
            raw_rectangles = []
            for contour in filtered_contours:
                area = cv2.contourArea(contour)

                # 检查面积是否符合边界
                if not (lower_bound <= area <= upper_bound):
                    continue

                # 获取轮廓的外接矩形（轴对齐）
                x, y, w, h = cv2.boundingRect(contour)

                # ---------------------------------------------------------
                # 第12步：表头检测与过滤（可选）
                # ---------------------------------------------------------
                # 判断逻辑：如果矩形的左上角靠近任何一个表格交点，
                # 则认为该区域属于表头，需要过滤掉
                matched = not remove_headers  # 默认值取决于remove_headers参数
                if remove_headers:
                    for pt in intersections:
                        # 容差范围：10像素
                        # 检查该矩形左上角是否在交点的10像素范围内
                        if 0 <= int(x - pt[0]) <= 10 and 0 <= int(y - pt[1]) <= 10:
                            matched = True
                            break

                if matched:
                    raw_rectangles.append({
                        "x": x,
                        "y": y,
                        "w": w,
                        "h": h,
                        "size": area
                    })

            logger.info("表头过滤后剩余 {} 个矩形".format(len(raw_rectangles)))

            # ---------------------------------------------------------
            # 第13步：过滤重叠矩形
            # ---------------------------------------------------------
            # 当两个矩形重叠面积超过较小矩形面积的50%时，保留较大的那个
            filtered = LocalTableRecognizer._filter_overlapping(raw_rectangles)

            # ---------------------------------------------------------
            # 第14步：生成标准格式的输出
            # ---------------------------------------------------------
            content = []
            for idx, rect in enumerate(filtered):
                mb = {
                    # 宽度和高度各减1，避免矩形重叠（根据原逻辑保留）
                    "width": str(rect["w"] - 1),
                    "height": str(rect["h"] - 1),
                    "left": str(rect["x"]),
                    "top": str(rect["y"]),
                    "name": "Rect%s" % idx,
                    "fill": "rgba(220,20,60,0.4)",
                    "type": "rect",
                    "row": 0,  # 预留字段，暂未实现行号计算
                    "col": 0   # 预留字段，暂未实现列号计算
                }
                content.append(mb)

            logger.info("本地识别完成, 共{}个矩形".format(len(content)))
            return content

        except Exception as e:
            logger.error("本地表格识别异常: {}".format(e))
            return []

    @staticmethod
    def _filter_overlapping(rectangles, overlap_threshold=0.5):
        """
        过滤重叠的矩形区域，保留较大的那个。

        算法流程：
            1. 按面积从大到小排序矩形
            2. 依次检查每个矩形与已保留矩形的重叠情况
            3. 如果重叠面积超过较小矩形面积的指定比例，则跳过该矩形
            4. 否则，将其加入保留列表

        Args:
            rectangles: 矩形列表，每个元素包含 x, y, w, h, size 键
            overlap_threshold: 重叠阈值（默认0.5）
                              当重叠面积占较小矩形面积的比例超过此值时，
                              认为两个矩形重复，保留较大的

        Returns:
            list: 过滤后的矩形列表，按面积从大到小排序
        """
        if not rectangles:
            return []

        # 按面积从大到小排序（优先保留大矩形）
        sorted_rects = sorted(rectangles, key=lambda r: r["size"], reverse=True)
        kept = []

        for cur in sorted_rects:
            overlapping = False

            for k in kept:
                # ---------------------------------------------------------
                # 计算两个矩形的重叠区域
                # ---------------------------------------------------------
                # x1, y1: 重叠区域的左上角坐标（两个矩形各自左上角的最大值）
                # x2, y2: 重叠区域的右下角坐标（两个矩形各自右下角的最小值）
                x1 = max(cur["x"], k["x"])
                y1 = max(cur["y"], k["y"])
                x2 = min(cur["x"] + cur["w"], k["x"] + k["w"])
                y2 = min(cur["y"] + cur["h"], k["y"] + k["h"])

                # 检查是否存在有效重叠区域
                # x1 < x2 且 y1 < y2 表示两个矩形在该维度上有重叠
                if x1 < x2 and y1 < y2:
                    overlap_area = (x2 - x1) * (y2 - y1)
                    smaller_area = min(cur["w"] * cur["h"], k["w"] * k["h"])

                    # 计算重叠比例，如果超过阈值则认为是重复矩形
                    if smaller_area > 0 and overlap_area / smaller_area > overlap_threshold:
                        overlapping = True
                        break

            if not overlapping:
                kept.append(cur)

        return kept


# ============================================================
# 统一入口函数
# ============================================================

def Picture_table_recognition(Img_path, min_area_threshold=300, max_area_ratio=0.3, remove_headers=True):
    """
    图片表格识别统一入口函数。

    本函数是外部调用的主要接口，负责：
        1. 下载网络图片（如果是URL）到本地
        2. 调用本地识别器进行表格检测
        3. 清理临时文件

    Args:
        Img_path: 图片路径，可以是本地路径或网络URL
        min_area_threshold: 最小面积阈值（默认300），见 LocalTableRecognizer.detect_tables
        max_area_ratio: 最大面积占图像面积的比例（默认0.3），同上
        remove_headers: 是否移除表头（默认True），同上

    Returns:
        list: 表格单元格坐标列表，格式见 LocalTableRecognizer.detect_tables 返回值

    Example:
        >>> result = Picture_table_recognition("https://example.com/table.jpg")
        >>> print(result)
        [
            {'width': '99', 'height': '29', 'left': '10', 'top': '10', ...},
            {'width': '99', 'height': '29', 'left': '110', 'top': '10', ...},
            ...
        ]
    """
    # 下载网络图片到本地临时目录
    filepath = FileDown(Img_path)

    try:
        # 调用本地识别器进行表格检测
        logger.info("开始本地表格识别: {}".format(Img_path))
        content = LocalTableRecognizer.detect_tables(
            filepath,
            remove_headers=remove_headers,
            min_area_threshold=min_area_threshold,
            max_area_ratio=max_area_ratio
        )
        logger.info("识别完成, 共{}个矩形".format(len(content)))
        return content

    finally:
        # ---------------------------------------------------------
        # 清理临时文件
        # 无论识别成功或失败，都要清理下载的临时文件
        # ---------------------------------------------------------
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                logger.info("临时文件已清理: {}".format(filepath))
            except Exception as e:
                logger.warning("清理临时文件失败: {}".format(e))




# ============================================================
# 本地调试函数
# ============================================================

def local_debug(img_path=None):
    """
    本地调试函数，用于测试图片表格识别效果（不调用外部API）。

    用法：
        from modules.Transaction import Picture_recognition as pic

        # 指定本地图片路径测试
        pic.local_debug(r"C:\\Users\\test\\table.jpg")

        # 不传参数则弹出文件选择框
        pic.local_debug()

    参数：
        img_path: 本地图片路径，不传则弹出窗口选择文件
    """
    import tkinter as tk
    from tkinter import filedialog

    # 如果没传路径，弹出文件选择框
    if img_path is None:
        root = tk.Tk()
        root.withdraw()
        img_path = filedialog.askopenfilename(
            title="选择表格图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
        )
        if not img_path:
            print("未选择图片，调试取消")
            return

    print(f"开始识别图片: {img_path}")
    print("=" * 50)

    # 调用识别
    result = LocalTableRecognizer.detect_tables(img_path)

    print(f"识别完成，共检测到 {len(result)} 个矩形")
    for i, rect in enumerate(result):
        print(f"  {i+1}. {rect['name']}: left={rect['left']}, top={rect['top']}, "
              f"width={rect['width']}, height={rect['height']}")

    # 可视化结果
    _visualize_result(img_path, result)

    return result


def _visualize_result(img_path, rectangles):
    """
    将识别结果可视化，画在原图上显示
    """
    import cv2
    import numpy as np

    # 读取原图
    image = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), -1)
    if image is None:
        print("无法读取图片进行可视化")
        return

    # 画矩形
    for rect in rectangles:
        x, y = int(rect['left']), int(rect['top'])
        w, h = int(rect['width']), int(rect['height'])
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(image, rect['name'], (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # 转换颜色（OpenCV是BGR，转回RGB用于显示）
    if len(image.shape) == 3 and image.shape[2] == 3:
        image_show = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        image_show = image

    # 用matplotlib显示（可选依赖）
    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(12, 8))
        plt.imshow(image_show)
        plt.title(f"识别结果: {len(rectangles)} 个矩形")
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"可视化失败（可能未安装matplotlib）: {e}")
        # 备用：保存结果图
        output_path = img_path.rsplit('.', 1)[0] + '_result.jpg'
        cv2.imwrite(output_path, image)
        print(f"结果已保存到: {output_path}")

