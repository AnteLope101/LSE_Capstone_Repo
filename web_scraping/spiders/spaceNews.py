# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class SpacenewsSpider(scrapy.Spider):
    name = 'spaceNews'
    allowed_domains = ['space.com']
    start_urls = ['https://www.space.com//']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        featured_urls = response.css('section[class="feature-block top-featured"] a::attr(href)').extract()

        latest_urls = response.css('div[class="list-text-links list-text-links-trending-panel"] > div > a::attr(href)').extract()

        tech_urls = list(set(response.css('div[class="listingResults mixed1"] a::attr(href)').extract()))

        space_urls = response.css('div[class="listingResults mixed2"] a::attr(href)').extract()

        astro_urls = response.css('div[class="listingResults mixed3"] a::attr(href)').extract()

        life_urls = response.css('div[class="listingResults mixed4"] a::attr(href)').extract()

        sky_urls = response.css('div[class="listingResults mixed5"] a::attr(href)').extract()

        all_urls = featured_urls + latest_urls + tech_urls + space_urls + astro_urls + life_urls + sky_urls
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Space.com'

        items['link'] = response.url
        
        date_published = response.css('time[itemprop="datePublished"]::attr(datetime)')[0].extract()
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = " ".join(response.css('div[id="article-body"] > p::text, div[id="article-body"] > p > a::text, div[id="article-body"] > p u::text').extract()) 
   
        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
