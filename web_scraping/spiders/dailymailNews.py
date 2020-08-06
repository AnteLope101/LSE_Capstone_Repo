# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date


class DailymailnewsSpider(scrapy.Spider):
    name = 'dailymailNews'
    allowed_domains = ['dailymail.co.uk']
    start_urls = ['https://www.dailymail.co.uk/sciencetech/index.html/']

    base_url = 'https://www.dailymail.co.uk'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('h2 > a::attr(href)').extract()
        all_links = [i for i in all_links if '/article' in i]
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Daily Mail'

        items['link'] = response.url

        d = response.css('time::attr(datetime)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        t = response.css('h2::text').extract()
        if not t:
            title = response.css('h1::text').extract()
        else:
            title = t[0]
        body = ' '.join(response.css('div[itemprop="articleBody"] > p::text, div[itemprop="articleBody"] > p > a::text').extract())
        if not body:
            body = ' '.join(response.css('.mol-para-with-font::text, .mol-para-with-font > a::text, .mol-para-with-font > em::text, .mol-para-with-font > i::text').extract()).replace('\xa0','')

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
