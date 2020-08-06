# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date


class TheconversationnewsSpider(scrapy.Spider):
    name = 'theconversationNews'
    allowed_domains = ['theconversation.com']
    start_urls = ['https://theconversation.com/uk/technology/']

    base_url = 'https://theconversation.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('h2 > a::attr(href)').extract()
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'The Conversation'

        items['link'] = response.url

        d = response.css('time::attr(datetime)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1 > strong::text')[0].extract().replace('\n','').strip() 
        body = ' '.join(response.css('div[itemprop="articleBody"] > p::text, div[itemprop="articleBody"] > p em::text, div[itemprop="articleBody"] > p a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
