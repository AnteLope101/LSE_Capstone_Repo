# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date


class InterestingengnewsSpider(scrapy.Spider):
    name = 'interestingengNews'
    allowed_domains = ['interestingengineering.com']
    start_urls = ['https://interestingengineering.com/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        main_urls = response.css('.main-post-title::attr(href)').extract()

        other_urls = response.css('h2[class="clearfix"] > a::attr(href)').extract() 

        all_urls = main_urls + other_urls
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Interesting Engineering'

        items['link'] = response.url

        d = response.css('div[class="post-tag"] > span::text').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('div[class="content-text clearfix"] > p::text, div[class="content-text clearfix"] > p em::text, div[class="content-text clearfix"] > p a::text, div[class="content-text clearfix"] > p span::text').extract())
        if not body:
            body = ' '.join(response.css('.body-element > p::text, .body-element > p > a::text, .body-element > p em::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
