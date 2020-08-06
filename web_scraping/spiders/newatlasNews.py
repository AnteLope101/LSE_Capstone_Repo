# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class NewatlasnewsSpider(scrapy.Spider):
    name = 'newatlasNews'
    allowed_domains = ['newatlas.com']
    start_urls = ['https://newatlas.com//']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        top_url = response.css('.PromoC-title > a::attr(href)').extract()

        list_urls = response.css('.PromoB-title > a::attr(href)').extract()

        all_urls = top_url + list_urls
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'New Atlas'

        items['link'] = response.url

        date_published = response.css('.ArticlePage-datePublished::text')[0].extract().replace('\n','')
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract().replace('\n','').strip()
        body = ' '.join(response.css('.RichTextArticleBody > div > p::text, .RichTextArticleBody > div > p a::attr(href)').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
