# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter


class LatimesnewsSpider(scrapy.Spider):
    name = 'latimesNews'
    allowed_domains = ['latimes.com']
    start_urls = ['https://www.latimes.com/science/']

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        all_urls = response.css('.TwoColumnContainer7030-row a::attr(href)').extract()
        all_urls = [i for i in all_urls if '/story' in i]
        all_urls = list(set(all_urls))

        for url in all_urls:
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'Los Angeles Times'

        items['link'] = response.url

        d = response.css('.ArticlePage-datePublished-day::text').extract()
        if not d:
            dd = response.css('.LongFormPage-datePublished-day::text').extract()
            if not dd:
                date_published = response.css('.StoryStackPage-datePublished-day::text')[0].extract()
            else:
                date_published = dd[0]
        else:
            date_published = d[0]
        date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        title = response.css('h1::text')[0].extract().replace('\n','').strip()
        body = ' '.join(response.css('div[class="RichTextArticleBody-body RichTextBody"] > p::text, div[class="RichTextArticleBody-body RichTextBody"] > p > a::text, div[class="RichTextArticleBody-body RichTextBody"] > p em::text').extract()).replace('\n','')
        if not body:
            body = ' '.join(response.css('div[class="StoryStackItem-body RichTextBody"] > p::text, div[class="StoryStackItem-body RichTextBody"] > p > a::text, div[class="StoryStackItem-body RichTextBody"] > p em::text').extract()).replace('\n','')
        
        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items


