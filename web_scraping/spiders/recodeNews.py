# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date 


class RecodenewsSpider(scrapy.Spider):
    name = 'recodeNews'
    allowed_domains = ['vox.com']
    start_urls = ['https://www.vox.com/recode/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css('h2[class="c-entry-box--compact__title"] a::attr(href)').extract()
        all_urls = [i for i in all_urls if 'podcast' not in i]

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Recode'

        items['link'] = response.url

        d = response.css('time::text').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('.c-page-title::text')[0].extract()
        body = ' '.join(response.css('.c-entry-content > p::text, .c-entry-content > p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
