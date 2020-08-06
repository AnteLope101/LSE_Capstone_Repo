# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class ArstechnewsSpider(scrapy.Spider):
    name = 'arstechNews'
    allowed_domains = ['arstechnica.com']
    start_urls = ['https://arstechnica.com//']


    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css('h2 a::attr(href)').extract()

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Ars Technica'

        items['link'] = response.url

        date_published = response.css('.date::text')[0].extract()
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('div[class="article-content post-page"] p::text, div[class="article-content post-page"] > p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
