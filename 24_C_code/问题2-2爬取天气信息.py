import requests
import re
import time as delay
from bs4 import BeautifulSoup
import pandas as pd
import json


# 定义一个函数，用于获取网页的源代码
def get_page(url, headers):
    html = requests.get(url, headers=headers)
    if html.status_code == 200:
        html.encoding = html.apparent_encoding
        return html.text
    else:
        print("Failed to fetch page:", url)
        return None


# 定义一个函数，用于解析网页中的数据，并返回一个数据框
def parse_page(html):
    # 创建空列表，用于存储数据
    date_box = []
    max_temp = []
    min_temp = []
    weh = []
    wind = []
    # 使用 BeautifulSoup 解析网页
    bs = BeautifulSoup(html, 'html.parser')
    # 找到包含数据的标签
    data = bs.find_all(class_='thrui')
    # 使用正则表达式提取数据
    date = re.compile('class="th200">(.*?)</div>')
    tem = re.compile('class="th140">(.*?)</div>')
    time = re.findall(date, str(data))
    for item in time:
        # 不提取星期数据
        date_box.append(item[:10])
    temp = re.findall(tem, str(data))
    for i in range(len(temp) // 4):
        max_temp.append(temp[i * 4 + 0])
        min_temp.append(temp[i * 4 + 1])
        weh.append(temp[i * 4 + 2])
        wind.append(temp[i * 4 + 3])

    # 将数据转换为数据框，不添加星期列
    datas = pd.DataFrame({'日期': date_box, '最高温度': max_temp, '最低温度': min_temp, '天气': weh, '风向': wind})
    return datas


# 定义一个函数，用于将数据框保存为 CSV 文件
def save_to_csv(datas, city, time):
    """
    将天气数据保存为 CSV 文件

    参数:
    datas (DataFrame): 包含天气数据的 DataFrame
    city (str): 城市名称
    time (str): 时间（年月，如 202301）
    """
    # 创建保存路径，格式为：data/城市_时间.csv
    save_path = f'data/{city}_{time}.csv'

    try:
        # 确保目录存在
        import os
        os.makedirs('data', exist_ok=True)

        # 保存数据框为 CSV 文件
        datas.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"成功将 {city} {time} 的天气数据保存到 {save_path}")
    except Exception as e:
        print(f"保存 CSV 文件失败: {e}")


def crawl_weather(city, code, time):
    # 根据城市的编码和时间范围，生成网页的 url
    url = "http://lishi.tianqi.com/{}/{}.html".format(code, time)
    # 定义请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Cookie': 'lianjia_uuid=9d3277d3-58e4-440e-bade-5069cb5203a4;'
                  'UM_distinctid=16ba37f7160390-05f17711c11c3e-454c0b2b-100200-16ba37f716618b;'
                  ' _smt_uid=5d176c66.5119839a;'
                  'sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2216ba37f7a942a6-0671dfdde0398a-454c0b2b-1049088-16ba37f7a95409%22%2C%22%24device_id%22%3A%2216ba37f7a942a6-0671dfdde0398a-454c0b2b-1049088-16ba37f7a95409%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; '
                  '_ga=GA1.2.1772719071.1561816174; '
                  'Hm_lvt_9152f8221cb6243a53c83b956842be8a=1561822858;'
                  '_jzqa=1.2532744094467475000.1561816167.1561822858.1561870561.3;'
                  'CNZZDATA1253477573=987273979-1561811144-%7C1561865554;'
                  'CNZZDATA1254525948=879163647-1561815364-%7C1561869382;'
                  'CNZZDATA1255633284=1986996647-1561812900-%7C1561866923;'
                  'CNZZDATA1255604082=891570058-1561813905-%7C1561866148;'
                  '_qzja=1.1577983579.1561816168942.1561822857520.1561870561449.1561870561449.1561870847908.0.0.0.7.3;'
                  'select_city=110000; lianjia_ssid=4e1fa281-1ebf-e1c1-ac56-32b3ec83f7ca;'
                  'srcid=eyJ0Ijoie1wiZGF0YVwiOlwiMzQ2MDU5ZTQ0OWY4N2RiOTE4NjQ5YmQ0ZGRlMDAyZmFhO'
                  'DZmNjI1ZDQyNWU0OGQ3MjE3Yzk5NzFiYTY4ODM4ZThiZDNhZjliNGU4ODM4M2M3ODZhNDNiNjM1NzMzNjQ4'
                  'ODY3MWVhMWFmNzFjMDVmMDY4NWMyMTM3MjIxYjBmYzhkYWE1MzIyNzFlOGMyOWFiYmQwZjBjYjcyNmI'
                  'wOWEwYTNlMTY2MDI1NjkyOTBkNjQ1ZDkwNGM5ZDhkYTIyODU0ZmQzZjhjODhlNGQ1NGRkZTA0ZTBlZDFiN'
                  'mIxOTE2YmU1NTIxNzhhMGQ3Yzk0ZjQ4NDBlZWI0YjlhYzFiYmJlZjJlNDQ5MDdlNzcxMzAwMmM1ODBlZDJkNm'
                  'IwZmY0NDAwYmQxNjNjZDlhNmJkNDk3NGMzOTQxNTdkYjZlMjJkYjAxYjIzNjdmYzhiNzMxZDA1MGJlNjBmNzQ'
                  'xMTZjNDIzNFwiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCIzMGJlNDJiN1wifSIsInIiOiJodHRwczovL2'
                  'JqLmxpYW5qaWEuY29tL3p1ZmFuZy9yY28zMS8iLCJvcyI6IndlYiIsInYiOiIwLjEifQ=='
    }
    try:
        # 获取网页的源代码
        print(url)
        html = get_page(url, headers)
        # 解析网页中的数据，并返回一个数据框
        datas = parse_page(html)
        # 将数据框保存为 CSV 文件
        save_to_csv(datas, city, time)
        # 打印提示信息
        print("成功爬取 {} 的 {} 的历史天气数据".format(city, time))
    except Exception as e:
        print("爬取 {} 的 {} 历史天气数据失败：{}".format(city, time, e))


# 从本文件夹下的 city.json 文件中读取城市名称和编码
with open('city_my.json', 'r', encoding='utf-8') as f:
    city_dict = json.load(f)

# 定义一个列表，存储需要爬取的时间范围
time_list = ["202501", "202502","202503", "202504","202505"]

# 遍历城市字典和时间列表，调用爬取函数
for city, code in city_dict.items():
    for time in time_list:
        crawl_weather(city, code, time)
        delay.sleep(5)