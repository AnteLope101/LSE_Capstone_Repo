# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class ScitechdailynewsSpider(scrapy.Spider):
    name = 'scitechdailyNews'
    allowed_domains = ['scitechdaily.com']
    start_urls = ['https://scitechdaily.com/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        lead_url = response.css('h3[class="entry-title content-lead-title"] > a::attr(href)').extract()

        grid_urls = response.css('h3[class="entry-title content-grid-title"] > a::attr(href)').extract()

        list_urls = response.css('h3[class="entry-title content-list-title"] > a::attr(href)').extract()

        all_urls = lead_url + grid_urls + list_urls
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'SciTechDaily'

        items['link'] = response.url

        date_published = response.css('span[class="entry-meta-date updated"]::text')[0].extract()
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract().replace('\n','')
        body = ' '.join(response.css('div[class="entry-content clearfix"] > p::text, div[class="entry-content clearfix"] > p > strong::text, div[class="entry-content clearfix"] > p > em::text, div[class="entry-content clearfix"] > p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
