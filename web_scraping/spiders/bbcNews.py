# -*- coding: utf-8 -*-
import scrapy
from ..items import CapstoneNewsItem
import dateparser
from w3lib.url import url_query_parameter
from datetime import date



class BbcnewsSpider(scrapy.Spider):
    name = 'bbcNews'
    allowed_domains = ['bbc.co.uk']
    start_urls = ['https://www.bbc.co.uk/news/science_and_environment/',
                  'https://www.bbc.co.uk/news/technology/']

    base_url = 'https://www.bbc.co.uk'

    def parse(self, response):
        print("procesing:"+response.url)

        # extract links
        top_link = response.xpath("//a[@class = 'gs-c-promo-heading gs-o-faux-block-link__overlay-link gel-paragon-bold gs-u-mt+ nw-o-link-split__anchor']/@href").extract()

        other_links = response.css('a[class="gs-c-promo-heading gs-o-faux-block-link__overlay-link gel-pica-bold nw-o-link-split__anchor"]::attr(href)').extract()

        list_links = response.css('a[class="qa-heading-link lx-stream-post__header-link"]::attr(href)').extract()

        # create urls
        all_links = top_link + other_links + list_links
        all_links = [i for i in all_links if '/news/' in i and '/av/' not in i]
        all_links = list(set(all_links))

        for link in all_links:
            url = self.base_url + link
            yield scrapy.Request(url, meta={'deltafetch_key': url_query_parameter(url, 'id')}, callback=self.parse_attr)


    def parse_attr(self, response):
        print("procesing:"+response.url)

        items = CapstoneNewsItem()
        items['source'] = 'BBC'

        items['link'] = response.url

        d = response.css('.mini-info-list__item > div::attr(data-datetime)').extract()
        if not d:
            date_published = date.today().strftime("%d-%b-%Y")
        else:
            date_published = d[0]
            date_published = dateparser.parse(date_published).date().strftime("%d-%b-%Y")
        t = response.css('h1.story-body__h1::text').extract()
        if not t:
            title = response.css('h1::text')[0].extract()
        else:
            title = t[0]
        body = ' '.join(response.css('.story-body__inner > p::text, .story-body__inner > p > a::text').extract())
        if not body:
            body = ' '.join(response.css('.vxp-media__summary > p::text, .vxp-media__summary > p a::text, .vxp-media__summary > p em::text').extract())

        items['date_published'] = date_published
        items['title'] = title
        items['article'] = body
        
        yield items
