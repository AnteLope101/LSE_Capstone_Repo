# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class LivescinewsSpider(scrapy.Spider):
    name = 'livesciNews'
    allowed_domains = ['livescience.com']
    start_urls = ['https://www.livescience.com//']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css("a[class='article-link']::attr(href)").extract()

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Live Science'

        items['link'] = response.url

        date_published = response.css('.chunk::text')[0].extract()
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('div[itemprop="articleBody"] > p::text, div[itemprop="articleBody"] > p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
