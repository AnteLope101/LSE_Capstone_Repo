# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from dateutil import parser


class CtvnewsSpider(scrapy.Spider):
    name = 'ctvNews'
    allowed_domains = ['ctvnews.ca']
    start_urls = ['https://www.ctvnews.ca/sci-tech/']

    base_url = 'https://www.ctvnews.ca'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('.teaserTitle > a::attr(href)').extract()
        all_links = [i for i in all_links if '/video' not in i]
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'CTV News'

        items['link'] = response.url

        date_published = response.css('.date::text')[0].extract().replace('\t','').replace('\n','')
        date_published = parser.parse(date_published, fuzzy=True, ignoretz=True).strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.clearfix > div > p::text, .clearfix > div > p > a::text').extract()).replace('\t','').replace('\n','')

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
