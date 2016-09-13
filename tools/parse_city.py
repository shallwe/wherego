#coding: utf-8
import json
import os
import random


def parse_cities(province):
    data = json.load(open("data/{}.json".format(province)))
    ret = {}
    for city in data['features']:
        name = city['properties']['name']
        if '市' == name[-1]:
            name = name[:-1]
        ret[name] = city['properties']['cp']
    return ret

def main():
    data = {}
    province_name_map = {
        "anhui": "安徽",
        "fujian": "福建",
        "gansu": "甘肃",
        "guangdong": "广东",
        "guangxi": "广西",
        "guizhou": "贵州",
        "hainan": "海南",
        "hebei": "河北",
        "heilongjiang": "黑龙江",
        "henan": "河南",
        "hubei": "湖北",
        "hunan": "湖南",
        "jiangsu": "江苏",
        "jiangxi": "江西",
        "jilin": "吉林",
        "liaoning": "辽宁",
        "neimenggu": "内蒙古",
        "ningxia": "宁夏",
        "qinghai": "青海",
        "shandong": "山东",
        "shanxi": "山西",
        "shanxi1": "陕西",
        "sichuan": "四川",
        "xinjiang": "新疆",
        "xizang": "西藏",
        "yunnan": "云南",
        "zhejiang": "浙江",
    }

    for f in os.listdir('data'):
        province = f[:-5]
        data[province_name_map[province]] = parse_cities(province)

    extra = {
        '上海': [
            121.472644,
            31.231706
        ],

        '北京': [
            116.405285,
            39.904989
        ],

        '天津': [
            117.190182,
            39.125596
        ],

        '重庆': [
            106.504962,
            29.533155
        ],

        '香港': [
            114.173355,
            22.320048
        ],

        '澳门': [
            113.54909,
            22.198951
        ]
    }
    for city, pos in extra.items():
        data.update({city: {city: pos}})
    data.update({
        '台湾': {
            "台北": [121.5, 25.05],
            "高雄": [120.37, 22.64],
            "基隆": [121.73, 25.14],
            "台中": [120.67, 24.15],
            "台南": [120.19, 22.98],
            "宜兰": [121.75, 24.75],
            "桃园": [121.3, 25],
            "新竹": [120.96, 24.81],
        }
    })
    json.dump(data, open('china.json', 'w'))
    from pprint import pprint
    pprint(data)
    # print(len(data))
    province = random.choice(list(data.keys()))
    city = random.choice(list(data[province]))
    print(province, city)

if __name__ == '__main__':
    main()