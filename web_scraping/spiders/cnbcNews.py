# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from dateutil import parser


class CnbcnewsSpider(scrapy.Spider):
    name = 'cnbcNews'
    allowed_domains = ['cnbc.com']
    start_urls = ['https://www.cnbc.com/health-and-science//','https://www.cnbc.com/technology//']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css('div[class="PageBuilder-col-9 PageBuilder-col"] a::attr(href)').extract()
        all_urls = [i for i in all_urls if '/2020/' in i]
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'CNBC News'

        items['link'] = response.url

        d = response.css('time[data-testid="published-timestamp"]::text').extract()
        if not d:
            date_published = response.css('.datestamp::text')[0].extract()
        else:
            date_published = d[0]
        date_published = parser.parse(date_published, fuzzy=True, ignoretz=True).strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.group > p::text, .group > p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
