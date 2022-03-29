import scrapy
from scrapy import Request
from scrapy_splash import SplashRequest


class AmazonBookYearSpider(scrapy.Spider):
    name = 'amazon_raw'
    allow_domains = ['https://www.amazon.com']
    start_urls = ['https://www.amazon.com/gp/bestsellers/1997/books/']

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse_by_year)

    def parse_by_year(self, response):
        year_slt = response.css('div#zg_bsarCalendar a')
        yield from response.follow_all(year_slt,callback = self.parse_book)

    def parse_book(self, response):
        book_slt = response.css('li.zg-item-immersion')
        if book_slt is not None:
            for book in book_slt:
                if book.css('span>.a-link-normal::attr(href)') != None:
                    book_href = 'https://www.amazon.com' + book.css('span>.a-link-normal::attr(href)').get()  
                yield {
                    'year': response.css('.zg_selected a::text').get(),
                    'order': book.css('.zg-badge-text::text').get(),
                    'name': book.css('.p13n-sc-truncate::text').get().strip() if book.css('.p13n-sc-truncate::text') else None,
                    'ASIN': book_href.split('/')[-1].split('?')[0] if book_href else None,
                    'book_href': book_href,
                    'author': book.css('.a-size-small .a-link-child::text').get() if book.css('.a-size-small .a-link-child::text') else book.css('.a-size-small .a-color-base::text').get(),
                    'author_href': 'https://www.amazon.com' + book.css('.a-size-small .a-link-child::attr(href)').get() if book.css('.a-size-small .a-link-child::attr(href)') else None,
                    'rating': book.css('.a-icon-alt::text').get(),
                    'review': book.css('a + a.a-size-small::text').get(),
                    'type': book.css('.a-size-small .a-color-secondary::text').get(),
                    'price': book.css('.p13n-sc-price::text').get(),
                    'category': None
                }

            next_year = response.css('.a-last ::attr(href)').get()
            if next_year is not None:
                yield response.follow(next_year, callback = self.parse_book)

