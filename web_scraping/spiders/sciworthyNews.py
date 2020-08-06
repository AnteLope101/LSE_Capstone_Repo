# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class SciworthynewsSpider(scrapy.Spider):
    name = 'sciworthyNews'
    allowed_domains = ['sciworthy.com']
    start_urls = ['https://sciworthy.com/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        top_urls = response.css('.fg-item > a::attr(href)').extract()

        list_urls = response.css('h1 > a::attr(href)').extract()

        all_urls = top_urls + list_urls
        all_urls = [i for i in all_urls if i != 'https://sciworthy.com/']
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Sciworthy'

        items['link'] = response.url

        d = response.css('time[class="entry-date published"]::attr(datetime)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('.entry-title-primary::text')[0].extract()
        body = ' '.join(response.css('.entry-content > p > span::text, .entry-content > p::text, .entry-content > p > span > a::text, .entry-content > p > a::text').extract()).replace('\n', '').strip()

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
