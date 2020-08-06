# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date


class GuardiannewsSpider(scrapy.Spider):
    name = 'guardianNews'
    allowed_domains = ['theguardian.com']
    start_urls = ['https://www.theguardian.com/science/', 'https://www.theguardian.com/uk/technology/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css('div[class="fc-item__content "] a::attr(href)').extract() 
        all_urls = [i for i in all_urls if '/science' in i or '/technology' in i] 
        all_urls = [i for i in all_urls if '-podcast' not in i and '-video' not in i and '/gallery' not in i]
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'The Guardian'

        items['link'] = response.url

        d = response.css('time[itemprop="datePublished"]::attr(datetime)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract().replace('\n','')
        body = ' '.join(response.css('div[itemprop="articleBody"] > p::text, div[itemprop="articleBody"] > p a::text, div[itemprop="articleBody"] > p span::text').extract())
        if not body:
            body = ' '.join(response.css('div[itemprop="reviewBody"] > p::text, div[itemprop="reviewBody"] > p a::text, div[itemprop="reviewBody"] > p span::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
