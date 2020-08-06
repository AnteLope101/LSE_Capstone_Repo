# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date


class AbcnewsnewsSpider(scrapy.Spider):
    name = 'abcnewsNews'
    allowed_domains = ['abcnews.go.com']
    start_urls = ['https://abcnews.go.com/Technology/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css('h1 > a::attr(href)').extract()
        all_urls = [i for i in all_urls if '/wireStory' in i]
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'ABC News'

        items['link'] = response.url

        d = response.css('div[class="Byline__Meta Byline__Meta--publishDate"]::text').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('.Article__Headline__Title::text')[0].extract()
        body = ' '.join(response.css('article[class="Article__Content story"] > p::text, article[class="Article__Content story"] > p > a::text').extract()).replace('\n','')

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
