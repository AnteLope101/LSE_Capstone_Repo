# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class BulletinmailnewsSpider(scrapy.Spider):
    name = 'bulletinmailNews'
    allowed_domains = ['bulletinmail.com']
    start_urls = ['https://bulletinmail.com/']

    def parse(self, response):
        print("procesing:"+response.url)
        pass

 #       # extract links
 #       all_urls = response.css('.g1-frame::attr(href)').extract()
 #       all_urls = list(set(all_urls))

 #       for url in all_urls:
 #           yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Bulletin Mail'

        items['link'] = response.url

        d = response.css('time[itemprop="datePublished"]::attr(datetime)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('div[itemprop="articleBody"] > p::text, div[itemprop="articleBody"] > p > a::text, div[itemprop="articleBody"] > p > strong::text, div[itemprop="articleBody"] > p > em::text').extract()).replace('\n', '').strip()
        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
