# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class NewscomnewsSpider(scrapy.Spider):
    name = 'newscomNews'
    allowed_domains = ['news.com.au']
    start_urls = ['https://www.news.com.au/technology/science/']

    def parse(self, response):
        print("procesing:"+response.url)

        all_urls = response.css('h4 > a::attr(href)').extract()
        all_urls = [i for i in all_urls if '/news-story' in i]
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'News.com.au'

        items['link'] = response.url

        d = response.css('.datestamp::text').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.story-content > p::text, .story-content > p a::text, .story-content > p i::text').extract()).replace('\n', '').strip()

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items

