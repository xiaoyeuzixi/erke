import requests
import json
import time
import re
from io import BytesIO
from PIL import Image
import ddddocr
from PIL import ImageEnhance



SSID = str(input("请输入SSID:"))
print("ssid为:", SSID)

timestamp = int(time.time())
excluded_keywords = {'军事', '训练', '军', '名单', '工作', '体验', '华岩', '聚会', '赛', '跑'}
excluded_keywords = {'军事'}


def activities():
    url = 'https://2class.cqtbi.edu.cn/Student/Activity/getActivityCanApply.html'
    hreader = {
    'Cookie': f'SSID={SSID}',
    }

    print(hreader)
    data = {

        }
    response = requests.post(url, headers=hreader, data=data)
    text = response.text
    activities = json.loads(text)
    #保存到本地
    with open('text.json', 'w', encoding='utf-8') as f:
        json.dump(activities, f, ensure_ascii=False, indent=4)
    print(activities)
    # 读取 JSON 文件
    with open(r'e:\GitHub\二课网页\text.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 假设活动数据在 'activities' 键中，需要根据实际情况调整
    # 这里假设数据是以列表形式存在
    activities = data  # 直接使用 data，因为你提供的例子没有包含活动列表的键

    # 按照 applyStartDate 排序
    sorted_activities = sorted(activities, key=lambda x: int(x['applyStartDate']))

    # 重新保存到 JSON 文件
    with open(r'e:\GitHub\二课网页\text.json', 'w', encoding='utf-8') as file:
        json.dump(sorted_activities, file, ensure_ascii=False, indent=4)

    print("数据已成功排序并保存。")


def screening():
    with open('text.json', 'r', encoding='utf-8') as f:
        activities = json.load(f)

        # 筛选出可申请的活动
        activityID = []
        for activity in activities:
            if '报名' in activity.get('status2Name', ''):
                if not any(keyword in activity.get('activityName', '') for keyword in excluded_keywords):
                    activityID.append(activity['activityID'])
                    print(f'正在报名:',activity['activityName'])
        print(activityID)
        return activityID

#获取时间戳    
def timestamp_list():
    with open('text.json', 'r', encoding='utf-8') as f:
        activities = json.load(f)

        # 筛选出可申请的活动
        timestamps = []
        for activity in activities:
            if '报名' in activity.get('status2Name', ''):
                if not any(keyword in activity.get('activityName', '') for keyword in excluded_keywords):
                    timestamps.append(activity['applyStartDate'])
                    print(f'正在报名:',activity['applyStartDate'])
        print(timestamps)
        return timestamps



def sign_up():
    url = "https://2class.cqtbi.edu.cn/Student/activity/applyGo.html"

    # 设置请求头
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://2class.cqtbi.edu.cn",
        "Referer": "https://2class.cqtbi.edu.cn/Student/Activity/apply.html?activityID=85479&retUrl=JTJGU3R1ZGVudCUyRkFjdGl2aXR5JTJGaW5kZXguaHRtbA==",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Connection": "keep-alive",
    }

    # 设置请求体的数据
    data = {
        "activityID": {activityID},
        "activityApplyRand": {ver_code},
        "s1": {s1},
        "s2": f"{s2}",
    }

    # 设置 cookies
    cookies = {
        "SSID": f"{SSID}",
        "activityApplyTimes": "1",
        "activityApplyTimeStart": f"{timestamp}",
    }

    try:
        # 发送 POST 请求
        response = requests.post(url, headers=headers, data=data, cookies=cookies)
        
        # 检查响应状态码
        response.raise_for_status()  # 如果响应代码不是200，将抛出异常
        
        # 打印响应结果
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误发生: {http_err}")
    except Exception as err:
        print(f"发生错误: {err}")

