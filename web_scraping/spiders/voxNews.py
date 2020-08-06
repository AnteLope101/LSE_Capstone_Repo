# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date


class VoxnewsSpider(scrapy.Spider):
    name = 'voxNews'
    allowed_domains = ['vox.com']
    start_urls = ['https://www.vox.com/science-and-health/', 'https://www.vox.com/technology/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        featured_urls = response.css('div[class="c-two-up__main"] > div > a::attr(href)').extract()

        other_urls = response.css('div[class="c-compact-river"] > div > div > a::attr(href)').extract()

        all_urls = featured_urls + other_urls
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Vox'

        items['link'] = response.url

        d = response.css('time[class="c-byline__item"]::attr(datetime)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('div[class="c-entry-content "] > p::text, div[class="c-entry-content "] > p > a::text').extract())
        if not body:
            body = ' '.join(response.css('div[class="c-entry-content c-entry-content__stream "] > p::text, div[class="c-entry-content c-entry-content__stream "] > p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
