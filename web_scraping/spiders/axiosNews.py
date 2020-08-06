# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class AxiosnewsSpider(scrapy.Spider):
    name = 'axiosNews'
    allowed_domains = ['axios.com']
    start_urls = ['https://www.axios.com/science/','https://www.axios.com/technology/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css('h3 > a::attr(href)').extract()
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Axios'

        items['link'] = response.url

        d = response.css('article .fWINAL::text').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = parser.parse(date_published, fuzzy=True, ignoretz=True).strftime("%d-%b-%Y")
        title = response.css('article h1::text')[0].extract()
        body = ' '.join(response.css('article > div > div > p::text, article > div > div > p strong::text, article > div > div > p a::text, article > div > div > ul li::text, article > div > div > ul a::text').extract()).replace('\n', '').strip()

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
