# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from dateutil import parser
from datetime import date


class SkynewsnewsSpider(scrapy.Spider):
    name = 'skynewsNews'
    allowed_domains = ['news.sky.com']
    start_urls = ['https://news.sky.com/technology/']

    base_url = 'https://news.sky.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('.sdc-site-tile__headline > a::attr(href)').extract()
        all_links = [i for i in all_links if '/video' not in i]
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Sky News'

        items['link'] = response.url

        d = response.css('.sdc-article-date__date-time::text').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = parser.parse(date_published, fuzzy=True, ignoretz=True).strftime("%d-%b-%Y")
        title = response.css('h1 span::text')[0].extract().replace('\n','').strip()
        body = ' '.join(response.css('div[class="sdc-article-body sdc-article-body--lead"] > p::text, div[class="sdc-article-body sdc-article-body--lead"] > p a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
