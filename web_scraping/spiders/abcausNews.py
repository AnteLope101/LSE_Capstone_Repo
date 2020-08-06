# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class AbcausnewsSpider(scrapy.Spider):
    name = 'abcausNews'
    allowed_domains = ['abc.net.au']
    start_urls = ['https://www.abc.net.au/news/science//','https://www.abc.net.au/news/technology//']

    base_url = 'https://www.abc.net.au'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('.row > div > a::attr(href)').extract()
        if all_links:   # science news
            all_links = [i for i in all_links if '/news' in i]
        else:
            top_links = response.css('.doctype-article > h3 > a::attr(href)').extract()
            more_links = response.css('.article-index > li > a::attr(href)').extract()

            all_links = top_links + more_links
            all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'ABC News'

        items['link'] = response.url
        
        dates = response.css('time::attr(datetime)').extract()
        if not dates:
            date_published = response.css('.timestamp::text')[0].extract().replace('\n', '')
        else:
            date_published = dates[0]
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        titles = response.css('h1::text').extract()
        titles = [i for i in titles if 'Technology News' not in i]
        titles = [i for i in titles if 'Science' not in i]
        title =  titles[0]
        body = " ".join(response.css('div[itemprop="text"] > p::text, div[itemprop="text"] > p > a::text').extract())
        if not body:
            body = " ".join(" ".join(response.css("div[class='article section'] > p::text, div[class='article section'] > p:not([class='topics']) > a::text").extract()).split())
   
        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
