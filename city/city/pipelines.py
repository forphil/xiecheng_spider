# -*- coding: utf-8 -*-
import pymysql
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class CityPipeline(object):
    #sql语句格式
    cityInsert = '''insert into city(id,name,numOfSight) values \
        ('{id}','{name}','{numOfSight}')'''

    #开始时自动执行此函数
    def open_spider(self, spider):
        self.connect = pymysql.connect(host='192.168.99.1',
                                       port=3306,
                                       db='xiecheng',
                                       user='root',
                                       passwd='123456',
                                       charset='utf8',
                                       use_unicode=True)
        self.cursor = self.connect.cursor()
        self.connect.autocommit(True)
        #每个城市的景点页的url，和景点的页数 写入txt文件
        self.file = open('..\城市景点页的url地址.txt', 'a', encoding='utf-8')

    def process_item(self, item, spider):
        #向mysql插入数据
        sqlinsert = self.cityInsert.format(
            id=int(item['id']),
            name=item['name'],
            numOfSight=int(item['numOfSight'])
        )
        self.cursor.execute(sqlinsert)

        #记录每个城市的景点页的url，和景点的页数
        line=item['url']+"_"+item['numOfPage']+ "\n"
        self.file.write(line)

        return item

    #结束时自动执行此函数
    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()
        self.file.close()

class reviewPipeline(object):
    #sql语句格式

    #开始时自动执行此函数
    def open_spider(self, spider):
        self.connect = pymysql.connect(host='192.168.99.1',
                                       port=3306,
                                       db='xiecheng',
                                       user='root',
                                       passwd='123456',
                                       charset='utf8',
                                       use_unicode=True)
        self.cursor = self.connect.cursor()
        self.connect.autocommit(True)

    def process_item(self, item, spider):
        #向mysql插入数据
        reviewID=item['reviewID']
        sightID=item['sightID']
        userID=item['userID']
        useful=item['useful']
        commentTime=item['commentTime']
        content = item.get('content'),
        score = item['score'],
        userName = item['userName'],
        sceneryScore = item.get('sceneryScore'),
        interestScore = item.get('interestScore'),
        costPerformScore = item.get('costPerformScore')
        self.cursor.execute("insert into review(reviewID,sightID,userID,useful,commentTime,content,score,userName,sceneryScore,interestScore,costPerformScore) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (reviewID,sightID,userID,useful,commentTime,content,score,userName,sceneryScore,interestScore,costPerformScore))
        return item

    #结束时自动执行此函数
    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()


class urlOfSightPipeline(object):
    def open_spider(self, spider):
        self.file = open('..\每个景点的url地址.txt', 'a', encoding='utf-8')

    def process_item(self, item, spider):
        #如果有排名，一起写入文件，用_隔开
        line = item['url']+"_"+item['ranking']+"\n"
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()

class sightPipeline(object):
    sightInsert = '''insert into sight(id,name,score,ranking,numOfComment,wantTogo,beenTo,address,grade,tel,openTime,intro,traffic,sceneryScore,interestScore,costPerformScore,loveComment,familyComment,friendComment,businessComment,aloneComment,greatComment,fineComment,generalComment,badComment,terribleComment) values \
        ('{id}','{name}','{score}',{ranking},'{numOfComment}','{wantTogo}','{beenTo}','{address}',{grade},'{tel}','{openTime}','{intro}','{traffic}','{sceneryScore}','{interestScore}','{costPerformScore}','{loveComment}','{familyComment}','{friendComment}','{businessComment}','{aloneComment}','{greatComment}','{fineComment}','{generalComment}','{badComment}','{terribleComment}')'''

    def open_spider(self, spider):
        self.connect = pymysql.connect(host='192.168.99.1',
                                       port=3306,
                                       db='xiecheng',
                                       user='root',
                                       passwd='123456',
                                       charset='utf8',
                                       use_unicode=True)
        self.cursor = self.connect.cursor()
        self.connect.autocommit(True)

    def process_item(self, item, spider):
        #向mysql插入数据
        sqlinsert = self.sightInsert.format(
            id=item['id'],
            name=item['name'],
            score=item.get('score'),
            ranking=item.get('ranking','NULL') ,
            numOfComment=item['numOfComment'],
            wantTogo=item['wantTogo'],
            beenTo=item['beenTo'],
            address=item.get('address','NULL'),
            grade=item.get('grade','NULL'),
            tel=item.get('tel','NULL'),
            openTime=item.get('openTime','NULL'),
            intro=item.get('intro','NULL'),
            traffic=item.get('traffic','NULL'),
            sceneryScore=item.get('sceneryScore',0),
            interestScore=item.get('interestScore',0),
            costPerformScore=item.get('costPerformScore',0),
            loveComment=item.get('loveComment',0),
            familyComment=item.get('familyComment',0),
            friendComment=item.get('friendComment',0),
            businessComment=item.get('businessComment',0),
            aloneComment=item.get('aloneComment',0),
            greatComment=item['greatComment'],
            fineComment=item['fineComment'],
            generalComment=item['generalComment'],
            badComment=item['badComment'],
            terribleComment=item['terribleComment']
        )
        id = item['id'],
        name = item['name'],
        score = item.get('score'),
        #ranking='NULL',
        ranking = item.get('ranking'),
        numOfComment = item['numOfComment'],
        wantTogo = item['wantTogo'],
        beenTo = item['beenTo'],
        address = item.get('address'),
        grade = item.get('grade'),
        tel = item.get('tel'),
        openTime = item.get('openTime'),
        intro = item.get('intro'),
        traffic = item.get('traffic'),
        sceneryScore = item.get('sceneryScore'),
        interestScore = item.get('interestScore'),
        costPerformScore = item.get('costPerformScore'),
        loveComment = item.get('loveComment'),
        familyComment = item.get('familyComment'),
        friendComment = item.get('friendComment'),
        businessComment = item.get('businessComment'),
        aloneComment = item.get('aloneComment'),
        greatComment = item['greatComment'],
        fineComment = item['fineComment'],
        generalComment = item['generalComment'],
        badComment = item['badComment'],
        terribleComment = item['terribleComment']

        #self.cursor.execute(sqlinsert)
        self.cursor.execute("insert into sight(id,name,score,ranking,numOfComment,wantTogo,beenTo,address,grade,tel,openTime,intro,traffic,sceneryScore,interestScore,costPerformScore,loveComment,familyComment,friendComment,businessComment,aloneComment,greatComment,fineComment,generalComment,badComment,terribleComment) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (id,name,score,ranking,numOfComment,wantTogo,beenTo,address,grade,tel,openTime,intro,traffic,sceneryScore,interestScore,costPerformScore,loveComment,familyComment,friendComment,businessComment,aloneComment,greatComment,fineComment,generalComment,badComment,terribleComment))


    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()