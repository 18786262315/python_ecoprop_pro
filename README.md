



# 介绍
这是一个基于 FastAPI 的 PDF 生成器
之前有部分功能是使用比较旧文件生成方式，使用 reportlab 库进行生成
因改动成本较大，所以暂时保留。

需要安装 wkhtmltopdf

# python版本 
python3.9


# 安装插件
pip install -r requirements.txt

# 虚拟环境切换： conda activate FastAPI
FastAPI 程序启动 ：
# uvicorn manger:app --port 7777 --reload
正式环境后台运行 无需其他的管理工具 ：
# nohup uvicorn manger:app --host 0.0.0.0 --port 7777 --reload  > /home/mixgo/project/python/logs/log.txt 2>&1 &

# 部署注意事项
1、字体引用位置检测
2、静态文件位置检测
3、端口问题，目前使用7777
4、部署时，请将项目目录下的logs目录，复制到部署目录下，并修改权限为777

# ubuntu 部署记录

# 使用 sudo 权限安装
sudo apt update
sudo apt install python3.12-venv  # 根据你的 Python 版本调整（如 python3.10-venv）

# 进入项目目录（如果尚未进入）
cd ~/ecoprop_python/python_ecoprop_pro

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip3 install -r requirements.txt

# 程序启动 :
uvicorn manger:app --port 7777 --reload

# 正式环境后台运行 无需其他的管理工具 :
nohup uvicorn manger:app --host 0.0.0.0 --port 7777 --reload  > /home/mixgo/project/python/logs/log.txt 2>&1 &

