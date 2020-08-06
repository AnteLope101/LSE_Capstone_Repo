# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class WirednewsSpider(scrapy.Spider):
    name = 'wiredNews'
    allowed_domains = ['wired.com']
    start_urls = ['https://www.wired.com/category/science/']

    base_url = 'https://www.wired.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.xpath("//div[@class='cards-component']//div[@class='cards-component__row']//a/@href").extract()
        all_links = list(set(all_links))
        all_links = [i for i in all_links if i.startswith('/story')]

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Wired'

        items['link'] = response.url

        date_published = response.css('.content-header__title-block-publish-date::text')[0].extract()
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('.content-header__hed::text')[0].extract()
        body = ' '.join(response.css('div[class="grid--item body body__container article__body grid-layout__content"] > p::text, div[class="grid--item body body__container article__body grid-layout__content"] > p > em::text, div[class="grid--item body body__container article__body grid-layout__content"] > p > a::text, div[class="grid--item body body__container article__body grid-layout__content"] > p > em > a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
