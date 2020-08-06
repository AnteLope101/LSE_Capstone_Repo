# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date


class HowstuffworksnewsSpider(scrapy.Spider):
    name = 'howstuffworksNews'
    allowed_domains = ['howstuffworks.com']
    start_urls = ['https://www.howstuffworks.com//']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css('div[class="tile-meta"] a::attr(href)').extract()
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'How Stuff Works'

        items['link'] = response.url

        d = response.css('.content-date::text').extract()
        if d:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        else:
            date_published = date.today().strftime("%d-%b-%Y")

        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('#page0 p::text, #page0 p > a::text').extract())
        #next_page = response.css('a[class="page-link next"]::attr(href)').extract()
        #if next_page:
        #    next_page_url = next_page[0]
        #    body = yield scrapy.Request(next_page_url, callback=lambda r: self.parse_next(r, body))

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items


    def parse_next(self, response, body_old):
        body_more = ' '.join(response.css('div[class="infinite-item"] > p::text').extract())
        body = [body_old, body_more]
        if None not in body:
            body = ' '.join([body_old, body_more])
        else:
            body = body_more

        next_page = response.css('a[class="page-link next"]::attr(href)').extract()
        if next_page:
            next_page_url = next_page[0]
            body = yield scrapy.Request(next_page_url, callback=lambda r: self.parse_next(r, body))
    
        return body


