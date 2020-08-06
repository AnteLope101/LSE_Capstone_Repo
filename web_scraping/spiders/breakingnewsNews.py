# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class BreakingnewsnewsSpider(scrapy.Spider):
    name = 'breakingnewsNews'
    allowed_domains = ['breakingnews.ie']
    start_urls = ['https://www.breakingnews.ie/tech//']

    base_url = 'https://www.breakingnews.ie'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        top_links = response.css('h3 > a::attr(href)').extract()

        other_links = response.css('h4 > a::attr(href)').extract()

        # create urls
        all_links = top_links + other_links 
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'BreakingNews'

        items['link'] = response.url

        d = response.css('span[itemprop="datePublished"]::text').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        t = response.css('h2[itemprop="headline"]::text, h2[itemprop="headline"] > span::text').extract()
        if not t:
            title = response.css('h1 > span::text').extract()
        else:
            title = t[0]
        body = ' '.join(response.css('span[itemprop="articleBody"] > p::text, span[itemprop="articleBody"] > p > a::text, span[itemprop="articleBody"] > p > em::text').extract()).replace('\n','')
        if not body:
            body = ' '.join(response.css('story > p::text, story > p > a::text, story > p > i::text, story > p > em::text').extract()).replace('\n','')

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
