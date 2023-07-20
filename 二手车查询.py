"""
由于使用https，所以需要以管理员身份运行
"""
import random
import time
import requests
import json
from share_package import components, wxpusher
from requests.packages import urllib3

urllib3.disable_warnings()  # 关闭https的ssl证书警告

my_logger = components.Logger()
my_file_operator = components.File_Operater()
my_wxpusher = wxpusher.WxPusher()

PROXIES = [{"http": "http://127.0.0.1:9090", "https": "http://127.0.0.1:9090"}, {}][1]  # 代理选项，便于通过burpsuite查看流量
NOTIFY_URL = "https://www.tesla.cn/inventory/used/my?Province=CN&FleetSalesRegions=CN&arrangeby=plh&zip=&range=0"

headers_computer = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "*/*",
    "host": "www.tesla.cn",
    "Referer": "https://www.tesla.cn/inventory/used/my?Province=CN&FleetSalesRegions=CN&arrangeby=plh&zip=&range=0",
    "Cookie": 'gdp_user_id=gioenc-7300165g%2C494g%2C55da%2Ccad1%2Cdcaebc0b247d; b0e25bc027704bfe_gdp_sequence_ids=%7B%22globalKey%22%3A31%2C%22VISIT%22%3A2%2C%22PAGE%22%3A4%2C%22CUSTOM%22%3A5%2C%22VIEW_CLICK%22%3A23%7D; RT="z=1&dm=www.tesla.cn&si=5edda009-420c-4771-abb7-c3977db8f8a7&ss=ljdvtw6t&sl=0&tt=0"; coin_auth=38cbb71b2bc836f1ac066e5a5b7a5ac4; ip_info={"ip":"218.4.161.210","location":{"latitude":31.4482,"longitude":121.1007},"region":{"longName":"Jiangsu","regionCode":"JS"},"city":"Taicang","country":"China","countryCode":"CN","postalCode":""}; AKA_A2=A; ak_bmsc=E0F075543C3F0C8814B5251C660FBA1B~000000000000000000000000000000~YAAQJuBb2urBgeWIAQAAEJBz+xRiNgLElIGI5qKci3ih2fp5ppRkvAY49J1MonKcnopx3LLPIDeeUKUDlJR/tY7uZXluoRQiCCvon/9S9RYiqjwAX7WGNU9wYywXQLrNWcFo+gIBruch/H48+RmZSK4fjTGpjZXoHL+j616RWlKQJtisL0aRUgOhin3k9m2BDsZo1yAfkvpVVRUQUliiGMVtLoOWwKOvu5AZWVVDNIXyZCQhvLNRKh7xQZULZvPEbR+5kqwNqcgWbA0X4xx3OabFF3BKt+FSK/TH9RieAfgT5SwTkQ+N/QCag2rRRdhT0Nwb64vphpK5f6X/B2dabz7S91F/jSIqZW0gV7bfhRPE0d9D2l8VIBiT0UwKW5zCGhC/LIanBLNrkBgIPPUDLrWE75gdJTfWm+05VV8kS/XlDIYAqsuSGALDykBc0Ffc6qfgff4lQwlBx5ZgHW4h85SZd9nmevP9GXiacQ==; bm_sv=C33DE4CB6F68831F0705CF0A245723FE~YAAQJuBb2vTBgeWIAQAAUJFz+xQJp3OFH7YTyE36ROf6Mfv6H6lkMnJaLnP+qaCqT49r30zHhrWh+GLkpUN0+yURV8qxNJFlNalJox2Pz4nGhzj9i6D7Qpm38GI7cZVV2rHKZrdUZuG1jSj+OrS3gIiCeDFPZsjIY36yPdXnSXenWj7g0BRXgypB8ZNbbIWrL96dKD8Z8lVj8RikLym60aEgh9MnHK+dC67BKbLz+2tCb8LTaYlVyaBkgw+e2g==~1',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Te": "trailers"
}
host = 'https://www.tesla.cn/inventory/api/v1/inventory-results?query=%7B%22query%22%3A%7B%22model%22%3A%22my%22%2C%22condition%22%3A%22used%22%2C%22options%22%3A%7B%22FleetSalesRegions%22%3A%5B%22CN%22%5D%7D%2C%22arrangeby%22%3A%22Price%22%2C%22order%22%3A%22asc%22%2C%22market%22%3A%22CN%22%2C%22language%22%3A%22zh%22%2C%22super_region%22%3A%22north%20america%22%2C%22lng%22%3A121.1007%2C%22lat%22%3A31.4482%2C%22zip%22%3A%22%22%2C%22range%22%3A0%7D%2C%22offset%22%3A0%2C%22count%22%3A50%2C%22outsideOffset%22%3A0%2C%22outsideSearch%22%3Afalse%7D '


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
    last_vin_info_dic = get_json('last_vin_info_dic.json')
    all_vin_info_dic = get_json('all_vin_info_dic.json')
    response = get_response()
    response_dic = json.loads(response.content.decode('unicode-escape'))
    my_logger.info(f"共返回{response_dic['total_matches_found']}个结果")
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
                my_logger.info(f"价格变化：之前售价{last_vin_info_dic[车架号]['售价']}，当前售价{售价}，调整幅度{str(int(last_vin_info_dic[车架号]['售价'])-int(售价))}，详细信息：{info_str}")
                notify_pricechange.append(f"之前售价{last_vin_info_dic[车架号]['售价']}，当前售价{售价}，调整幅度{str(int(last_vin_info_dic[车架号]['售价'])-int(售价))}，详细信息：{info_str}")

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
        query_car()
        time.sleep(60 + random.randint(0, 10))
