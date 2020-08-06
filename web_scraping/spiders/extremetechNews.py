# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class ExtremetechnewsSpider(scrapy.Spider):
    name = 'extremetechNews'
    allowed_domains = ['extremetech.com']
    start_urls = ['https://www.extremetech.com/tag/science/']

    def parse(self, response):
        print("procesing:"+response.url)

        all_urls = response.css('h4 > a::attr(href)').extract()
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Extreme Tech'

        items['link'] = response.url

        d = ' '.join(response.css('.by.vcard::text').extract())
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d
            date_published = parser.parse(date_published, fuzzy=True, ignoretz=True).strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('span[id="intelliTXT"] > p::text, span[id="intelliTXT"] > p > span::text, span[id="intelliTXT"] > p a::text, span[id="intelliTXT"] > p em::text').extract()).replace('\n', '').strip()

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
