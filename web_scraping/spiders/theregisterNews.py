# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class TheregisternewsSpider(scrapy.Spider):
    name = 'theregisterNews'
    allowed_domains = ['theregister.co.uk']
    start_urls = ['https://www.theregister.co.uk/']

    base_url = 'https://www.theregister.co.uk'

    def parse(self, response):
        print("procesing:"+response.url)

        # create urls
        all_links = response.css('article > a::attr(href)').extract()
        all_links = [i for i in all_links if i.startswith('/2020')]
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'The Register'

        items['link'] = response.url

        d = response.css('.dateline::text').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0].replace('\xa0',' ')
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = ' '.join(response.css('h1::text, h1 > i::text').extract())
        body = ' '.join(' '.join(response.css('div[id="body"] > p::text, div[id="body"] > p > a::text, div[id="body"] > p > i::text, div[id="body"] > p > a > i::text, div[id="body"] > p > strong::text').extract()).split()) 

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
