import os
import time
from loguru import logger as loguru_logger

# 日志简单配置
# 具体其他配置 可自行参考 https://github.com/Delgan/loguru

# format 参数： {time} {level} {message}、  {time:YYYY-MM-DD at HH:mm:ss} | {level} | {message} 记录参数
#  level 日志等级
# rotation 参数：1 week 一周、00:00每天固定时间、 500 MB 固定文件大小
# retention 参数： 10 days 日志最长保存时间
# compression 参数： zip 日志文件压缩格式
# enqueue 参数 True 日志文件异步写入
# serialize 参数： True 序列化json
# encoding 参数： utf-8 字符编码、部分情况会出现中文乱码问题
# logger.info('If you are using Python {}, prefer {feature} of course!', 3.6, feature='f-strings') 格式化输入内容
#  可通过等级不同对日志文件进行分割储存 
# @logger.catch 异常代码装饰器、直接定位错误代码位置。

# 业务多了，日志也多了，我们可以为每个业务分别创建一个日志记录器
loggers = {}
def get_log_path(business_name, level="info") -> str:
        """
        根据业务名+等级+日期 生成日志文件名
        需要传入 业务名 和 日志等级
        """
        basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_path = os.path.join(basedir, 'logs')

        if not os.path.exists(log_path):
            os.makedirs(log_path, exist_ok=True)

        time_str = time.strftime("%Y-%m-%d")
        log_file = f"{business_name}_{level}_{time_str}.log"
        log_path = os.path.join(log_path, log_file)

        return log_path

def get_logger(name: str):
    """
    获取日志记录器
    """
    if name in loggers:
        return loggers[name]
    
    # 创建一个新的日志记录器
    new_logger = loguru_logger.bind(name=name)
    # new_logger.remove()
    new_logger.add(
                    get_log_path(name,'INFO'),  # 生成日志文件名
                    rotation="12:00", # 每天12点分割
                    retention="5 days",  # 保留5天
                    enqueue=True, # 异步写入
                    encoding='utf-8',  # 编码格式
                    filter=lambda record: record["extra"].get("name") == name # 过滤器，对业务进行区分记录
                    )
    
    new_logger.add(
                    get_log_path(name,'ERROR'), 
                    rotation="12:00", 
                    retention="5 days",
                    level='ERROR',  # 只记录错误
                    enqueue=True,
                    encoding='utf-8', 
                    filter=lambda record: record["extra"].get("name") == name
                   )

    loggers[name] = new_logger
    return new_logger



# 不一定要统一在这边调用，可以在需要的地方调用。 方便维护的话还是放在这边好一些。

# # 示例：为 business_b 创建日志记录器
# business_b_logger = get_logger("business_b")

# # 示例：为 business_a 创建日志记录器
# business_a_logger = get_logger("business_a")

# # 示例：为 manger 创建日志记录器
manger_logger = get_logger("manger")

# 初始化日志记录器
logger = get_logger("root")


logger.info('If you are using Python {}, prefer {feature} of course!', 3.6, feature='f-strings')


manger_logger.info('If you are using Python {}, prefer {feature} of course!', 3.7, feature='f-strings')
