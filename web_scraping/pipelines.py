# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem

class CapstoneNewsPipeline(object):
    def process_item(self, item, spider):
        return item

class DuplicatesPipeline(object):

    def __init__(self):
        self.link_seen = set()

    def process_item(self, item, spider):
        if item['link'] in self.link_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.link_seen.add(item['link'])
            return item