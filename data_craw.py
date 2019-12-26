# coding=utf-8
# coding=utf-8
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from lxml import etree

#生成页面url
def get_url1(pages):
    urls={}       #存贮链接的字典，key为页数，value为链接
    for page in range(1,int(pages)+1):
        page_url="https://sh.lianjia.com/chengjiao/pg{}/".format(page)
        #print(page_url)
        #获取详情页url,利用正则表达式匹配
        response1=requests.get(page_url)
        if response1.status_code==200:
            pattern=re.compile('<div class="info"><div class="title"><a href="(.*?)"')   #编译正则表达式，()是为了提取匹配的字符串
            response1.encoding = 'gbk'
            url=re.findall(pattern,response1.text)      #匹配所有满足正则表达式的信息
            #print(len(url))   #每页有30条房屋信息
            urls[page]=url
    #print(urls)
    return urls

#获取详情页所需的字段，beautifulsoup
def get_field(urls,pages):
    info = {"ID":[],"区域":[],"房型": [],"建筑年代":[], "面积": [],"房屋朝向":[],"装修情况":[],"总价（万）": [],"单价(元/平米)":[],
            "成交周期（天）":[],"成交日期":[],"带看次数":[]}
    for page in range(1,int(pages)+1):
        for i in urls[page]:
            response2=requests.get(i)
            if response2.status_code == 200:
                # 获取所需字段信息,beautifulsoup可以获取的
                soup=BeautifulSoup(response2.text ,'lxml')
                info["总价（万）"].append(soup.select('div.info.fr > div.price > span > i')[0].text )  #通过采用soup.select()方法，可以得到所需的内容;.表示类;运用方法 .text得到文本
                info["成交周期（天）"].append(soup.select('div.msg > span:nth-of-type(2) > label')[0].text)
                info["带看次数"].append(soup.select('div.info.fr > div.msg > span:nth-of-type(4) > label')[0].text.strip())
                info["单价(元/平米)"].append(soup.select(' div.info.fr > div.price > b')[0].text)
                info["成交日期"].append(soup.select(' div.house-title > div > span')[0].text.replace('成交',''))
                #获取所需字段信息,xpath提取
                d=etree.HTML(response2.text)
                info["房型"].append(d.xpath('// *[ @ id = "introduction"] / div[1] / div[1] / div[2] / ul / li[1] / text()')[0].strip())
                info["面积"].append(d.xpath('//*[@id="introduction"]/div[1]/div[1]/div[2]/ul/li[3]/text()')[0].strip())
                info["建筑年代"].append(d.xpath('//*[@id="introduction"]/div[1]/div[1]/div[2]/ul/li[8]/text()')[0])
                info["房屋朝向"].append(d.xpath('//*[@id="introduction"]/div[1]/div[1]/div[2]/ul/li[7]/text()')[0].strip())
                info["装修情况"].append(d.xpath('// *[ @ id = "introduction"] / div[1] / div[1] / div[2] / ul / li[9] / text()')[0].strip())
                info["ID"].append(d.xpath('//*[@id="introduction"]/div[1]/div[2]/div[2]/ul/li[1]/text()')[0].strip())
                info["区域"].append(d.xpath('/html/body/section[2]/div[2]/div/div/div[1]/a[1]/text()')[0])

    #将房屋信息读取到dataframe
    df=pd.DataFrame(info)
    pd.set_option('display.max_columns', None)          #显示所有列
    print(df)
    return df
#将数据导出保存为csv
def output_csv(df):
    df.to_csv('lianjia_ershoufang.csv', sep=',', index=False, header=False)

if __name__ == "__main__":
    pages=input("please input pages:")
    urls=get_url1(pages)
    df=get_field(urls, pages)
    output_csv(df)



