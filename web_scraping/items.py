# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class CapstoneNewsItem(scrapy.Item):
    # define the fields for your item here like:
    source = scrapy.Field()
    link = scrapy.Field()
    date_published = scrapy.Field()
    title = scrapy.Field()
    article = scrapy.Field()
    
