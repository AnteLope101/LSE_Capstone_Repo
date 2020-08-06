# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class VenturebeatnewsSpider(scrapy.Spider):
    name = 'venturebeatNews'
    allowed_domains = ['venturebeat.com']
    start_urls = ['https://venturebeat.com/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        hero_url = response.css('.Hero__title > a::attr(href)').extract()

        list_urls = response.css('.ArticleListing__title > a::attr(href)').extract()

        all_urls = hero_url+ list_urls
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'VentureBeat'

        items['link'] = response.url

        d = response.css('time::attr(datetime)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.article-content > p::text, .article-content > p > a::text, .article-content > p em::text').extract()).replace('\n', '').replace('\xa0','')

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
