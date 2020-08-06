# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date


class MirrornewsSpider(scrapy.Spider):
    name = 'mirrorNews'
    allowed_domains = ['mirror.co.uk']
    start_urls = ['https://www.mirror.co.uk/tech/']


    def parse(self, response):
        print("procesing:"+response.url)

        # extract urls
        head_urls = response.css('a[class="headline publication-font"]::attr(href)').extract()

        teaser_urls = response.css('.teaser > a[class="headline"]::attr(href)').extract()

        all_urls = head_urls + teaser_urls
        all_urls = [i for i in all_urls if '/science' in i or '/tech' in i]
        all_urls = [i for i in all_urls if '-review-' not in i]
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Daily Mirror'

        items['link'] = response.url

        d = response.css('time::attr(datetime)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract() 
        body = ' '.join(response.css('.article-body > p::text, .article-body > p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items

