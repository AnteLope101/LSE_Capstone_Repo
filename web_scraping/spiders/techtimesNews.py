# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class TechtimesnewsSpider(scrapy.Spider):
    name = 'techtimesNews'
    allowed_domains = ['techtimes.com']
    start_urls = ['https://www.techtimes.com/science/','https://www.techtimes.com/personaltech/','https://www.techtimes.com/health']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css('.art-title > a::attr(href)').extract()
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Tech Times'

        items['link'] = response.url

        date_published = response.css('time::attr(datetime)')[0].extract()
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('div[itemprop="articleBody"] > p > span::text, div[itemprop="articleBody"] > p::text, div[itemprop="articleBody"] > p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
