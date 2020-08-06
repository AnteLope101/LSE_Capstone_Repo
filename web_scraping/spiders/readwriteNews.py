# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class ReadwritenewsSpider(scrapy.Spider):
    name = 'readwriteNews'
    allowed_domains = ['readwrite.com']
    start_urls = ['https://readwrite.com/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css('h2 > a::attr(href)').extract()
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'ReadWrite'

        items['link'] = response.url

        d = response.css('.post-cat::text').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.entry-content.col-md-10 > p::text, .entry-content.col-md-10 > p a::text, .entry-content.col-md-10 > p em::text, .entry-content.col-md-10 > p i::text, .entry-content.col-md-10 > blockquote em::text, .entry-content.col-md-10 > p b::text, .entry-content.col-md-10 > p > span::text').extract()).replace('\n', '').strip()

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
