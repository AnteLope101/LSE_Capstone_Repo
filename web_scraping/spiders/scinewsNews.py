# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class ScinewsnewsSpider(scrapy.Spider):
    name = 'scinewsNews'
    allowed_domains = ['sciencenews.org']
    start_urls = ['https://www.sciencenews.org/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        featured_urls = response.css('section[class="featured-articles__wrapper___1dxwZ"] a::attr(href)').extract()

        trending_urls = response.css('section[class="trending-stories__wrapper___1KLqW"] a::attr(href)').extract()

        promoted_urls = response.css('section[class="promoted-stories__section___zvI1g"] a::attr(href)').extract()

        topic_urls = response.css('section[class="topics-river__wrapper___2CozB"] a::attr(href)').extract()

        all_urls = featured_urls + trending_urls + promoted_urls + topic_urls
        all_urls = [i for i in all_urls if '/article/' in i]
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Science News'

        items['link'] = response.url
        
        if len(response.css('time[class="date entry-date header-default__published___foBuM"]::text').extract()) > 0:
            date_published = response.css('time[class="date entry-date header-default__published___foBuM"]::text')[0].extract()
        else:
            date_published = response.css('.byline__published___3GjAo::text')[0].extract()
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        t = response.css('.header-default__title___2wL7r::text').extract()
        if not t:
            title = response.css('h1::text')[0].extract()
        else:
            title = t[0]
        body = ' '.join(response.css('.single__rich-text___BlzVF > p::text, .single__rich-text___BlzVF > p > a::text, .single__rich-text___BlzVF > p > em::text').extract()).replace('\n',' ')

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
