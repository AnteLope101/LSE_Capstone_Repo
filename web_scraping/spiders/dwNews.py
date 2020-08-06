# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class DwnewsSpider(scrapy.Spider):
    name = 'dwNews'
    allowed_domains = ['dw.com']
    start_urls = ['https://www.dw.com/en/top-stories/science/s-12526/']

    base_url = 'https://www.dw.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('.col2.basicTeaser > div > a::attr(href)').extract()
        all_links = [i for i in all_links if '/g-' not in i and '/av-' not in i]
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'DW'

        items['link'] = response.url

        d = response.css('.smallList > li::text').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.longText > p::text, .longText > p a::text, .longText > p em::text').extract()).replace('\n', '').replace('\xa0','')

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
