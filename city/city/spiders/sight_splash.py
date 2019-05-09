# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from city.items import sightItem
import re
from scrapy_splash import SplashRequest
from urllib.request import Request, urlopen
import json

#计数器,用于记录每个IP访问了多少个携程网
def foo (i, L=[]):
  if len(L)==0:
    L.append(0)
  L[0]+=i
  return L[0]

class citySpider(scrapy.Spider):
    # 爬虫的唯一名字，在项目中爬虫名字一定不能重复
    name='sight'
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36",
        "ROBOTSTXT_OBEY": False,
        "RETRY_TIMES": 1,
        "DOWNLOAD_TIMEOUT": 15,
        "ITEM_PIPELINES": {
            'city.pipelines.sightPipeline': 300
        },
        "DOWNLOAD_DELAY": 10,
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
            'city.middlewares.MyUserAgentMiddleware': 400
        },
        "HTTPCACHE_ENABLED": True,
        "HTTPCACHE_EXPIRATION_SECS": 0,
        "HTTPCACHE_DIR": 'httpcache',

        "MY_USER_AGENT" :[
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393"
        ]
    }

    #调用牛魔IP的API，获得新的IP和port。可以保存到文件里，一个IP多次使用，节省IP使用量
    def getIP(self):
        url = "http://api.http.niumoyun.com/v1/http/ip/get?p_id=228&s_id=2&u=AmFVNwE5B2FSYwAuB0kHOA8gVWldZQsaBVJUUFNV&number=1&port=1&type=1&map=1&pro=0&city=0&pb=1&mr=2&cs=1"
        request = Request(url)
        html = urlopen(request)
        data = html.read()
        data_json = json.loads(data)
        ip = data_json['data'][0]['ip']
        port = data_json['data'][0]['port']
        print("新ip和port："+ip+" "+str(port))
        file = open("D:\mycode\pycharm\\xiecheng\city\city\spiders\ip和port", "w")
        file.write(ip + "_" + str(port) + '/n')


    #每个爬虫请求都调用此方法，获取IP和port
    def getProxy(self):
        #每次执行，计数器加1，也就是记录该ip访问了多少次网页
        print("ip计数："+str(foo(1)))
        #每爬20次，就更换一个IP，这个参数课手动调整，只要保证IP不被封就可以
        if foo(0) % 20 == 0:
            #调用方法，通过API新获得一个IP
            self.getIP()
        file=open("D:\mycode\pycharm\\xiecheng\city\city\spiders\ip和port","r")
        line=file.readline()
        ip=line.split('_')[0]
        port=line.split('_')[1].split('/n')[0]
        return ip,int(port)


    def start_requests(self):

        #不用ip代理的脚本
        lua2="""
        function main(splash, args)
          splash:set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36")          
          splash.images_enabled=false
          splash:go(args.url)
          splash:wait(1)
          return splash:html() 
        end
        """

        file=open("D:\mycode\pycharm\\xiecheng\city\city\每个景点的url地址.txt", "r")
        for line in file:
            #获取本次请求要使用的IP和port
            ip, port = self.getProxy()
            print("当前ip："+ip+" "+str(port))
            # 自定义lua脚本，只调用html()方法获取网页的html代码，否则splash无法加载网页。同时使用ip代理
            lua = """
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
            """ % (ip, port)
            list = line.split("_")
            url=list[0]
            ranking = list[1]
            yield SplashRequest(url=url, meta={'url': url, 'ranking': ranking}, callback=self.parse, endpoint='execute',
                                args={'lua_source': lua})

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
        #try:
        item['name']=response.xpath('//div[@class="dest_toptitle detail_tt"]/div/div[@class="f_left"]/h1/a/text()').extract()[0]
        # except:
        #     self.getIP()
        #     return
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