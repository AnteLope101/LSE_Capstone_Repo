# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from dateutil import parser


class PhysworldnewsSpider(scrapy.Spider):
    name = 'physworldNews'
    allowed_domains = ['physicsworld.com']
    start_urls = ['https://physicsworld.com//']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        top_urls = response.css('.article__title > a::attr(href)').extract()

        list_urls = response.css('.listing-block__title > a::attr(href)').extract()

        all_urls = top_urls + list_urls
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Physicsworld'

        items['link'] = response.url

        date_published = response.css('.single-header__meta::text')[0].extract()
        date_published = parser.parse(date_published, fuzzy=True, ignoretz=True).strftime("%d-%b-%Y")
        title = response.css('h1::text').extract()
        title = [i for i in title if '\n' not in i and '\t' not in i]
        if not title:
            title = response.css('.hero-top-banner__title span::text')[0].extract()
        else:
            title = title[0]
        body = ' '.join(response.css('.entry-content > p::text, .entry-content > p a::attr(href), .entry-content > p em::text, .entry-content > ul li::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
