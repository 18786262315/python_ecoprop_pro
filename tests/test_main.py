from fastapi.testclient import TestClient
import sys
from pathlib import Path


# 获取项目根目录（manger 和 tests 的父目录）
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# 导入模块
import manger

print(manger.test)

client = TestClient(manger.app)

def test_read_root():
    response = client.get("/")
    print(response.status_code)
    assert 1 + 1 == 2
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}
def test_pro_info():
    ...
    response = client.get("/project/")
    print(response.json() )
    assert response.status_code == 200
    assert response.json() == "Mixgo Make PDF API !"