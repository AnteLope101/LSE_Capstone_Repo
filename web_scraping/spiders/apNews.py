# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class ApnewsSpider(scrapy.Spider):
    name = 'apNews'
    allowed_domains = ['apnews.com']
    start_urls = ['https://apnews.com/apf-science/', 'https://apnews.com/apf-technology/']

    base_url = 'https://apnews.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('.CardHeadline > a::attr(href)').extract() 

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'AP News'

        items['link'] = response.url

        date_published = response.css('span[data-key="timestamp"]::text')[0].extract()
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract() 
        body = ' '.join(response.css('.Article > p::text, .Article > p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
