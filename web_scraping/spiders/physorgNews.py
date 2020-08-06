# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class PhysorgnewsSpider(scrapy.Spider):
    name = 'physorgNews'
    allowed_domains = ['phys.org']
    start_urls = ['https://phys.org//']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        top_urls = response.css('div[class="row no-gutters mb-3"] a::attr(href)').extract()
        top_urls = [i for i in top_urls if '/phys.org' in i]

        other_urls = response.css('a[class="news-link"]::attr(href)').extract()
        other_urls = [i for i in other_urls if '/phys.org' in i]

        all_urls = top_urls + other_urls

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Phys.org'

        items['link'] = response.url

        date_published = response.css('div[class="article__info mb-2"] p::text')[0].extract().replace('\n','').replace('\t','').strip()
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(' '.join(response.css('div[class="mt-4 article-main"] > p::text, div[class="mt-4 article-main"] > p > a::text, div[class="mt-4 article-main"] > p > i::text').extract()).replace('\n','').split()) 

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items

