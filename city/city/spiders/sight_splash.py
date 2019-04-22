# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from city.items import sightItem
import re
from scrapy_splash import SplashRequest
from urllib.request import Request, urlopen
import json

class citySpider(scrapy.Spider):
    # 爬虫的唯一名字，在项目中爬虫名字一定不能重复
    name='sight'
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36",
        "ROBOTSTXT_OBEY": False,
        "RETRY_TIMES": 3,
        "DOWNLOAD_TIMEOUT": 15,
        "ITEM_PIPELINES": {
            'city.pipelines.sightPipeline': 300
        },
        "DOWNLOAD_DELAY": 2,
        "SPLASH_URL" :'http://192.168.99.100:8050',
        "DUPEFILTER_CLASS": 'scrapy_splash.SplashAwareDupeFilter',
        "HTTPCACHE_STORAGE": 'scrapy_splash.SplashAwareFSCacheStorage',
        "SPIDER_MIDDLEWARES": {
            'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
        },
        "DOWNLOADER_MIDDLEWARES": {
            'scrapy_splash.SplashCookiesMiddleware': 723,
            'scrapy_splash.SplashMiddleware': 725,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
        },
        "HTTPCACHE_ENABLED": True,
        "HTTPCACHE_EXPIRATION_SECS": 0,
        "HTTPCACHE_DIR": 'httpcache'
    }

    #通过API每次获取一个ip和port
    def getProxy(self):
        url="https://api.2808proxy.com/proxy/unify/get?token=YTR8N4JY3K5CGNAKSYXZ18M6TROKZ833&amount=1&proxy_type=http&format=json&splitter=rn&expire=40"
        request = Request(url)
        html = urlopen(request)
        data = html.read()
        data_json = json.loads(data)
        ip = data_json['data'][0]['ip']
        port=data_json['data'][0]['http_port']
        return ip,port

    def start_requests(self):
        #自定义lua脚本，只调用html()方法获取网页的html代码，否则splash无法加载网页
        lua="""
        function main(splash, args)
              splash:on_request(function(request)
                request:set_proxy{
                    host = "%s",
                    port = %d,
                }
                end)
          splash:set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36")          
          splash.images_enabled=false
          splash:go(args.url)
          splash:wait(1)
          return splash:html() 
        end
        """ % ("117.191.11.80",8080)
        #不适用ip代理
        lua2="""
        function main(splash, args)
          splash:set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36")          
          splash.images_enabled=false
          splash:go(args.url)
          splash:wait(1)
          return splash:html() 
        end
        """

        file=open("D:\mycode\pycharm\\xiecheng\city\city\\每个景点的url地址.txt", "r")
        for line in file:
            list = line.split("_")
            url=list[0]
            ranking = list[1]
            yield SplashRequest(url=url, meta={'url': url, 'ranking': ranking}, callback=self.parse, endpoint='execute',
                                args={'lua_source': lua2})
        file.close()

        #url="http://www.gpsspg.com/ip/"
        #yield SplashRequest(url=url,callback=self.testParse, endpoint='execute', args={'lua_source': lua})
        #url="https://you.ctrip.com/sight/xian7/1446.html"
        #ranking="No"
        #yield SplashRequest(url=url, meta={'url': url, 'ranking': ranking}, callback=self.parse, endpoint='execute', args={'lua_source': lua2})

    #通过http://www.gpsspg.com/ip/测试是否成功换了ip
    def testParse(self,response):
        print(response)
        url=response.xpath('//div[@style="max-width:728px;font-size:14px;"]/span[@class="fcr"]/text()').extract()[0]
        print(url)

    def parse(self, response):
        url = response.request.meta['url']
        ranking=response.request.meta['ranking']
        #打印爬到的全部信息
        print(response.body)
        item=sightItem()
        #id，字符串
        item['id']=url.split("/")[-1].split(".")[0]
        #名字
        item['name']=response.xpath('//div[@class="dest_toptitle detail_tt"]/div/div[@class="f_left"]/h1/a/text()').extract()[0]
        #分数，字符串
        score=response.xpath('//ul[@class="detailtop_r_info"]/li[1]/span/b')
        if len(score)>0:
            item['score'] =score.xpath("string(./text())").extract()[0]

        #排名，字符串
        if ranking!="No":
            item['ranking']=ranking
        #评论数，字符串
        item['numOfComment']=response.xpath('//li[@href="#weiboCom1"]/h2/span/span/text()').extract()[0]
        #想去和去过，字符串
        item['wantTogo']=response.xpath('//li[@class="des_icon_want"]/p/span[2]/em/text()').extract()[0]
        item['beenTo'] = response.xpath('//em[@id="emWentValueID"]/text()').extract()[0]
        #地址
        item['address']=response.xpath('//p[@class="s_sight_addr"]/text()').extract()[0].split("：")[1]
        #等级,电话
        lis=response.xpath('//ul[@class="s_sight_in_list"]/li')
        for li in lis:
            if li.xpath("string(./span[@class=\"s_sight_classic\"]/text())").extract()[0]=="等        级：":
                item['grade']=li.xpath("string(./span[@class=\"s_sight_con\"]/text())").extract()[0].strip()
            elif li.xpath("string(./span[@class=\"s_sight_classic\"]/text())").extract()[0]=="电        话：":
                item['tel'] = li.xpath("string(./span[@class=\"s_sight_con\"]/text())").extract()[0].strip()

        #开放时间
        Opentime = response.xpath('//dl[@class="s_sight_in_list"]')
        if len(Opentime)!=0:
            item['openTime']=response.xpath('//dl[@class="s_sight_in_list"]/dd/text()').extract()[0].strip()
        #简介
        intros=response.xpath('//div[@class="toggle_l"][1]/div[@itemprop="description"]/p')
        if len(intros)!=0:
            introString=""
            #取该标签下全部文字
            for intro in intros:
                introString+=intro.xpath('string(.)').extract()[0].strip()
            item['intro']=introString

        comment=response.xpath('//dl[@class="comment_show"]/dd')
        if len(comment)>0:
            #三小项得分，字符串
            item['sceneryScore']=response.xpath('//dl[@class="comment_show"]/dd[1]/span[@class="score"]/text()').extract()[0]
            item['interestScore']=response.xpath('//dl[@class="comment_show"]/dd[2]/span[@class="score"]/text()').extract()[0]
            item['costPerformScore']=response.xpath('//dl[@class="comment_show"]/dd[3]/span[@class="score"]/text()').extract()[0]

        comment=response.xpath('//ul[@class="cate_count"]')
        if len(comment)>0:
            # 各种类型的评论条数，字符串
            item['loveComment']=response.xpath('//ul[@class="cate_count"]/li[1]/a/span[@class="ct_count"]/text()').extract()[0][0:-1]
            item['familyComment'] = response.xpath('//ul[@class="cate_count"]/li[2]/a/span[@class="ct_count"]/text()').extract()[0][0:-1]
            item['friendComment'] = response.xpath('//ul[@class="cate_count"]/li[3]/a/span[@class="ct_count"]/text()').extract()[0][0:-1]
            item['businessComment'] = response.xpath('//ul[@class="cate_count"]/li[4]/a/span[@class="ct_count"]/text()').extract()[0][0:-1]
            item['aloneComment'] = response.xpath('//ul[@class="cate_count"]/li[5]/a/span[@class="ct_count"]/text()').extract()[0][0:-1]

        #各种等级的评论条数,字符串
        item['greatComment']=response.xpath('//ul[@class="tablist"]/li[2]/a/span/text()').extract()[0][1:-1]
        item['fineComment'] = response.xpath('//ul[@class="tablist"]/li[3]/a/span/text()').extract()[0][1:-1]
        item['generalComment'] = response.xpath('//ul[@class="tablist"]/li[4]/a/span/text()').extract()[0][1:-1]
        item['badComment'] = response.xpath('//ul[@class="tablist"]/li[5]/a/span/text()').extract()[0][1:-1]
        item['terribleComment'] = response.xpath('//ul[@class="tablist"]/li[6]/a/span/text()').extract()[0][1:-1]

        #去另一个url爬取交通信息
        url=url.split(".html")[0]+"-traffic.html#jiaotong"
        yield scrapy.Request(url=url, meta={'item': item}, callback=self.parseTraffic)

    def parseTraffic(self, response):
        item = response.meta['item']
        #交通
        traffic=response.xpath('//div[@class="detailcon"]/div/text()').extract()[0].strip()
        if traffic!="":
            item['traffic']=traffic

        yield item