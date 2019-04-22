# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#%d,%s,%f,%d,%d,%d,%d,%s,%s,%s,%s,%s,%s,%f,%f,%f,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

#城市
class cityItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    id=scrapy.Field()
    numOfSight=scrapy.Field()
    url=scrapy.Field()
    numOfPage=scrapy.Field()

#每个景点的url
class urlOfSightItem(scrapy.Item):
    url=scrapy.Field()
    ranking=scrapy.Field()

class reviewItem(scrapy.Item):
    reviewID=scrapy.Field()
    sightID=scrapy.Field()
    userID=scrapy.Field()
    useful=scrapy.Field()
    commentTime=scrapy.Field()
    content=scrapy.Field()
    userName=scrapy.Field()
    score=scrapy.Field()
    sceneryScore=scrapy.Field()
    interestScore=scrapy.Field()
    costPerformScore=scrapy.Field()

#景点
class sightItem(scrapy.Item):
    id=scrapy.Field()
    name=scrapy.Field()
    score=scrapy.Field()
    ranking=scrapy.Field()
    numOfComment=scrapy.Field()
    wantTogo=scrapy.Field()
    beenTo=scrapy.Field()
    address=scrapy.Field()
    grade=scrapy.Field()
    tel=scrapy.Field()
    openTime=scrapy.Field()
    intro=scrapy.Field()
    traffic=scrapy.Field()
    sceneryScore=scrapy.Field()
    interestScore=scrapy.Field()
    costPerformScore=scrapy.Field()
    loveComment=scrapy.Field()
    familyComment=scrapy.Field()
    friendComment=scrapy.Field()
    businessComment=scrapy.Field()
    aloneComment=scrapy.Field()
    greatComment=scrapy.Field()
    fineComment=scrapy.Field()
    generalComment=scrapy.Field()
    badComment=scrapy.Field()
    terribleComment=scrapy.Field()
