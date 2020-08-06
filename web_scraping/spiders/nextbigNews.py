# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class NextbignewsSpider(scrapy.Spider):
    name = 'nextbigNews'
    allowed_domains = ['nextbigfuture.com']
    start_urls = ['https://www.nextbigfuture.com//']

    i = 1

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css('.tag_to_view+ a::attr(href)').extract() 

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)
            
        #self.i += 1
            
        #if self.i > 1:
        #    next_url = 'https://www.nextbigfuture.com/' + 'page/' + self.i
        #    yield scrapy.Request(next_url, callback=self.parse)
            


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Next Big Future'

        items['link'] = response.url

        date_published = response.css('.updated span::text')[0].extract()
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('.entry-title::text')[0].extract()  
        body = ' '.join(response.css('div[class="thecontent"]>p::text, div[class="thecontent"]>p>a::text, div[class="thecontent"]>p>i::text').extract()).replace('\u2063', '').replace('\n', '')

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
