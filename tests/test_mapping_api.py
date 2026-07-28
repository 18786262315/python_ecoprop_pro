"""
测试画图API /mapping

参数说明:
- userId: 用户ID
- token: 用户token
- brokeId: 业务ID
- sitePlanId: 画图方案ID
- filepath: 图片文件路径
"""
import requests

# ========== 配置区域 - 请替换以下参数 ==========
BASE_URL = "http://localhost:7777"  # 根据实际情况修改
USER_ID = "6"  # 用户ID
TOKEN = "f09a7cc6687c4916991c4addb2a06441"
BROKE_ID = "0c5d80359cc5416a9ea953fdebcbfc20"
SITE_PLAN_ID = "e5f007b39ba74e4d9e8db47b1637a696"
FILE_PATH = r"https://img.singmap.com/upload/broke/0c5d80359cc5416a9ea953fdebcbfc20/7474b1724023430aa9eb0a05e5000ee1/siteplanImg/1060a877bd684885b23a5bc6738402cd.jpg"  # 例如: r"D:\images\floorplan.jpg"
# project_id = "3089426bf28744ae9baefd07ef0565f1"
# ===========================================


def test_mapping_api():
    url = f"{BASE_URL}/Transaction/mapping"

    # 注意：userId 也是必填字段（基类 userInfo 定义）
    payload = {
        "userId": USER_ID,
        "agentId": USER_ID, 
        "token": TOKEN,
        "brokeId": BROKE_ID,
        "sitePlanId": SITE_PLAN_ID,
        "filepath": FILE_PATH,
    }

    print(f"请求URL: {url}")
    print(f"请求参数: {payload}")

    try:
        response = requests.get(url, json=payload)  # 使用 json 参数发送 JSON body
        print(f"\n状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n解析后的JSON: {data}")
            return data
        else:
            print(f"\n请求失败!")
            return None

    except requests.exceptions.ConnectionError:
        print("连接错误: 无法连接到服务器，请确认服务是否启动")
        return None
    except requests.exceptions.Timeout:
        print("请求超时")
        return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None


if __name__ == "__main__":
    # 先测试图片URL是否可以访问
    print("=== 测试图片URL可访问性 ===")
    try:
        resp = requests.get(FILE_PATH, timeout=15, verify=False)
        print(f"图片URL状态码: {resp.status_code}")
        print(f"Content-Length: {len(resp.content)} bytes")
    except Exception as e:
        print(f"图片URL访问失败: {e}")

    print("\n=== 调用API ===")
    test_mapping_api()
