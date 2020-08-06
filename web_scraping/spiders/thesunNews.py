# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class ThesunnewsSpider(scrapy.Spider):
    name = 'thesunNews'
    allowed_domains = ['thesun.co.uk']
    start_urls = ['https://www.thesun.co.uk/tech/science//']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css('.teaser-anchor::attr(href)').extract()

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'The Sun'

        items['link'] = response.url

        date_published = response.css('.article__datestamp::text')[0].extract().replace(',','')
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.article__content > p::text, .article__content > p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
