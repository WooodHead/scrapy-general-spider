# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import redis


from scrapy import signals


import json
import codecs
from collections import OrderedDict



class TXTWithEncodingPipeline(object):

    def __init__(self):
        self.file = codecs.open('data_utf8.txt', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        # line = '\t'.join([v for k, v in OrderedDict(item).items()]) + "\n"
        line = ''
        for k, v in OrderedDict(item).items():
            for d in v:
                # print type(d), d
                li = ['|'.join(v1) for k1, v1 in OrderedDict(d).items()]
                line = '\t'.join(li[-1:]) + '\n'
                self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()


class JsonWithEncodingPipeline(object):

    def __init__(self):
        self.file = codecs.open('data_utf8.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(OrderedDict(item), ensure_ascii=False, sort_keys=False) + "\n"
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()


class RedisPipeline(object):

    def __init__(self):
        self.r = redis.StrictRedis(host='localhost', port=6379)

    def process_item(self, item, spider):
        if not item['id']:
            print 'no id item!!'

        str_recorded_item = self.r.get(item['id'])
        final_item = None
        if str_recorded_item is None:
            final_item = item
        else:
            ritem = eval(self.r.get(item['id']))
            final_item = dict(item.items() + ritem.items())
        self.r.set(item['id'], final_item)

    def close_spider(self, spider):
        return

import sys
import MySQLdb
import hashlib
from scrapy.exceptions import DropItem
from scrapy.http import Request

class MySQLStorePipeline(object):
  def __init__(self):
    # self.conn = MySQLdb.connect(user='user', 'passwd', 'dbname', 'host', charset="utf8", use_unicode=True)
    self.conn = MySQLdb.connect(user='dbuser', passwd='dbpasswd', db='dbname', host='dbhost', charset="utf8", use_unicode=True)
    self.cursor = self.conn.cursor()

    def process_item(self, item, spider):    
        try:
            self.cursor.execute("""INSERT INTO example_book_store (book_name, price)  
                            VALUES (%s, %s)""", 
                           (item['book_name'].encode('utf-8'), 
                            item['price'].encode('utf-8')))

            self.conn.commit()


        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])


        return item
