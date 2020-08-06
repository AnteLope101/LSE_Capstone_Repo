# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class GeekwirenewsSpider(scrapy.Spider):
    name = 'geekwireNews'
    allowed_domains = ['geekwire.com']
    start_urls = ['https://www.geekwire.com//']

    def parse(self, response):
        print("procesing:"+response.url)

        all_urls = response.css('h2 > a::attr(href), header > a::attr(href)').extract()
        all_urls = [i for i in all_urls if '/2020' in i]
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'GeekWire'

        items['link'] = response.url

        d = response.css('.page-header time[itemprop="datePublished"]::attr(datetime)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('div[itemprop="articleBody"] > p::text, div[itemprop="articleBody"] > p a::text, div[itemprop="articleBody"] > p em::text, div[itemprop="articleBody"] > ul li::text').extract()).replace('\n', '').strip()

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
