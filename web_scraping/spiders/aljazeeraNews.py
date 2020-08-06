# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class AljazeeranewsSpider(scrapy.Spider):
    name = 'aljazeeraNews'
    allowed_domains = ['aljazeera.com']
    start_urls = ['https://www.aljazeera.com/topics/categories/science-and-technology.html/']

    base_url = 'https://www.aljazeera.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        top_links = response.css('.frame-container a::attr(href)').extract()

        other_links = response.css('div[class="row topics-sec-item default-style"] > div > a::attr(href)').extract()

        opinion_links = response.css('.topics-sidebar-title::attr(href)').extract()

        indepth_links = response.css('.indepth-wrapper > a::attr(href)').extract()

        # create urls
        all_links = top_links + other_links + opinion_links + indepth_links
        all_links = [i for i in all_links if '/programmes' not in i]
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Aljazeera'

        items['link'] = response.url

        d = response.css('time::attr(datetime)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = parser.parse(date_published, fuzzy=True, ignoretz=True).strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.article-p-wrapper > p::text, .article-p-wrapper > p > a::text, .article-p-wrapper > p > em::text').extract()).replace('\n','').replace('\xa0','') 

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
