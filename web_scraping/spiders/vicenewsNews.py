# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date


class VicenewsnewsSpider(scrapy.Spider):
    name = 'vicenewsNews'
    allowed_domains = ['vice.com']
    start_urls = ['https://www.vice.com/en_us/section/tech/']

    base_url = 'https://www.vice.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        top_links = response.css('.sections-card__heading-link::attr(href)').extract()

        list_links = response.css('.heading-hover::attr(href)').extract()

        all_links = top_links + list_links
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Vice News'

        items['link'] = response.url

        d = response.css('div[class="article-heading-v2__formatted-date dsp-inline--xs"]::text').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('div[class="article__body article__body dsp-block-xx ff--body-article size--article lh--body"] > p::text, div[class="article__body article__body dsp-block-xx ff--body-article size--article lh--body"] > p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
