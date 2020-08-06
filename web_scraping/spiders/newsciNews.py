# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date


class NewscinewsSpider(scrapy.Spider):
    name = 'newsciNews'
    allowed_domains = ['newscientist.com']
    start_urls = ['https://www.newscientist.com//']

    base_url = 'https://www.newscientist.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('.card__link::attr(href)').extract()

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'New Scientist'

        items['link'] = response.url

        d = response.css('.published-date::text').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0].split(',')[0].replace('\n','').strip()
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('.content__title::text')[0].extract()  
        body = " ".join(response.css(".article-content > p::text, .article-content > p > a::text").extract()).replace('\r','').replace('\n','').strip() 

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
