# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class NaturenewsSpider(scrapy.Spider):
    name = 'natureNews'
    allowed_domains = ['nature.com']
    start_urls = ['https://www.nature.com/news/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        featured_urls = response.css('section[class="section__top-new cleared"] a::attr(href)').extract()

        latest_urls = response.css('section[class="section__news cleared"] ul a::attr(href)').extract()

        opinion_urls = response.css('section[class="section__opinion cleared"] ul a::attr(href)').extract()

        research_urls = response.css('section[class="section__research-analysis cleared"] ul a::attr(href)').extract()

        career_urls = response.css('section[class="section__career cleared"] ul a::attr(href)').extract()

        all_urls = featured_urls + latest_urls + opinion_urls + research_urls + career_urls
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Nature News'

        items['link'] = response.url
        
        date_published = response.css('time[itemprop="datePublished"]::text')[0].extract()
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1[itemprop="headline"]::text')[0].extract()
        body = " ".join(response.css('div[class="article__body serif cleared"]>p::text, div[class="article__body serif cleared"]>p>i::text, div[class="article__body serif cleared"]>p>a::text').extract()) 
   
        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
