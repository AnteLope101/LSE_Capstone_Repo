# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class ScinewsforstudentsnewsSpider(scrapy.Spider):
    name = 'scinewsforstudentsNews'
    allowed_domains = ['sciencenewsforstudents.org']
    start_urls = ['https://www.sciencenewsforstudents.org/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        top_urls = response.css('h2 > a::attr(href)').extract()

        featured_urls = response.css('h3 > a::attr(href)').extract()

        all_urls = top_urls + featured_urls
        all_urls = [i for i in all_urls if '/article/' in i]
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Science News for Students'

        items['link'] = response.url

        d = response.css('.byline-inner time::attr(datetime)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.content > div > p::text, .content > div > p > a::text, .content > div > em::text').extract()).replace('\n', '').strip()

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
