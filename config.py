
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
    @staticmethod
    def init_app(app):
        pass

