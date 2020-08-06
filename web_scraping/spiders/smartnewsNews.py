# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date


class SmartnewsnewsSpider(scrapy.Spider):
    name = 'smartnewsNews'
    allowed_domains = ['smithsonianmag.com']
    start_urls = ['https://www.smithsonianmag.com/smartnews/science/',
                  'https://www.smithsonianmag.com/smartnews/ideas-innovations/',
                  'https://www.smithsonianmag.com/science-nature/',
                  'https://www.smithsonianmag.com/innovation/']

    base_url = 'https://www.smithsonianmag.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('h3 a::attr(href)').extract()

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Smart News'

        items['link'] = response.url

        d = response.css('.pub-date::attr(data-pubdate), div[class="author-name-date floatstyle"] > span::text').extract()
        if not d:
            date_published = response.css('div[class="author-name-name"] > span::text').extract()
            if not date_published:
                date_published = date.today().strftime("%d-%b-%Y")
            else:
                date_published = date_published[1]
                date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        ti = response.css('h1::text').extract()  
        if not ti:
            title = response.css('main h2::text')[0].extract()  
        else:
            title = ti[0]
        body = " ".join(response.css('div[class="article-body pagination-first"] > p::text, div[class="article-body pagination-first"] > p > a::text, div[class="article-body pagination-first"] > p > span::text').extract()) 

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
