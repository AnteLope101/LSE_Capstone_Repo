# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class IndependentscinewsnewsSpider(scrapy.Spider):
    name = 'independentscinewsNews'
    allowed_domains = ['independentsciencenews.org']
    start_urls = ['https://www.independentsciencenews.org/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        top_urls = response.css('.topStories a::attr(href)').extract()

        list_urls = response.css('h2 > a::attr(href)').extract()

        all_urls = top_urls + list_urls
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Independent Science News'

        items['link'] = response.url

        d = response.css('.date::text').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.pf-content > p::text, .pf-content > p > a::text, .pf-content > p > em::text, .pf-content > blockquote > p::text').extract()).replace('\n', '').strip()

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
