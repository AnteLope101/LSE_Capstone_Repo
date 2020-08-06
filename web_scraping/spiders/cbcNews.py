# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class CbcnewsSpider(scrapy.Spider):
    name = 'cbcNews'
    allowed_domains = ['cbc.ca']
    start_urls = ['https://www.cbc.ca/news/technology/']

    base_url = 'https://www.cbc.ca'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('.contentArea a::attr(href)').extract()
        all_links = [i for i in all_links if '/news' in i]
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'CBC News'

        items['link'] = response.url

        date_published = response.css('time::attr(datetime)')[0].extract()
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.story p::text, .story p > em::text, .story p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
