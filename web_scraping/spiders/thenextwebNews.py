# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from dateutil import parser


class ThenextwebnewsSpider(scrapy.Spider):
    name = 'thenextwebNews'
    allowed_domains = ['thenextweb.com']
    start_urls = ['https://thenextweb.com//']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css('.story-title a::attr(href) , .cover-title a::attr(href)').extract()
        all_urls = [i for i in all_urls if '/2020' in i]

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'The Next Web'

        items['link'] = response.url

        date = response.css('.post-byline .timeago::attr(datetime)').extract()
        if not date:
            date_published = response.css('.c-post-pubDate::text')[0].extract()
            date_published = parser.parse(date_published, fuzzy=True, ignoretz=True).strftime("%d-%b-%Y")
        else:
            date_published = date[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('div[class="post-body fb-quotable u-m-3"] > p::text, div[class="post-body fb-quotable u-m-3"] > p > a::text').extract()).replace('\n','').strip()
        if not body:
            body = ' '.join(response.css('div[class="c-formatted c-post-content"] > p::text, div[class="c-formatted c-post-content"] > p a::text, div[class="c-formatted c-post-content"] > p > span::text').extract()).replace('\n','').replace('\xa0','').strip()

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
