# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date
from dateutil import parser


class PopscinewsSpider(scrapy.Spider):
    name = 'popsciNews'
    allowed_domains = ['popsci.com']
    start_urls = ['https://www.popsci.com//']

    base_url = 'https://www.popsci.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        col1_links = response.css('div[class="column_one "] > ul > li > div > a::attr(href)').extract()

        col2_links = response.css('div[class="column_two"] > ul > li > div > a::attr(href)').extract()

        other_links = response.css('div[class="flex-feature | container container_column--desktop "] > a::attr(href)').extract()

        box_links = response.css('div[class="envelope-container"] a::attr(href)').extract()

        all_links = col1_links + col2_links + other_links + box_links
        all_links = list(set(all_links))
        all_links = [i for i in all_links if '/story' in i]

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Popular Science'

        items['link'] = response.url

        date_published = response.css('span[class="article_byline | align_items_center--mobile container_column container_row--desktop flex italic justify_center padding_bottom_sm--mobile text_align_center align_items_center"] > span::text')[0].extract()
        if 'ago' in date_published:
            date_published = date.today().strftime("%d-%b-%Y")
        elif 'Updated' in date_published:
            date_published = parser.parse(date_published, fuzzy=True, ignoretz=True).strftime("%d-%b-%Y")
        else:
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract().strip()
        body = ' '.join(response.css('div[id="article-body"] > div > section > div > p::text, div[id="article-body"] p > i::text, div[id="article-body"] p > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items

