# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class TimenewsSpider(scrapy.Spider):
    name = 'timeNews'
    allowed_domains = ['time.com']
    start_urls = ['https://time.com/section/tech//']

    base_url = 'https://time.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('a[class="media-img margin-16-bottom"]::attr(href)').extract()
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Time'

        items['link'] = response.url

        d = response.css('div[class="timestamp published-date padding-12-left"]::text').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0].split('|')[0]
            date_published = parser.parse(date_published, fuzzy=True, ignoretz=True).strftime("%d-%b-%Y") 
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.padded > p::text, .padded > p > a::text, .padded > p > i::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
