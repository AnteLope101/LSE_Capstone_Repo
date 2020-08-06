# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class NytnewsSpider(scrapy.Spider):
    name = 'nytNews'
    allowed_domains = ['nytimes.com']
    start_urls = ['https://www.nytimes.com/section/science/']

    base_url = 'https://www.nytimes.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        top_links = response.css('ol[class="css-1i4ie59 ekkqrpp2"] > li a::attr(href)').extract()
        top_links = list(set(top_links))

        latest_links = response.css('div[class="css-13mho3u"] a::attr(href)').extract() 
        latest_links = [i for i in latest_links if i.startswith("/2020")]

        all_links = top_links + latest_links
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'New York Times'

        items['link'] = response.url
        
        dates = response.css('time::text').extract()
        if len(dates) > 0:
            for i in dates:
                if '2020' in i:
                    date_published = i
        else:
            date_published = response.css('time > div > span::text')[0].extract() 
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        t = response.css('h1 span::text').extract()
        if not t:
            title = response.css('h1::text')[0].extract() 
        else:
            title = t[0]
        body = " ".join(response.css('section[itemprop="articleBody"] p::text, section[itemprop="articleBody"] p>a::text').extract()) 
   
        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
