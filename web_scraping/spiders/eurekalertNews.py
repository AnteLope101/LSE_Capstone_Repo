# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class EurekalertnewsSpider(scrapy.Spider):
    name = 'eurekalertNews'
    allowed_domains = ['eurekalert.org']
    start_urls = ['https://www.eurekalert.org//']

    base_url = 'https://www.eurekalert.org'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        most_links = response.css('div[class="row"] a::attr(href)').extract() 
        most_links = [i for i in most_links if '/pub_releases' in i]

        other_links = response.css('ul[class="article-links"] a::attr(href)').extract()

        all_links = most_links + other_links
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'EurekAlert!'

        items['link'] = response.url

        date_published = response.css('div[class="release_date"] > time::text')[0].extract()
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract().replace('\n','').strip()
        body =  ' '.join(response.css('div[class="entry"] > p::text, div[class="entry"] > p > a::text, div[class="entry"] > p > em::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
