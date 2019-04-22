# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from city.items import cityItem
import re

class citySpider(scrapy.Spider):
    # 爬虫的唯一名字，在项目中爬虫名字一定不能重复
    name='city'

    #管道文件中使用CityPipeline类
    custom_settings = {
        "USER_AGENT" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "ITEM_PIPELINES": {
            'city.pipelines.CityPipeline': 300
        },
        "ROBOTSTXT_OBEY": False,
        "RETRY_TIMES": 3,
        "DOWNLOAD_TIMEOUT": 10,
        "DOWNLOAD_DELAY": 1
    }

    def start_requests(self):
        line="https://you.ctrip.com/place/"
        yield scrapy.Request(url=line,callback=self.parse)

    def parse(self, response):
        response = Selector(response)

        #国内有几个地区
        numOfRegions=len(response.xpath('//dl[@class="item itempl-60"][2]/dd[@class="panel-con"]/ul/li'))
        #对每个地区，执行下面的操作
        for i in range(numOfRegions):
            line="//dl[@class=\"item itempl-60\"][2]/dd[@class=\"panel-con\"]/ul/li["+str(i+1)+"]/a"
            #找出各个地区下面的全部城市
            citys=response.xpath(line)
            for city in citys:
                #新建一个city对象
                item = cityItem()
                # 用该城市网址中的数字作为该城市的id
                # 用正则表达式找出网址中的数字，结果是一个列表，用[0]取第一个元素
                partUrl = city.xpath("string(./@href)").extract()[0]
                item['id'] = re.findall(r"\d+", partUrl)[0]
                item['name'] = city.xpath("string(./text())").extract()[0]
                #拼出该城市景点页的完整url
                partUrl=partUrl.split("/")[-1]
                url="https://you.ctrip.com/sight/"+partUrl
                item['url']=url
                #为了获得该城市的景点数量，爬取该城市景点页的信息
                #把当前item当做参数传给下一个parse
                yield scrapy.Request(url=url, meta={'item': item}, callback=self.parseCitySight)

    def parseCitySight(self,response):
        #不用加response = Selector(response)了
        #获取item参数
        item = response.meta['item']
        #爬取景点数量
        try:
            numOfSight=response.xpath('//div[@class="ttd_pager cf"]/p/text()').extract()[0]
            #该城市的景点有多少页
            item['numOfPage']=response.xpath('//div[@class="pager_v1"]/span/b/text()').extract()[0]
        #如果是台湾的页面，因为不符合规范，跳过
        except IndexError:
            return
        item['numOfSight']=numOfSight.split(" ")[-1][0:-1]
        yield item




