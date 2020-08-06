# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date


class FoxnewsSpider(scrapy.Spider):
    name = 'foxNews'
    allowed_domains = ['foxnews.com']
    start_urls = ['https://www.foxnews.com/science/', 'https://www.foxnews.com/tech/']

    base_url = 'https://www.foxnews.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('h2[class="title"] > a::attr(href), h4[class="title"] > a::attr(href)').extract()
        all_links = [i for i in all_links if '/science' in i and 'pictures' not in i]
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Fox News'

        items['link'] = response.url

        d = response.css('time::text').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.article-body > p::text, .article-body > p > a::text, .article-body > ul > li::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
