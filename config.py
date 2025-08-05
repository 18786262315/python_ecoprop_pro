
import os

class Config:
    # SECRET_KEY = os.urandom (24)
    # MYSQL_USER = 'root'
    # MYSQL_PASS = 'ycc962464'
    # MYSQL_HOST = '127.0.0.1'
    # MYSQL_PORT = '3306'
    # MYSQL_DB = 'fastapi_models'
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:ycc962464@127.0.0.1:3306/model_file'
    # SQLALCHEMY_COMMIT_ON_TEARDOWN =True
    # SQLALCHEMY_TRACK_MODIFICATIONS = True
    # email_host = 'smtp.qq.com'  # 设置服务器
    # mail_pwd = "zlamhlqmvtbybcgb"  # 口令
    # email_receivers = '843092012@qq.com'
    # SECRET_KEY = 'abcdefg'
    # # UPLOAD_FOLDER = r'\my_pro\python\mixgo_model_file\file'
    # UPLOAD_FOLDER = R'\home\upload'
    # # JSONIFY_MIMETYPE = "application/json"
    # JSON_AS_ASCII = False  # support Chinese
    # JSON_SORT_KEYS = False  # don't sort when jsonify （ref）



    # PDF Set
    
    # 本地调试 ===============================================================================
    # envs = "cc" # 本地
    # imgpath = 'https://img.singmap.com'
    # urlpath = 'https://api.singmap.com' #API
    # now_host = "https://api.singmap.com"
    # filepath = os.getcwd() # 当前文件路径 
    # returnpaths = os.getcwd() # 当前文件路径 
    # wkhtml_path = R"D:\OtherApps\wkhtmltopdf\bin\wkhtmltopdf.exe"  # wkhtmltopdf 的路径
    # ecoprop_temp_path = os.path.join(os.getcwd(),'temp') # 当前文件路径 
    # ecoprop_return_path = os.path.join(os.getcwd(),'pdf') # 当前文件路径 
    # ReLoSG_HOST = "http://192.168.0.145:4501"

    # 测试环境 ===============================================================================
    # envs = "test" # 测试
    # imgpath = 'http://192.168.0.145:8083'
    # urlpath = 'http://192.168.0.145:9998'
    # now_host = "http://127.0.0.1:9998"
    # filepath = '/home/mixgo_py_pro'
    # wkhtml_path = R"D:\OtherApps\wkhtmltopdf\bin\wkhtmltopdf.exe"  # wkhtmltopdf 的路径
    # returnpaths = "/home/mixgo_py_pro"
    # ecoprop_temp_path = "/home/upload/broke/ecoprop/temp"
    # ecoprop_return_path = "/home/upload/broke/ecoprop/pdf"

    # 线上 ===============================================================================
    # envs = "release" # 发布
    # imgpath = 'https://img.singmap.com'
    # urlpath = 'https://api.singmap.com' #API
    # now_host = "http://127.0.0.1:9998" 
    # wkhtml_path = R"/usr/bin/wkhtmltopdf"  # wkhtmltopdf 的路径
    # filepath = '/home/upload/broke/pnd/file/report'
    # returnpaths = "/home/upload/broke/pnd/file/report"
    # ecoprop_temp_path = "/home/upload/broke/ecoprop/temp"
    # ecoprop_return_path = "/home/upload/broke/ecoprop/pdf"


    # 香港独立部署程序 ===============================================================================
    envs = "release" # 发布
    imgpath = 'https://ecoprop.s3.ap-southeast-1.amazonaws.com' # oss 图片
    host_imgpath = 'http://imagesingmap.mypropdb.com' # 服务所在的本地图片 /upload 地址 

    urlpath = 'http://127.0.0.1:9998' #API
    now_host = "http://127.0.0.1:9998"

    # ReLoSG 项目API地址
    ReLoSG_HOST = "http://192.168.0.145:4501" 

    # wkhtmltopdf 的路径
    wkhtml_path = R"/usr/bin/wkhtmltopdf"

    filepath = os.getcwd()  # 项目所在路径 
    returnpaths = "/home/upload/savills/pnd/file/report" # Pnd 报告保存路径
    ecoprop_temp_path = os.path.join(os.getcwd(),'temp') # 项目模板所在路径 
    ecoprop_return_path = "/home/upload/savills/ecoprop/pdf" # Ecoprop 报告保存路径


    # Link 地址
    ecoprop_share_path = "http://share.ecoprop.com/" # # Ecoprop 分享路径
    ecoprop_share_paths = "https://share.ecoprop.com/" # # https 
    ecoprop_pro_vs_path = "https://app.singmap.com/share/index.html#/vsProject" # Ecoprop Pro 路径



    # API path ===============================================================================
    # PND API 路径
    PND_PROJECT_INFO = "/pnd-api/project/queryProjectInfoById"
    PND_PDF_PROJECT_LIST = "/pnd-api/pdf/queryPdfProjectList"
    PND_PDF_DISTRICT_LIST = "/pnd-api/pdf/queryPdfDistrictList"
    PND_PROJECT_RETAIL_COUNT = "/pnd-api/project/queryRetailCount"
    PND_PROJECT_INFO_BIG = "/pnd-api/project/queryProjectInfoById_big"

    # APP Service API 路径
    APP_PROJECT_BEDROOM_COUNT = "/app-service/project/queryProjectCountByBedroom"
    APP_AGENT_SHARE_INFO = "/app-service/agent/queryShareAgentInfo"
    APP_PROJECT_INFO = "/app-service/project/queryProjectInfo"
    APP_UNIT_TYPE_REPORT = "/app-service/unit/unitTypeReport"
    APP_SITEPLAN_IMG = "/app-service/siteplan/querySitePlanImg"
    APP_MEDIA_SHARE = "/app-service/media/queryProjectShareMedia"
    APP_FLOOR_PLANS = "/app-service/floor/queryFloorPlansByType"
    APP_UNIT_INFO = "/app-service/unit/getUnitInfo"

    @staticmethod
    def init_app(app):
        pass

