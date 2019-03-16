# -*- coding: utf-8 -*-

import json
import logging
import random
import re
import time
import sys

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.exceptions import RequestException

import bei_ke_db

ua = UserAgent(use_cache_server=False)
# 日志配置
handler = logging.FileHandler(filename='bei_ke_used.log', encoding='utf-8')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('%(asctime)s -|- %(levelname)s -|- %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.addHandler(stream_handler)

# 日志示例
# logger.info('This is a log info')
# logger.debug('Debugging')
# logger.warning('Warning exists')

# 正则
re_build_year = re.compile('(\d{4})年建')
re_house_type = re.compile('(\d+)室(\d+)厅(\d+)卫')
re_floor_position = re.compile('(.+) \(共(\d+)层\)')
re_houser_area = re.compile('([\d\.]+)㎡')
re_property_right = re.compile('(\d+)年')
re_community_number = re.compile('.*/(\d+)/')
re_listing_time = re.compile('(\d+)年(\d+)月(\d+)日')

host = 'https://zj.ke.com'


def prepare(host):
    ready_url = host + '/ershoufang/'
    ready_response = requests.get(
        ready_url, timeout=7
    )
    if ready_response.status_code == 200:
        try:
            ready_soup = BeautifulSoup(
                ready_response.text, 'html5lib')
            zone_option_dom = ready_soup.find('div', class_="m-filter").find(
                'div', class_="position").find('div', attrs={"data-role": "ershoufang"}).find_all('a')
            zone_options = {}
            for a in zone_option_dom:
                zone_options[a.string] = a['href']
            for (name, href) in zone_options.items():
                print('当前处理：' + name)
                deal_house_list(host, name, href)

        except Exception:
            logger.exception('Ready解析失败')
    else:
        logger.warning('Ready请求失败 %s', ready_response.status_code)
        time.sleep(3)
        prepare(host)


def print_schedule(curr_value, total_value):
    if total_value == 0:
        total_value = 1
    print('处理第 ' + str(curr_value) + ' 页中 - ' +
          "{:.2f}".format(1/total_value*100) + " %")


def deal_house_list(host, zone_name, zone_href):
    headers = {
        'User-Agent':  ua.random,
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    try:
        url = host + zone_href
        # 请求各区第一页列表
        response = requests.get(
            url, headers=headers, timeout=7)
        if response.status_code == 200:
            print(zone_name + '列表首页请求成功')
            soup = BeautifulSoup(response.text, 'html5lib')

            # 分析页码
            page_box = soup.find('div', class_="house-lst-page-box")
            max_page = 0
            if page_box:
                page_data = page_box['page-data']
                max_page = int(json.loads(page_data)['totalPage'])

            print('共 ' + str(max_page) + ' 页')
            # 处理第一页
            print_schedule(1, max_page)
            deal_house_detail(soup)

            # 处理其他页
            if max_page > 1:
                for page_num in range(2, max_page + 1):
                    print_schedule(page_num, max_page)
                    time.sleep(random.randint(3, 7))
                    url_other_page = host + zone_href + '/' + 'pg' + page_num + '/'
                    response_other_page = requests.get(
                        url_other_page, headers=headers, timeout=7)
                    if response_other_page.status_code == 200:
                        soup_other_page = BeautifulSoup(
                            response_other_page.text, 'html5lib')
                        deal_house_detail(soup_other_page)
                    else:
                        logger.warning(
                            '列表请求失败 地址：%s， 状态码：%s', url_other_page, response_other_page.status_code)
        else:
            logger.warning('列表首页请求失败 地址：%s， 状态码：%s', url, response.status_code)
    except RequestException:
        logger.exception('发生错误')


def deal_house_detail(soup):
    headers = {
        'User-Agent':  ua.random,
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    sell_list = soup.select('li.clear')
    sell_num = len(sell_list)
    if sell_num > 0:
        print('共 ' + str(sell_num) + ' 条数据')
        for (i, li) in enumerate(sell_list):
            try:
                time.sleep(3)
                detail_href = li.find('a')['href']  # 详情页面链接  s
                print('访问详情页面：' + detail_href + ' - ' +
                      str("{:.2f}".format(i/sell_num*100)) + ' %')
                response_detail = requests.get(
                    detail_href, headers=headers, timeout=7)
                if response_detail.status_code == 200:
                    soup_detail = BeautifulSoup(
                        response_detail.text, 'html5lib')
                    describe = soup_detail.find(
                        'h1', class_="main").string.strip()  # 标题 - 描述  s

                    img_house_layout = None   # 户型图  s
                    img_house_other = []   # 房源照片  s
                    img_dom = soup_detail.find('ul', class_="smallpic")
                    if img_dom:
                        for li in img_dom.select('li'):
                            if li['data-desc'] == '户型图':
                                img_house_layout = json.dumps(li['data-pic'])
                            else:
                                img_house_other.append(li['data-pic'])
                    else:
                        print('当前房源没有图片')
                    img_house_other = json.dumps(img_house_other)

                    price_dom = soup_detail.find('div', class_="price")
                    total_price_value = int(price_dom.find(
                        'span', class_="total").string)  # 总价  s
                    total_price_unit = price_dom.find(
                        'span', class_="unit").span.string  # 总价单位  s
                    unit_price_value = float(price_dom.find(
                        'span', class_="unitPriceValue").string)  # 均价  s
                    unit_price_unit = price_dom.find(
                        'div', class_="unitPrice").i.string  # 均价单位  s

                    community_dom = soup_detail.find(
                        'div', class_="aroundInfo")
                    community_info_dom = community_dom.find(
                        'div', class_="communityName").find('a', class_="info")
                    community_href = community_info_dom['href']   # 小区链接  s
                    community_number = re.match(
                        re_community_number, community_href).groups()[0]   # 小区编号  s
                    community_area_info_dom = community_dom.find(
                        'div', class_="areaName").find('span', class_="info")
                    # 小区所在区  s
                    community_zone = community_area_info_dom.contents[0].string
                    # 小区所在商圈  s
                    community_business_zone = community_area_info_dom.contents[1].string

                    house_number_dom = community_dom.find(
                        'div', class_="houseRecord").find('span', class_="info")
                    house_number_dom.span.extract()
                    house_number = house_number_dom.get_text().strip()   # 房子的贝壳编码  s

                    house_info_dom = soup_detail.find(
                        'div', class_="houseInfo")
                    build_year_string = house_info_dom.find(
                        'div', class_="area").find('div', class_="subInfo").string
                    build_year_re = re.match(re_build_year, build_year_string)
                    build_year = None  # 建造年代  s
                    if build_year_re:
                        build_year = int(build_year_re.groups(1)[0])

                    intro_content_dom = soup_detail.find(
                        'div', class_="introContent")

                    base_intro = intro_content_dom.find(
                        'div', class_="base").find_all('li')
                    house_type_room = None  # 室  s
                    house_type_living = None  # 厅  s
                    house_type_bathroom = None  # 卫  s
                    floor_position = None   # 楼层位置  s
                    floor_sum = None   # 总楼层  s
                    house_area = None  # 总面积  s
                    family_structure = None   # 户型结构  s
                    building_types = None   # 建筑类型  s
                    house_toward = None   # 房屋朝向  s
                    building_structure = None   # 建筑结构  s
                    repair_situation = None   # 装修情况  s
                    ladder_household_proportion = None   # 梯户比例  s
                    equipped_elevator = None   # 配备电梯  s
                    villa_type = None   # 别墅类型  s
                    property_right_years = None   # 产权年限  s
                    for li in base_intro:
                        label = li.contents[0].string
                        content = li.contents[1].string
                        if content == '暂无数据':
                            continue
                        if label == '房屋户型':
                            house_type_re = re.match(
                                re_house_type, content).groups()
                            house_type_room = int(house_type_re[0])
                            house_type_living = int(house_type_re[1])
                            house_type_bathroom = int(house_type_re[2])
                        elif label == '所在楼层':
                            floor = re.match(
                                re_floor_position, content).groups()
                            floor_position = floor[0]
                            floor_sum = int(floor[1])
                        elif label == '建筑面积':
                            area = re.match(re_houser_area, content).groups()
                            house_area = float(area[0])
                        elif label == '户型结构':
                            family_structure = content
                        elif label == '建筑类型':
                            building_types = content
                        elif label == '房屋朝向':
                            house_toward = content
                        elif label == '建筑结构':
                            building_structure = content
                        elif label == '装修情况':
                            repair_situation = content
                        elif label == '梯户比例':
                            ladder_household_proportion = content
                        elif label == '配备电梯':
                            equipped_elevator = content
                        elif label == '别墅类型':
                            villa_type = content
                        elif label == '产权年限':
                            property_right_re = re.match(
                                re_property_right, content).groups()
                            property_right_years = int(property_right_re[0])
                        else:
                            logger.info(
                                '卍卍卍卍卍卍卍卍 【基本信息】没有写入的属性：%s 卐卐卐卐卐卐卐卐', label)

                    transaction_intro = intro_content_dom.find(
                        'div', class_="transaction").find_all('li')
                    listing_time = None   # 挂牌时间  s
                    trading_authority = None   # 交易权属  s
                    last_transaction = None   # 上次交易  s
                    housing_use = None   # 房屋用途  s
                    housing_life = None   # 房屋年限  s
                    property_ownership = None   # 产权所属  s
                    mortgage_information = None   # 抵押信息  s
                    housing_spare_parts = None   # 房本备件  s
                    for li in transaction_intro:
                        label = li.contents[0].string
                        content = li.contents[1].string
                        if content == '暂无数据':
                            continue
                        if label == '挂牌时间':
                            listing_time_re = re.match(
                                re_listing_time, content).groups()
                            listing_time = listing_time_re[0] + '-' + \
                                listing_time_re[1] + '-' + listing_time_re[2]
                        elif label == '交易权属':
                            trading_authority = content
                        elif label == '上次交易':
                            last_transaction = content
                        elif label == '房屋用途':
                            housing_use = content
                        elif label == '房屋年限':
                            housing_life = content
                        elif label == '产权所属':
                            property_ownership = content
                        elif label == '抵押信息':
                            mortgage_information = content
                        elif label == '房本备件':
                            housing_spare_parts = content
                        else:
                            logger.info(
                                '卍卍卍卍卍卍卍卍 【交易信息】 没有写入的属性：%s 卐卐卐卐卐卐卐卐', label)

                    bei_ke_db.write_used_db(house_number, detail_href, describe,
                                            total_price_value, total_price_unit, unit_price_value, unit_price_unit,
                                            community_href, community_number, community_zone, community_business_zone,
                                            build_year, house_type_room, house_type_living, house_type_bathroom,
                                            floor_position, floor_sum, house_area, family_structure, building_types,
                                            house_toward, building_structure, repair_situation, ladder_household_proportion,
                                            equipped_elevator, villa_type, property_right_years, listing_time, trading_authority,
                                            last_transaction, housing_use, housing_life, property_ownership, mortgage_information,
                                            housing_spare_parts, img_house_layout, img_house_other,)
                else:
                    logger.info('详情页请求失败 地址：%s， 状态码：%s', detail_href,
                                response_detail.status_code)
            except Exception:
                logger.exception('详情页解析错误：%s', detail_href)
    else:
        print('当前页没有数据')


def main():
    prepare(host)


if __name__ == '__main__':
    main()
