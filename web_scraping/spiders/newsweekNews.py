# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date


class NewsweeknewsSpider(scrapy.Spider):
    name = 'newsweekNews'
    allowed_domains = ['newsweek.com']
    start_urls = ['https://www.newsweek.com/tech-science/']

    base_url = 'https://www.newsweek.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_links = response.css('h3 > a::attr(href)').extract()
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Newsweek'

        items['link'] = response.url

        d = response.css('time::attr(datetime)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('.article-content div[class="article-body v_text"] > p::text, .article-content div[class="article-body v_text"] > p a::text, .article-content div[class="article-body v_text"] > p em::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
