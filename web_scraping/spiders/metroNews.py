# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class MetronewsSpider(scrapy.Spider):
    name = 'metroNews'
    allowed_domains = ['metro.co.uk']
    start_urls = ['https://metro.co.uk/news/tech//', 'https://metro.co.uk/tag/science//']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        top_urls = response.css('.title > a::attr(href)').extract()

        list_urls = response.css('.nf-title > a::attr(href)').extract()

        all_urls = top_urls + list_urls
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Metro'

        items['link'] = response.url

        date_published = response.css('.post-date::text')[0].extract()
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text, h1 > span::text')[0].extract()
        body = ' '.join(response.css('.article-body > p::text, .article-body > p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
