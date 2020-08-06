# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class QuantamagnewsSpider(scrapy.Spider):
    name = 'quantamagNews'
    allowed_domains = ['quantamagazine.org']
    start_urls = ['https://www.quantamagazine.org//']

    base_url = 'https://www.quantamagazine.org'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        title_link = response.css('div[class="hero-title pb2"] > a::attr(href)').extract()

        other_links = response.css('div[class="card__content"] > a::attr(href)').extract()

        all_links = title_link + other_links
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Quanta Magazine'

        items['link'] = response.url
        
        date_published = response.css('.pv025 em::text')[0].extract()
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1[class="post__title__title mv025 noe"]::text')[0].extract()
        body = " ".join(response.css('.theme__anchors--underline > p::text, .theme__anchors--underline > p > a::text, .theme__anchors--underline > p > a > span::text').extract()) 
   
        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
