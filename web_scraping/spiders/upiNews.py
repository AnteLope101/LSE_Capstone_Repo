# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class UpinewsSpider(scrapy.Spider):
    name = 'upiNews'
    allowed_domains = ['upi.com']
    start_urls = ['https://www.upi.com/Science_News//']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css('div[class="col-md-7 lato"] a::attr(href)').extract()
        all_urls = [i for i in all_urls if '/2020/0' in i]
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'UPI'

        items['link'] = response.url

        date_published = ' '.join(response.css('.article-date::text')[0].extract().split())
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('article[itemprop="articleBody"] > p::text, article[itemprop="articleBody"] > p i::text, p::text, article[itemprop="articleBody"] > p a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items

