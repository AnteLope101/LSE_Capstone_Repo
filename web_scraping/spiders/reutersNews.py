# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from dateutil import parser
from datetime import date


class ReutersnewsSpider(scrapy.Spider):
    name = 'reutersNews'
    allowed_domains = ['reuters.com']
    start_urls = ['https://uk.reuters.com/news/technology/']

    base_url = 'https://uk.reuters.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('.story-content > a::attr(href)').extract()
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Reuters'

        items['link'] = response.url

        d = response.css('.ArticleHeader_date::text').extract()
        if not d:
            date_published = date.today.strftime("%d-%b-%Y")
        else:
            date_published = d[0].split('/')
            if len(date_published) > 1:
                date_published = date_published[0]
            else:
                date_published = d[0]
            date_published = parser.parse(date_published, fuzzy=True, ignoretz=True).strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.StandardArticleBody_body > p::text, .StandardArticleBody_body > p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