def s1_2():
    

    url = f'https://2class.cqtbi.edu.cn/Student/Activity/apply.html?activityID={activityID}&retUrl=JTJGU3R1ZGVudCUyRkFjdGl2aXR5JTJGaW5kZXguaHRtbA=='
    cookies = {

        'SSID':f'{SSID}',
        'activityApplyTimes':'1',
        'activityApplyTimeStart':f'{timestamp}',
        }

    response = requests.get(url, cookies=cookies)
    text = response.text
    s1 = ''.join(re.findall(r's1:"(.*?)"', text))  # 将s1转化为字符串
    s2 = ''.join(re.findall(r's2:"(.*?)"', text))  # 将s2转化为字符串
    print(s1, s2)
    return s1, s2

def image():
    cookies = {
    'SSID': 'jiqph7llau90l514d3kokgfnr5',
    'activityApplyTimes': '2',
    'activityApplyTimeStart': str(timestamp),  # 确保值是字符串
    }

    # 目标 URL
    url = "https://2class.cqtbi.edu.cn/Student/Activity/verifycode.html"

    # 发送请求，获取图片
    response = requests.get(url, cookies=cookies)

    # 检查请求是否成功
    if response.status_code == 200:
        # 判断响应内容是否是图片
        content_type = response.headers.get('Content-Type')
        if 'image' in content_type:  # 检查内容类型是否为图片
            img = Image.open(BytesIO(response.content))
            img.save("1.png")  # 直接保存图片为文件
            print("图片已保存。")
        else:
            print("返回的内容不是图片。")
    else:
        print(f"无法获取图片，状态码: {response.status_code}")

def code():
    image = Image.open('1.png')

    # 转换为 RGB 模式
    rgb_image = image.convert('RGB')

    # 获取图像的宽度和高度
    width, height = rgb_image.size

    # 创建一个新的空白图像，用于存放处理后的像素
    processed_image = Image.new('RGB', (width, height))

    # 遍历每个像素并处理
    for x in range(width):
        for y in range(height):
            pixel = rgb_image.getpixel((x, y))
            r, g, b = pixel
            # 如果像素接近白色，则变为黑色
            if r > 200 and g > 200 and b > 200:
                processed_image.putpixel((x, y), (0, 0, 0))  # 转换为黑色
            else:
                processed_image.putpixel((x, y), (255, 255, 255))  # 其他颜色变为白色

    # 将图像转换为灰度
    gray_image = processed_image.convert('L')

    # 进行二值化处理
    threshold = 128  # 选择阈值
    binary_image = gray_image.point(lambda p: 255 if p > threshold else 0)

    # 增强对比度
    enhancer = ImageEnhance.Contrast(binary_image)
    enhanced_image = enhancer.enhance(2.0)  # 可调整对比度倍数

    # 保存处理后的图像（可选，检查效果）
    enhanced_image.save('processed_image.png')


    ocr = ddddocr.DdddOcr()
    with open('processed_image.png', 'rb') as f:
        img_bytes = f.read()
    res = ocr.classification(img_bytes)

    verification_code = re.findall(r'\d+', res)  # 提取所有数字
    if verification_code:
        print("验证码是:", verification_code[0])  # 输出第一个找到了的验证码
    else:
        print("未找到验证码")
    return verification_code[0]



if __name__ == '__main__':
    activities()
    ID = screening()
    print(ID)
    image()
    ver_code = code()
    #id白名单
    whitelist_id = []
    #时间戳名单
    time_1 = timestamp_list()
    print(time_1)
    for i in range(len(ID)):
        activityID = ID[i]
        print(f"正在处理活动ID: {activityID}")
        # 遍历时间戳列表
        timestamp = time_1[i]
        current_time = int(time.time())  # 获取当前时间戳
        print(f"当前时间戳: {current_time}")
        print(f"对应时间戳: {timestamp}")
        
        # 检查当前时间是否到达对应时间戳
        if current_time >= timestamp:
            print(f"当前时间已达到时间戳 {timestamp}，执行任务")
            # 检测活动ID是否在白名单中
            if activityID in whitelist_id:
                s1, s2 = s1_2()
                sign_up()
                whitelist_id.append(activityID)
            else:
                print(f"活动ID {activityID} 不在白名单中，跳过报名。")
        