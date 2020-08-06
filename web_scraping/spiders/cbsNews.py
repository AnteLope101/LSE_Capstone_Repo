# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date


class CbsnewsSpider(scrapy.Spider):
    name = 'cbsNews'
    allowed_domains = ['cbsnews.com']
    start_urls = ['https://www.cbsnews.com/science/', 'https://www.cbsnews.com/technology/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css('div[class="col-8 nocontent"] a::attr(href)').extract()
        all_urls = [i for i in all_urls if '/news' in i]
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'CBS News'

        items['link'] = response.url

        d = response.css('p[class="content__meta content__meta-timestamp"] > time::attr(datetime)').extract()
        if not d:
            dd = response.css('.time::text').extract()
            if not dd:
                date_published = date.today().strftime("%d-%b-%Y")
            else:
                date_published = dd[0]
                date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        t = response.css('.content__title::text').extract()
        if not t:
            title = response.css('h1::text')[0].extract()
        else:
            title = t[0]
        body = ' '.join(response.css('.content__body > p::text, .content__body > p  a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
