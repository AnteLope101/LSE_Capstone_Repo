# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class HeadlinecodenewsSpider(scrapy.Spider):
    name = 'headlinecodeNews'
    allowed_domains = ['headlinecode.com']
    start_urls = ['https://headlinecode.com/science//', 'https://headlinecode.com/technology//']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css('h3 > a::attr(href)').extract()
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Headlinecode'

        items['link'] = response.url

        d = response.css('.entry-header .date.meta-item.fa-before::text').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('article > div > p::text, article > div > p > a::text, article > div > p > em::text').extract()).replace('\n', '').replace('\xa0','').strip()
        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
