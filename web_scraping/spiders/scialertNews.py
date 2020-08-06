# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class ScialertnewsSpider(scrapy.Spider):
    name = 'scialertNews'
    allowed_domains = ['sciencealert.com']
    start_urls = ['https://www.sciencealert.com//']

    base_url = 'https://www.sciencealert.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('.titletext > a::attr(href)').extract()
        all_links = list(set(all_links))

        # create urls
        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'ScienceAlert'

        items['link'] = response.url

        date = response.css('div[class="author-name-date floatstyle"] > span::text').extract()
        if not date:
            date_published = response.css('div[class="author-name-name"] > span::text')[1].extract()
        else:
            date_published = date[0]
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract().replace('\n','') 
        body = ' '.join(response.css('.article-fulltext > p::text, .article-fulltext > p > a::text, .article-fulltext > p em::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
