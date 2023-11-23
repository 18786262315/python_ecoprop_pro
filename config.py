
import os

class Config:
    # SECRET_KEY = os.urandom (24)
    MYSQL_USER = 'root'
    MYSQL_PASS = 'ycc962464'
    MYSQL_HOST = '127.0.0.1'
    MYSQL_PORT = '3306'
    MYSQL_DB = 'fastapi_models'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:ycc962464@127.0.0.1:3306/model_file'
    SQLALCHEMY_COMMIT_ON_TEARDOWN =True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    email_host = 'smtp.qq.com'  # 设置服务器
    mail_pwd = "zlamhlqmvtbybcgb"  # 口令
    email_receivers = '843092012@qq.com'
    SECRET_KEY = 'abcdefg'
    # UPLOAD_FOLDER = r'\my_pro\python\mixgo_model_file\file'
    UPLOAD_FOLDER = R'\home\upload'
    # JSONIFY_MIMETYPE = "application/json"
    JSON_AS_ASCII = False  # support Chinese
    JSON_SORT_KEYS = False  # don't sort when jsonify （ref）



    # PDF Set
    # 本地调试
    # envs = "cc" # 本地
    # imgpath = 'https://img.singmap.com'
    # urlpath = 'https://api.singmap.com' #API
    # now_host = "https://api.singmap.com"
    # filepath = os.getcwd() # 当前文件路径 
    # returnpaths = os.getcwd() # 当前文件路径 
    # ecoprop_temp_path = os.path.join(os.getcwd(),'temp') # 当前文件路径 
    # ecoprop_return_path = os.path.join(os.getcwd(),'pdf') # 当前文件路径 

    # 测试环境
    # envs = "test" # 测试
    # imgpath = 'http://192.168.0.145:8083'
    # urlpath = 'http://192.168.0.145:9998'
    # now_host = "http://127.0.0.1:9998"
    # filepath = '/home/mixgo_py_pro'
    # returnpaths = "/home/mixgo_py_pro"
    # ecoprop_temp_path = "/home/upload/broke/ecoprop/temp"
    # ecoprop_return_path = "/home/upload/broke/ecoprop/pdf"

    # 线上
    envs = "release" # 发布
    imgpath = 'https://img.singmap.com'
    urlpath = 'http://127.0.0.1:9998' # https://api.singmap.com
    now_host = "http://127.0.0.1:9998" 
    filepath = '/home/upload/broke/pnd/file/report'
    returnpaths = "/home/upload/broke/pnd/file/report"
    ecoprop_temp_path = "/home/upload/broke/ecoprop/temp"
    ecoprop_return_path = "/home/upload/broke/ecoprop/pdf"

    @staticmethod
    def init_app(app):
        pass

