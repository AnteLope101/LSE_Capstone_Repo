# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class CsonewsSpider(scrapy.Spider):
    name = 'csoNews'
    allowed_domains = ['csoonline.com']
    start_urls = ['https://www.csoonline.com/uk//']

    base_url = 'https://www.csoonline.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        top_links = response.css(".homepage-top-stories a::attr(href)").extract()

        other_links = response.css('.item-text::attr(href)').extract()

        list_links = response.css('h3 > a::attr(href)').extract() 

        # create urls
        all_links = top_links + other_links + list_links
        all_links = [i for i in all_links if i.startswith('/article')]
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'CSO Online'

        items['link'] = response.url

        d = response.css('.pub-date::attr(content)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract() 
        body = ' '.join(response.css('div[itemprop="articleBody"] > p::text, div[itemprop="articleBody"] > p > a::text, div[itemprop="articleBody"] > p > em::text, div[itemprop="articleBody"] > p > em > a::text').extract()).replace('\n','')
        if not body:
            body = ' '.join(response.css('div[itemprop="reviewBody"] > p::text, div[itemprop="reviewBody"] > p > a::text, div[itemprop="reviewBody"] > p i::text').extract()).replace('\n','')

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
