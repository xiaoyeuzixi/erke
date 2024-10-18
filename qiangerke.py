import requests
import json
import time
import re
from io import BytesIO
from PIL import Image
import ddddocr
from PIL import ImageEnhance
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


stop_event = threading.Event()

# 输入SSID
SSID = str(input("请输入SSID:"))
print("ssid为:", SSID)

excluded_keywords = {'军事', '训练', '军', '名单', '工作', '体验', '华岩', '聚会', '赛', '跑'}

def activities():
    """获取可申请活动并保存到本地JSON文件"""
    url = 'https://2class.cqtbi.edu.cn/Student/Activity/getActivityCanApply.html'
    headers = {
        'Cookie': f'SSID={SSID}',
    }
    response = requests.post(url, headers=headers)
    activities = json.loads(response.text)

    # 保存活动到文件
    with open('text.json', 'w', encoding='utf-8') as f:
        json.dump(activities, f, ensure_ascii=False, indent=4)
    
    print("活动数据已成功保存。")
    return activities

def screening(activities):
    """筛选出可申请的活动ID"""
    activityID = []
    for activity in activities:
        if '报名未开始' in activity.get('status2Name', ''):
            if not any(keyword in activity.get('activityName', '') for keyword in excluded_keywords):
                activityID.append(activity['activityID'])
                print(f'正在报名:', activity['activityName'])
    return activityID

def timestamp_list(activities):
    """获取可申请活动的时间戳"""
    timestamps = []
    for activity in activities:
        if '报名未开始' in activity.get('status2Name', ''):
            if not any(keyword in activity.get('activityName', '') for keyword in excluded_keywords):
                timestamps.append(activity['applyStartDate'])
                print(f'活动开始时间:', activity['applyStartDate'])
    return timestamps

def sign_up(activityID, ver_code, s1, s2):
    """进行报名请求"""
    url = "https://2class.cqtbi.edu.cn/Student/activity/applyGo.html"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://2class.cqtbi.edu.cn",
        "Referer": f"https://2class.cqtbi.edu.cn/Student/Activity/apply.html?activityID={activityID}&retUrl=JTJGU3R1ZGVudCUyRkFjdGl2aXR5JTJGaW5kZXguaHRtbA==",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Connection": "keep-alive",
    }

    # 设置请求体的数据
    data = {
        "activityID": activityID,
        "activityApplyRand": ver_code,
        "s1": s1,
        "s2": s2,
    }

    # 设置 cookies
    cookies = {
        "SSID": SSID,
        "activityApplyTimes": "1",
        "activityApplyTimeStart": str(int(time.time())),  # 使用当前时间戳
    }

    try:
        response = requests.post(url, headers=headers, data=data, cookies=cookies)
        response.raise_for_status()
        print("报名状态:", response.text)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误发生: {http_err}")
    except Exception as err:
        print(f"发生错误: {err}")

def s1_2(activityID):
    """获取s1和s2"""
    url = f'https://2class.cqtbi.edu.cn/Student/Activity/apply.html?activityID={activityID}&retUrl=JTJGU3R1ZGVudCUyRkFjdGl2aXR5JTJGaW5kZXguaHRtbA=='
    cookies = {
        'SSID': SSID,
        'activityApplyTimes': '1',
        'activityApplyTimeStart': str(int(time.time())),
    }
    response = requests.get(url, cookies=cookies)
    s1 = ''.join(re.findall(r's1:"(.*?)"', response.text))
    s2 = ''.join(re.findall(r's2:"(.*?)"', response.text))
    return s1, s2

def image():
    """获取验证码图片"""
    cookies = {
        'SSID': SSID,
        'activityApplyTimes': '1',
        'activityApplyTimeStart': str(int(time.time())),
    }
    url = "https://2class.cqtbi.edu.cn/Student/Activity/verifycode.html"
    response = requests.get(url, cookies=cookies)

    if response.status_code == 200 and 'image' in response.headers.get('Content-Type'):
        img = Image.open(BytesIO(response.content))
        img.save("1.png")
        print("验证码图片已保存。")
    else:
        print(f"无法获取图片，状态码: {response.status_code}")

def code():
    """处理验证码并返回识别结果"""
    image = Image.open('1.png')
    rgb_image = image.convert('RGB')
    width, height = rgb_image.size
    processed_image = Image.new('RGB', (width, height))

    for x in range(width):
        for y in range(height):
            pixel = rgb_image.getpixel((x, y))
            r, g, b = pixel
            processed_image.putpixel((x, y), (0, 0, 0) if r > 200 and g > 200 and b > 200 else (255, 255, 255))

    gray_image = processed_image.convert('L')
    threshold = 128
    binary_image = gray_image.point(lambda p: 255 if p > threshold else 0)

    enhancer = ImageEnhance.Contrast(binary_image)
    enhanced_image = enhancer.enhance(2.0)
    enhanced_image.save('processed_image.png')

    ocr = ddddocr.DdddOcr()
    with open('processed_image.png', 'rb') as f:
        img_bytes = f.read()
    res = ocr.classification(img_bytes)

    verification_code = re.findall(r'\d+', res)
    return verification_code[0] if verification_code else None

def wait_for_timestamp(timestamp):
    """等待直到目标时间戳"""
    current_time = int(time.time())
    while current_time < timestamp:
        time_diff = timestamp - current_time
        print(f"等待 {time_diff} 秒直到 {timestamp}，当前时间: {current_time}")
        time.sleep(min(time_diff, 2))
        current_time = int(time.time())
    print(f"当前时间 {current_time} 达到或超过目标时间 {timestamp}")

def process_activity(activityID, timestamp, whitelist_id):
    while not stop_event.is_set():
        print(f"处理活动ID: {activityID}，时间戳: {timestamp}")
        time.sleep(1)  # 模拟活动处理时间
        if stop_event.is_set():
            print(f"活动ID: {activityID} 被停止")
            break

def main():
    activities_data = activities()
    ID = screening(activities_data)
    print("可报名活动ID:", ID)

    # id白名单
    whitelist_id = []

    # 时间戳名单
    time_1 = timestamp_list(activities_data)
    print("活动开始时间戳:", time_1)

    # 使用线程池同时处理多个活动
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for i in range(len(ID)):
            activityID = ID[i]
            timestamp = int(time_1[i])
            futures.append(executor.submit(process_activity, activityID, timestamp, whitelist_id))

        for future in as_completed(futures):
            if stop_event.is_set():
                break
            try:
                future.result()
            except Exception as exc:
                print(f"处理活动时发生错误: {exc}")

def start_main_loop():
    while True:
        stop_event.clear()
        main_thread = threading.Thread(target=main)
        main_thread.start()

        # 等待1小时后停止当前任务
        time.sleep(3600)

        # 设置停止事件来终止当前的任务线程
        print("停止当前任务并刷新...")
        stop_event.set()

        # 等待任务线程结束
        main_thread.join()

if __name__ == '__main__':
    try:
        start_main_loop()
    except KeyboardInterrupt:
        print("手动终止程序...")
        stop_event.set()