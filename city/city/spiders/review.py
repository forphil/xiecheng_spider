import scrapy
from city.items import reviewItem
import re
import urllib
from bs4 import BeautifulSoup
import time
#5900
class reviewSpider(scrapy.Spider):
    # 爬虫的唯一名字，在项目中爬虫名字一定不能重复
    name='review'

    custom_settings = {
        "USER_AGENT" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36",
        "ITEM_PIPELINES": {
            'city.pipelines.reviewPipeline': 300
        },
        "ROBOTSTXT_OBEY": False,
        "RETRY_TIMES": 3,
        "DOWNLOAD_TIMEOUT": 10,
        "DOWNLOAD_DELAY": 1
    }

    def start_requests(self):
        file=open("D:\mycode\pycharm\\xiecheng\city\city\每个景点的url地址.txt", "r")
        for line in file:
            list = line.split("_")
            url=list[0]
            yield scrapy.Request(url=url, meta={'url': url},callback=self.parse)
        file.close()
        #url="https://you.ctrip.com/sight/macau39/49198.html"
        #yield scrapy.Request(url=url, meta={'url': url},callback=self.parse)

    def parse(self, response):
        #print(response.body)
        numOfReview=0
        url = response.request.meta['url']
        reviews=response.xpath('//div[@class="comment_ctrip"]/div[@class="comment_single"]')
        #如果有评论
        if len(reviews)>0:
            #处理首页的每个评论
            for review in reviews:
                numOfReview+=1
                item=reviewItem()
                partUrl = url.split('/')[-2]
                districtId = re.findall(r"\d+", partUrl)[0]
                item['sightID']=url.split('/')[-1].split('.')[0]
                item['reviewID']=url.split('/')[-1].split('.')[0]+"_"+str(numOfReview)
                item['content']=review.xpath("string(./ul/li[@class=\"main_con\"]/span/text())").extract()[0]
                score=review.xpath("string(.//span[@class=\"starlist\"]/span/@style)").extract()[0]
                if(score=="width:20%;"):
                    item['score']=1
                elif(score=="width:40%;"):
                    item['score'] = 2
                elif (score == "width:60%;"):
                    item['score'] = 3
                elif (score == "width:80%;"):
                    item['score'] = 4
                elif (score == "width:100%;"):
                    item['score'] = 5
                item['userName']=review.xpath("string(.//span[@class=\"ellipsis\"]/a/@title)").extract()[0]
                item['userID']=review.xpath("string(.//span[@class=\"ellipsis\"]/a/@href)").extract()[0].split('/')[-1]
                item['useful']=review.xpath("string(.//span[@class=\"useful\"]/em/text())").extract()[0]
                item['commentTime']=review.xpath("string(.//span[@class=\"time_line\"]/em/text())").extract()[0]
                threeScore=review.xpath("string(.//span[@class=\"sblockline\"]/text())").extract()[0]
                #如果三项小分存在
                if(threeScore!=''):
                    item['sceneryScore']=re.findall(r"\d+", threeScore)[0]
                    item['interestScore'] =re.findall(r"\d+", threeScore)[1]
                    item['costPerformScore'] =re.findall(r"\d+", threeScore)[2]
                yield item
            totalPage = response.xpath(".//b[@class='numpage']")
            #如果有翻页
            if len(totalPage)>0:
                #获取html请求的参数
                totalPage=response.xpath(".//b[@class='numpage']/text()").extract()[0]
                poiID = response.xpath(".//span[@class='c_tipswrap']/a[@class='b_orange_m']/@href").extract()[0]
                poiID = re.findall(r"\d+", poiID)[0]
                districtEName = re.findall(r"[^\d]", partUrl)[0].capitalize()
                resourceId=url.split('/')[-1].split('.')[0]
                #有多少页就发多少个请求
                for page in range(1,int(totalPage)):
                    time.sleep(0.5)
                    pagenow=page+1
                    param = {
                        'poiID': int(poiID),
                        'districtId': int(districtId),
                        'districtEName': districtEName,
                        'pagenow': pagenow,
                        'order': 3.0,
                        'star': 0.0,
                        'tourist': 0.0,
                        'resourceId': int(resourceId),
                        'resourcetype': 2
                    }
                    #发送html请求
                    param = urllib.parse.urlencode(param)
                    param = param.encode('utf-8')
                    post_url = "https://you.ctrip.com/destinationsite/TTDSecond/SharedView/AsynCommentView"
                    new_url = urllib.request.Request(post_url, param)
                    #解析返回的内容
                    response = urllib.request.urlopen(new_url)
                    content = response.read()
                    soup = BeautifulSoup(content, 'html.parser')

                    reviews=soup.find('div',class_="comment_ctrip").findAll('div',class_="comment_single")
                    #对返回的内容，依次处理每个评论
                    for review in reviews:
                        numOfReview += 1
                        item=reviewItem()
                        content=review.find('span',class_="heightbox")
                        item['sightID'] = url.split('/')[-1].split('.')[0]
                        item['reviewID'] = url.split('/')[-1].split('.')[0] + "_" + str(numOfReview)
                        if content!=None:
                            item['content'] =content.get_text()
                        score=review.find('span',class_="starlist").find('span').get('style')
                        if score!=None:
                            if (score == "width:20%;"):
                                item['score'] = 1
                            elif (score == "width:40%;"):
                                item['score'] = 2
                            elif (score == "width:60%;"):
                                item['score'] = 3
                            elif (score == "width:80%;"):
                                item['score'] = 4
                            elif (score == "width:100%;"):
                                item['score'] = 5
                        item['userName']=review.find('a',itemprop="author").get('title')
                        threeScore=review.find('span',class_="sblockline")
                        item['userID'] = review.find('span',class_="ellipsis").find('a').get('href').split('/')[-1]
                        item['useful'] = review.find('span',class_="useful").find('em').get_text()
                        item['commentTime'] = review.find('span',class_="time_line").find('em').get_text()
                        if threeScore!=None:
                            threeScore=threeScore.get_text()
                            item['sceneryScore'] = re.findall(r"\d+", threeScore)[0]
                            item['interestScore'] = re.findall(r"\d+", threeScore)[1]
                            item['costPerformScore'] = re.findall(r"\d+", threeScore)[2]
                        yield item






