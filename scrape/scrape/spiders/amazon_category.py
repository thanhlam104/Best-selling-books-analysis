import scrapy
import pandas as pd
from scrapy import Request


class AmazonBookYearSpider(scrapy.Spider):
    name = 'amazon_category'
    allow_domains = ['https://www.amazon.com']
    start_urls = pd.read_csv('links.csv')['link'].to_list()


    def start_requests(self):
        for url in self.start_urls:
            if url not in ['', None]:
                try: 
                    yield Request(url, callback=self.parse_category)
                except:
                    pass

    def parse_category(self, response):
        categories = response.css('.a-link-normal.a-color-tertiary::text').getall()
        categories = [i.strip() for i in categories]
        category = '/'.join(categories)

        yield{
            'ASIN': response.url.split('/')[-1] if response.url else None,
            'category': category,
        }

 