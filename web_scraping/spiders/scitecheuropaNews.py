# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class ScitecheuropanewsSpider(scrapy.Spider):
    name = 'scitecheuropaNews'
    allowed_domains = ['scitecheuropa.eu']
    start_urls = ['https://www.scitecheuropa.eu//']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css('.td-module-thumb > a::attr(href)').extract()
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'SciTech Europa'

        items['link'] = response.url

        d = response.css('.td-post-title time::attr(datetime)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.td-post-content > p::text, .td-post-content > p > a::text, .td-post-content > p em::text').extract()).replace('\n', '').strip()

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
