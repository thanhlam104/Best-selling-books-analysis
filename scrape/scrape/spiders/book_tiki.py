# using Docker(have Splash image installed inside also), 
# run by go to project file directory, type 'scrapy crawl book_tiki' on terminal
import scrapy
from scrapy import exceptions
import json
import pandas as pd

#run and debug as script
from scrapy import Request
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerRunner

class BookSpider(scrapy.Spider):
    name = 'tiki'
    start_url = 'https://tiki.vn/bestsellers/nha-sach-tiki/c8322?'
    start_urls = ['https://tiki.vn/bestsellers/sach-truyen-tieng-viet/c316',
                'https://tiki.vn/bestsellers/sach-tieng-anh/c320']
    
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url,callback=self.parse_by_year)




    def parse_by_year(self, response):
        for year_slt in response.xpath('//div[@class = "bestseller-nav"][1]//li//@href')[2:]:
            yield response.follow(year_slt.get(), callback= self.parse_by_page)

    def parse_by_page(self, response):
        pages_slt = response.xpath('//div[@class = "bestseller-nav"][1]/div//@href')
        if pages_slt == []: #For those pages dont't have 
            yield from self.parse_book(response )
        else: 
            for page_slt in pages_slt:
                yield response.follow(page_slt.get(), callback= self.parse_book)    
            
    def parse_book(self, response):
        #get book content
        books_selector = response.xpath('//*[@class = "bestseller-cat-item"]')
        for book_selector in books_selector:
            #handle the rating
            try:
                rating_selector = round(float(book_selector.xpath('.//p[@class = "rating"]//@style').get()[6:].strip('%'))/20,2)
            except(TypeError):
                rating_selector = None
            #handle the data-id
            href = book_selector.xpath('.//p[@class = "title"]//@href').get()
            year = response.xpath('//li/a[@class = "active"]/text()').get()
            def findID(href):
                i = -26 #place where '.html?src....'
                id = ''
                while href[i].isdigit():
                    id+=href[i]
                    i-=1
                return id[::-1]
            yield {
                    # 'current-category': response.xpath('//li/a[@class = "active"]/text()').get().strip(),
                    'title-best-seller': response.xpath('//div[@class="bestseller-cat-title"]//text()').getall()[1].strip(),
                    'category': book_selector.xpath('./@data-category').get(),
                    'year' :    year if year else 2015, # The 2015 year doesn't have @class = active
                    'order':    book_selector.xpath('.//*[@class= "number"]/text()').get().strip(),
                    'id':       findID(href),
                    'href':     href,
                    'name':     book_selector.xpath('./@data-title').get(),
                    # 'price-sale': book_selector.xpath('.//p[@class ="price-sale"]/text()[1]').get().strip(),
                    'price':    book_selector.xpath('./@data-price').get(),
                    'author':   book_selector.xpath('./@data-brand').get(),            
                    'rating':   rating_selector,    #the width of rating star
                    'review_count': book_selector.xpath('.//*[@class = "review"]/text()').get()
                    }
            # self.df = self.df.append(book, ignore_index = True)







# process = CrawlerProcess(get_project_settings())
# process.crawl(BookSpider)
# process.start()
# configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
# runner = CrawlerRunner()

# d = runner.crawl(BookSpider)
# d.addBoth(lambda _: reactor.stop())
# reactor.run() # the script will block here until the crawling is finished