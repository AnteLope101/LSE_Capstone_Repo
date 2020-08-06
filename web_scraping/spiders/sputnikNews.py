# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from dateutil import parser


class SputniknewsSpider(scrapy.Spider):
    name = 'sputnikNews'
    allowed_domains = ['sputniknews.com']
    start_urls = ['https://sputniknews.com/science/']

    base_url = 'https://sputniknews.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('.b-stories__img::attr(href)').extract()
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Sputnik'

        items['link'] = response.url

        date_published = response.css('.b-article__refs-date::text')[0].extract()
        date_published = parser.parse(date_published, fuzzy=True, ignoretz=True).strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.b-article__lead > p::text, .b-article__text > p::text, .b-article__text > p > a::text, .marker-quote1::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items

