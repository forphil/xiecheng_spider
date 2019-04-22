# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from city.items import urlOfSightItem
import re

class citySpider(scrapy.Spider):
    # 爬虫的唯一名字，在项目中爬虫名字一定不能重复
    name='urlOfSight'

    #管道文件中使用CityPipeline类
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "ITEM_PIPELINES": {
            'city.pipelines.urlOfSightPipeline': 300
        },
        "ROBOTSTXT_OBEY": False,
        "RETRY_TIMES": 3,
        "DOWNLOAD_TIMEOUT": 3,
        "DOWNLOAD_DELAY": 1.2
    }

    def start_requests(self):
        file=open(".\城市景点页的url地址.txt", "r")
        for line in file:
            url=line.split("_")[0]
            totalPage=line.split("_")[1]
            yield scrapy.Request(url=url,meta={'totalPage': totalPage,'currentUrl':url}, callback=self.parse)
        file.close()

    def parse(self, response):
        #该城市共有多少页景点
        totalPage = response.request.meta['totalPage']
        #首页的地址
        currentUrl=response.request.meta['currentUrl']
        #当前页的所有景点信息节点
        sights=response.xpath('//div[@class="list_mod2"]')
        for sight in sights:
            urlOfSight="https://you.ctrip.com"+sight.xpath("string(./div[@class=\"leftimg\"]/a/@href)").extract()[0]
            #print(sight.xpath("string(./div[@class=\"leftimg\"]/a)"))
            item=urlOfSightItem()
            #该景点完整url
            item['url']=urlOfSight
            #该景点的排名
            #ranking=sight.xpath("string(./div[@class=\"rdetailbox\"]/dl/dt/s[@class=\"g_background\"]/text())").extract()[0]
            ranking=sight.xpath("string(./div[@class=\"rdetailbox\"]/dl/dt/s/text())").extract()[0]
            #如果没有排名，就填“无”
            if ranking!="":
                item['ranking']=re.findall(r"\d+", ranking)[0]
            else:
                item['ranking']="No"
            yield item
        #当前在第几页
        currentPage=response.xpath('//div[@class="pager_v1"]/a[@class="current"]/text()').extract()[0]
        #如果没到最后一页
        if int(currentPage)<int(totalPage):
            #如果当前页是第一页
            if int(currentPage)==1:
                nextUrl=currentUrl.split(".html")[0]+"/s0-p%d.html"%(int(currentPage)+1)
                yield scrapy.Request(url=nextUrl, meta={'totalPage': totalPage, 'currentUrl': nextUrl}, callback=self.parse)
            #如果当前页不是第一页
            else:
                nextUrl=currentUrl.split("-")[0]+"-p%d.html"%(int(currentPage)+1)
                yield scrapy.Request(url=nextUrl, meta={'totalPage': totalPage, 'currentUrl': nextUrl},callback=self.parse)
