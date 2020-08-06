# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class GizmodonewsSpider(scrapy.Spider):
    name = 'gizmodoNews'
    allowed_domains = ['gizmodo.co.uk']
    start_urls = ['https://www.gizmodo.co.uk//']

    base_url = 'https://www.gizmodo.co.uk'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('div[class="media__body"] a::attr(href)').extract()
        all_links = [i for i in all_links if '/author' not in i]
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Gizmodo'

        items['link'] = response.url

        date_published = response.css('time[itemprop="datePublished"]::attr(datetime)').extract_first()
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('div[class="single-article__content group"] > p::text, div[class="single-article__content group"] > p > em::text, div[class="single-article__content group"] > p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
