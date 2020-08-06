# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser

class SciNewsnewsSpider(scrapy.Spider):
    name = 'sci_newsNews'
    allowed_domains = ['sci-news.com']
    start_urls = ['http://www.sci-news.com/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        top_urls = response.css('.info > a::attr(href)').extract()

        featured_urls = response.css('h3 > a::attr(href)').extract()

        list_urls = response.css('.list-articles a::attr(href)').extract()

        headlist_urls = response.css('.headlines-list a::attr(href)').extract()

        all_urls = top_urls + featured_urls + list_urls + headlist_urls
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Sci-News'

        items['link'] = response.url

        d = response.css('.date::text').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = parser.parse(date_published, fuzzy=True, ignoretz=True).strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.entry-content > p::text, .entry-content > p strong::text, .entry-content > p strong > em::text, .entry-content > p > em::text, .entry-content > p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
