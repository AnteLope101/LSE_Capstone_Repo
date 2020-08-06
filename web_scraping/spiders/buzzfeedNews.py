# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from dateutil import parser


class BuzzfeednewsSpider(scrapy.Spider):
    name = 'buzzfeedNews'
    allowed_domains = ['buzzfeednews.com']
    start_urls = ['https://www.buzzfeednews.com/section/science/', 'https://www.buzzfeednews.com/section/tech/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css(".newsblock-story-card__title > a::attr(href)").extract()

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'BuzzFeed'

        items['link'] = response.url

        date_published = response.css('.news-article-header__timestamps-posted::text')[0].extract().replace('\n','')
        date_published = parser.parse(date_published, fuzzy=True, ignoretz=True).strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.js-article-wrapper > div > p::text, .js-article-wrapper > div > p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
