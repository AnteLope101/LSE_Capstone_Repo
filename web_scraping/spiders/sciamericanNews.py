# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from dateutil import parser 
from w3lib.url import url_query_parameter
from datetime import date

class SciamericannewsSpider(scrapy.Spider):
    name = 'sciamericanNews'
    allowed_domains = ['scientificamerican.com']
    start_urls = ['https://www.scientificamerican.com//']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        top_urls = response.css('section[class="latest-articles-outer grid homepage-listing-swap "] a::attr(href)').extract()
        top_urls = [i for i in top_urls if '/article' in i or '/blogs' in i]

        popular_urls = response.css('h3[class="t_listing-title"] a::attr(href)').extract()
        
        all_urls = top_urls + popular_urls

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Scientific American'

        items['link'] = response.url

        d = response.css('time[itemprop="datePublished"]::text, span[itemprop="datePublished"]::attr(content)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            if 'Issue' in date_published:
                date_published = parser.parse(date_published, fuzzy=True).strftime("%b-%Y")
            else:
                date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('div[class="article-block article-text"] p::text, div[class="article-block article-text"] a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
