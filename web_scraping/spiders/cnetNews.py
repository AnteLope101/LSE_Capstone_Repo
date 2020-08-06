# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date


class CnetnewsSpider(scrapy.Spider):
    name = 'cnetNews'
    allowed_domains = ['cnet.com']
    start_urls = ['https://www.cnet.com/news//']

    base_url = 'https://www.cnet.com'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        top_links = response.css('.mainStory::attr(href)').extract()

        moretop_links = response.css('div[class="assetBody riverPost"] > a::attr(href)').extract()

        subtop_links = response.css('a[class="related content_article"]::attr(href)').extract()

        righttop_links = response.css('div[class="assetBody dekRight riverPost"] > a::attr(href)').extract()

        latest_links = response.css('h3 > .assetHed::attr(href)').extract()

        all_links = top_links + moretop_links + subtop_links + righttop_links + latest_links
        all_links = [i for i in all_links if '/news' in i]
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'CNET News'

        items['link'] = response.url

        d = response.css('time::attr(datetime)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract()
        body = ' '.join(response.css('div[class="col-7 article-main-body row "] > p::text, div[class="col-7 article-main-body row "] > p a::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
