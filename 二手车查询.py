"""
由于使用https，所以需要以管理员身份运行
"""
import os
import random
import time
import requests
import json

from share_package import components, wxpusher
from requests.packages import urllib3
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

urllib3.disable_warnings()  # 关闭https的ssl证书警告

my_logger = components.Logger()
my_file_operator = components.File_Operater()
my_wxpusher = wxpusher.WxPusher()

PROXIES = [{"http": "http://127.0.0.1:9090", "https": "http://127.0.0.1:9090"}, {}][1]  # 代理选项，便于通过burpsuite查看流量
NOTIFY_URL = "https://www.tesla.cn/inventory/used/my?Province=CN&FleetSalesRegions=CN&arrangeby=plh&zip=&range=0"

headers_computer = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "host": "www.tesla.cn",
    "Referer": "https://www.tesla.cn/inventory/used/my?Province=CN&FleetSalesRegions=CN&arrangeby=plh&zip=&range=0",
    "Cookie": '',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Te": "trailers"
}
host = 'https://www.tesla.cn/inventory/api/v1/inventory-results?query=%7B%22query%22%3A%7B%22model%22%3A%22my%22%2C%22condition%22%3A%22used%22%2C%22options%22%3A%7B%22FleetSalesRegions%22%3A%5B%22CN%22%5D%7D%2C%22arrangeby%22%3A%22Price%22%2C%22order%22%3A%22asc%22%2C%22market%22%3A%22CN%22%2C%22language%22%3A%22zh%22%2C%22super_region%22%3A%22north%20america%22%2C%22lng%22%3A121.1007%2C%22lat%22%3A31.4482%2C%22zip%22%3A%22%22%2C%22range%22%3A0%7D%2C%22offset%22%3A0%2C%22count%22%3A50%2C%22outsideOffset%22%3A0%2C%22outsideSearch%22%3Afalse%7D '


def get_cookie():
    os.environ['PATH'] = os.environ.get('PATH') + ";D:\\python_code"  # 把驱动所在的目录加入到环境变量中，以便程序调用
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)
    browser.get(host)
    cookies_list = browser.get_cookies()
    browser.close()
    cookies_str = ''
    for cookie in cookies_list:
        cookies_str = cookies_str + cookie['name'] + '=' + cookie['value'] + ';'
    print('cookies:' + cookies_str)
    headers_computer['Cookie'] = cookies_str


def get_json(filename):
    try:
        vin_info_dic = my_file_operator.input_from_json(filename)
    except FileNotFoundError:
        my_logger.info(f"未找到文件{filename}，从本次查询中获取数据")
        """{车架号:{"门店": 门店, "售价": 售价, "里程": 里程, "出厂日期": 出厂日期, "车漆": 车漆, "轮毂": 轮毂, "内饰": 内饰, "车架号": 车架号},}"""
        vin_info_dic = {}
    return vin_info_dic


def get_response():
    try:
        return requests.get(host, headers=headers_computer, proxies=PROXIES, verify=False)  # 使用指定请求头、代理
    except:
        print("请求异常，稍后重试")
        time.sleep(10 + random.randint(0, 10))
        return get_response()


def query_car():
    response = get_response()
    try:
        response_dic = json.loads(response.content.decode('unicode-escape'))
    except:
        pass
    else:
        result_count = response_dic['total_matches_found']
        my_logger.info(f"共返回{result_count}个结果")
        if int(result_count) != 0:
            analyze(response_dic)


def analyze(response_dic):
    last_vin_info_dic = get_json('last_vin_info_dic.json')
    all_vin_info_dic = get_json('all_vin_info_dic.json')
    notify_carfind = []
    notify_pricechange = []
    notify_carsell = []
    vin_info_dic = {}

    for index, result in enumerate(response_dic['results'], 1):
        门店 = result['VrlName']
        售价 = result['Price']
        里程 = result['Odometer']
        出厂日期 = result["FactoryGatedDate"][:10]
        车漆 = result['OptionCodeSpecs']['C_OPTS']['options'][0]['name'][:3]
        轮毂 = result['OptionCodeSpecs']['C_OPTS']['options'][1]['name'][:2]
        内饰 = result['OptionCodeSpecs']['C_OPTS']['options'][2]['name'][1:2]
        型号 = result['TrimName'][:-6]
        车架号 = result['VIN']
        info_dic = {"门店": 门店, "售价": 售价, "里程": 里程, "出厂日期": 出厂日期, "车漆": 车漆, "内饰": 内饰, "轮毂": 轮毂, "型号": 型号, "车架号": 车架号}
        info_str = json.dumps(info_dic, ensure_ascii=False, indent=1)[1:-1].replace('\"', '')
        vin_info_dic[车架号] = info_dic
        if 车架号 in last_vin_info_dic.keys():  # 如果车架号在上次查询的结果中
            if last_vin_info_dic[车架号]['售价'] != 售价:  # 如果价格有变化
                my_logger.info(f"价格变化：之前售价{last_vin_info_dic[车架号]['售价']}，当前售价{售价}，调整幅度{str(int(last_vin_info_dic[车架号]['售价']) - int(售价))}，详细信息：{info_str}")
                notify_pricechange.append(f"之前售价{last_vin_info_dic[车架号]['售价']}，当前售价{售价}，调整幅度{str(int(last_vin_info_dic[车架号]['售价']) - int(售价))}，详细信息：{info_str}")

        else:  # 如果不在库中，就是新上车源
            if 车架号 in all_vin_info_dic.keys():  # 如果车架号在所有查询的结果中,说明反复上架
                my_logger.info(f"发现新车源:（出现过）{info_str}")
                notify_carfind.append(f"\n（出现过）{info_str}")
            else:  # 首次上架
                all_vin_info_dic[车架号] = info_dic
                my_logger.info(f"发现新车源:{info_str}")
                notify_carfind.append(f"{info_str}")

    # 比较出本次查询发现的已售出车辆
    for vin in last_vin_info_dic.keys():
        if vin not in vin_info_dic.keys():  # 如果上一次查询到的某辆车，这次查询没了，说明卖掉了
            sell_info_str = json.dumps(last_vin_info_dic[vin], ensure_ascii=False, indent=1)[1:-1].replace('\"', '')
            my_logger.info(f"售出车辆:{sell_info_str}")
            notify_carsell.append(f"{sell_info_str}")

    last_vin_info_dic = vin_info_dic
    my_file_operator.output_to_json(last_vin_info_dic, 'last_vin_info_dic.json')
    my_file_operator.output_to_json(all_vin_info_dic, 'all_vin_info_dic.json')

    if notify_carfind:
        my_wxpusher.send_message(summary=f"发现新车源{len(notify_carfind)}辆", content=''.join(notify_carfind), url=NOTIFY_URL)
    if notify_pricechange:
        my_wxpusher.send_message(summary="价格变化", content='\n'.join(notify_pricechange), url=NOTIFY_URL)
    if notify_carsell:
        my_wxpusher.send_message(summary=f"售出车{len(notify_carsell)}辆", content='\n'.join(notify_carsell), url=NOTIFY_URL)


if __name__ == '__main__':
    while True:
        get_cookie()
        query_car()
        time.sleep(120 + random.randint(0, 10))
