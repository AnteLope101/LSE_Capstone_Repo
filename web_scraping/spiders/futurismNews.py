# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from dateutil import parser
from datetime import date


class FuturismnewsSpider(scrapy.Spider):
    name = 'futurismNews'
    allowed_domains = ['futurism.com']
    start_urls = ['https://futurism.com//']

    base_url = 'https://futurism.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        top_links = response.css('div[class="sc-dnqmqq euQtQS pages__Row-r8po92-0 pages__TopContentRow-r8po92-1 fHFVhw"] a::attr(href)').extract()
        top_links = [i for i in top_links if len(i) > 20 and '/authors' not in i]

        other_links = response.css('div[class="sc-dnqmqq euQtQS pages__Row-r8po92-0 pages__CenterContentRow-r8po92-3 iZXSgS"] a::attr(href)').extract()
        other_links = [i for i in other_links if '/authors' not in i]

        all_links = top_links + other_links
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Futurism'

        items['link'] = response.url
        
        d = response.css('div[class="sc-kAzzGY cqipuB sc-kEYyzF bqjiDS"]::text').extract()
        if not d:
            d = response.css('div.Meta::text').extract()
            d = [i for i in d if ' 2020' in i or ' ago' in i]
            if not d:
                date_published = date.today().strftime("%d-%b-%Y")
            else:
               date_published = d[0]
               date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y") 
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = " ".join(response.css('div[itemprop="articleBody"] p::text, div[itemprop="articleBody"] p > em::text, div[itemprop="articleBody"] p > a::text').extract()) 
   
        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
