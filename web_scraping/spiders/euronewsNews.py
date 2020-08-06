# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class EuronewsnewsSpider(scrapy.Spider):
    name = 'euronewsNews'
    allowed_domains = ['euronews.com']
    start_urls = ['https://www.euronews.com/knowledge/sci-tech/']

    base_url = 'https://www.euronews.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('a[rel="bookmark"]::attr(href)').extract()
        all_links = [i for i in all_links if 'https://' not in i and '/video' not in i and '/living' not in i]  
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Euronews'

        items['link'] = response.url

        date_published = response.css('time::attr(datetime)')[0].extract()
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('div[class="c-article-content  js-article-content article__content"] > p::text, div[class="c-article-content  js-article-content article__content"] > p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items

