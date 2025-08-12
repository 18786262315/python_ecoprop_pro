#!/bin/bash

# 配置项目参数
PROJECT_DIR="$HOME/ecoprop_python/python_ecoprop_pro"
GIT_REPO="https://github.com/18786262315/python_ecoprop_pro.git"  # 替换为实际仓库地址
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/log.txt"
PORT=7777
PYTHON_VENV="venv"
PYTHON_PACKAGE="python3.12-venv"  # Python虚拟环境依赖包

# 确保日志目录存在
mkdir -p "$LOG_DIR"

echo "===== 开始部署: $(date) ====="

# 检查项目目录是否存在，不存在则克隆仓库
if [ ! -d "$PROJECT_DIR" ]; then
    echo "项目目录不存在，从Git克隆仓库..."
    git clone "$GIT_REPO" "$PROJECT_DIR"
    if [ $? -ne 0 ]; then
        echo "克隆仓库失败，请检查仓库地址和网络连接"
        exit 1
    fi
else
    echo "拉取最新代码..."
    cd "$PROJECT_DIR" || exit 1
    git pull
    if [ $? -ne 0 ]; then
        echo "拉取代码失败，继续使用现有代码部署"
    fi
fi

cd "$PROJECT_DIR" || exit 1

# 检查并安装Python虚拟环境依赖
echo "检查Python虚拟环境依赖..."
if ! dpkg -s "$PYTHON_PACKAGE" >/dev/null 2>&1; then
    echo "未找到$PYTHON_PACKAGE，开始安装..."
    sudo apt update -y
    sudo apt install -y "$PYTHON_PACKAGE"
    if [ $? -ne 0 ]; then
        echo "$PYTHON_PACKAGE安装失败，请手动检查"
        exit 1
    fi
else
    echo "$PYTHON_PACKAGE已安装，跳过安装步骤"
fi

# 检查虚拟环境是否存在，不存在则创建
if [ ! -d "$PYTHON_VENV" ]; then
    echo "创建虚拟环境..."
    python3 -m venv "$PYTHON_VENV"
else
    echo "虚拟环境已存在，跳过创建步骤"
fi

# 激活虚拟环境并安装依赖
echo "激活虚拟环境并安装依赖..."
source "$PYTHON_VENV/bin/activate"
pip3 install --upgrade pip
pip3 install -r requirements.txt

# 停止可能正在运行的进程
echo "停止现有进程..."
PID=$(ps aux | grep "uvicorn manger:app" | grep -v grep | awk '{print $2}')
if [ -n "$PID" ]; then
    kill -9 "$PID"
    sleep 2
fi

# 启动应用（正式环境建议移除--reload参数）
echo "启动应用程序..."
nohup uvicorn manger:app --host 0.0.0.0 --port "$PORT" > "$LOG_FILE" 2>&1 &

# 检查是否启动成功
sleep 3
if pgrep -f "uvicorn manger:app" > /dev/null; then
    echo "应用启动成功，端口: $PORT"
    echo "日志文件: $LOG_FILE"
else
    echo "应用启动失败，请查看日志: $LOG_FILE"
    exit 1
fi

echo "===== 部署完成: $(date) ====="
    