# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class ZdnetnewsSpider(scrapy.Spider):
    name = 'zdnetNews'
    allowed_domains = ['zdnet.com']
    start_urls = ['https://www.zdnet.com/']

    base_url = 'https://www.zdnet.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # create urls
        all_links = response.css('h3 > a::attr(href)').extract()
        all_links = [i for i in all_links if '/article' in i]
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'ZDNet'

        items['link'] = response.url

        d = response.css('time::attr(datetime)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract() 
        body = ' '.join(response.css('.storyBody > p::text, .storyBody > p > a::text, .storyBody > ul > li::text, .storyBody > ul > li > strong::text, .storyBody > p > em::text').extract()).replace('\n','').replace('\xa0','')

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
