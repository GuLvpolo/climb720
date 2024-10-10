'''
Version: 2.4.0
由Pyinstaller打包
'''
import time
from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service 
import requests
from bs4 import BeautifulSoup as BS
import together
import os

#创建文件夹
if not os.path.exists("result"):
    os.makedirs("result")
if not os.path.exists("img"):
    os.makedirs("img")
#获取标题
base_url = input('请输入下载地址: ')
headers = {
    "Origin": "https://720yun.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
}
response = requests.get(base_url, headers=headers)
html=response.text
soup=BS(html,'html.parser')
vs = soup.find("title")
title = vs.text

print('开始获取图片连接')
urlHead = ''
while(urlHead == ''):
    server = Server('resources\\browsermob-proxy-2.1.4\\bin\\browsermob-proxy.bat', {'port': 8739})
    server.start()
    proxy = server.create_proxy()
    chrome_options = Options()
    chrome_options.binary_location='resources\\chrome.exe'
    #隐藏浏览器
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # 设置代理
    chrome_options.add_argument('--proxy-server={0}'.format(proxy.proxy))
    # service = Service('resources\\chromedriver.exe') 
    driver = webdriver.Chrome(executable_path='resources\\chromedriver.exe',options=chrome_options)
    proxy.new_har('html_list', options={'captureContent': True})
    driver.get(base_url)
    # 设置休眠时间,以充分获取网络资源
    time.sleep(5)
    # proxy.wait_for_traffic_to_stop(10,11)
    result = proxy.har
    for ent in result['log']['entries']:
        url = ent['request']['url']
        if (url.find("panoimg") != -1):
            urlHead = url
            break
    urlHead = os.path.dirname(urlHead) + "/"
    #关闭连接
    server.stop()
    proxy.close()
    driver.quit()

    os.system('cls')

    if (urlHead == r'/'):
        urlHead = ''
        i = 10
        while (i > 0):
            print('\r'*15 + "未获取到链接,将在" + str(i-1) + "秒后重试",end='')
            i = i - 1
            time.sleep(1)


headers = {
    "Origin": "https://720yun.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    "Referer":"https://www.720yun.com/",
}
thumb = r"thumb.jpg?x-oss-process=image%2Fresize%2Cw_200%2Ch_200%2Fauto-orient%2C1"
#获取预览图
index = str(urlHead).find("resource")
r = requests.get(url="https://ssl-thumb2.720static.com/" + str(urlHead)[index:] + thumb, headers=headers)
if r.status_code == 200:
    with open('result/preview.jpg', 'wb') as f:
        f.write(r.content)

print("开始下载图片")

import winsound

#尝试获取图片
r = requests.get(url=urlHead+"b/l3/01/l3_b_01_01.jpg", headers=headers)
if r.status_code == 200:
    r = requests.get(url=urlHead+"b/l3/01/l3_b_01_06.jpg", headers=headers)
    if r.status_code == 200:
        imgMatrix = '8*8'
    else:
        imgMatrix = '5*5'
    # 开始请求
    urlsList = list()
    # 构造6个面
    for faceCode in ('b','d','f','l','r','u'):
        # 似乎有3层清晰度，这里只取第三层
        for layerCode in range(3,4):
            if imgMatrix == '5*5':
                # 150张图片
                # 每层里面一般又有5个子文件夹（表示矩阵的行）
                for subFold in range(1,6):
                    # 每个子文件夹里面又有5个图片（表示矩阵的列）
                    for picCode in range(1,6):
                        pathStr = "{}/l{}/0{}/l{}_{}_0{}_0{}.jpg".format(faceCode, layerCode, subFold, layerCode, faceCode, subFold, picCode)
                        urlsList.append(urlHead + pathStr)
            else:
                # 384张图片
                for subFold in range(1,9):
                    # 每个子文件夹里面又有5个图片（表示矩阵的列）
                    for picCode in range(1,9):
                        pathStr = "{}/l{}/0{}/l{}_{}_0{}_0{}.jpg".format(faceCode, layerCode, subFold, layerCode, faceCode, subFold, picCode)
                        urlsList.append(urlHead + pathStr)

    for i in range(len(urlsList)):
        url = urlsList[i]
        print('\r'*8 + "{}/{}".format(i+1, len(urlsList)), end='')
        try:
            r = requests.get(url=url, headers=headers)
        except Exception as e:
            print('get 出了点问题：{}'.format(e))

        if r.status_code == 200:
            with open('img/' + url.split('/')[-1], 'wb') as f:
                f.write(r.content)
    print("\n下载完成")
    together.拼接所有('img/',title,base_url)
else:
    #或许没有三层
    r = requests.get(url=urlHead+"mobile_b.jpg", headers=headers)
    if r.status_code == 200:
        i = 0
        for faceCode in ('b','d','f','l','r','u'):
            url = urlHead+"mobile_{}.jpg".format(faceCode)
            r = requests.get(url = url, headers=headers)
            print('\r'*3 + "{}/{}".format(i+1, 6), end='')
            if r.status_code == 200:
                with open('result/' + faceCode + ".jpg", 'wb') as f:
                    f.write(r.content)
            i = i + 1
        print("\n下载完成")
        #拼接全景图
        winsound.Beep(600, 500)
        string = ""
        while string != 'y':
            string = input("输入y后按回车键开始拼接")
        together.a(title,base_url)