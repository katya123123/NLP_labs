import scrapy
from .lib import DB_link


class GoldenSpider(scrapy.Spider):
    name = "golden"
    allowed_domains = ["goldenmost.ru"]
    start_urls = ["https://goldenmost.ru/"]

    pagin_url = 'https://goldenmost.ru/category/politica/'
    
    page = 800
    cnt = 30

    saver = None

    def start_requests(self):
        self.saver = DB_link(self.name)
        self.saver.InitDir()
        self.saver.InitDB()

        yield scrapy.Request(
            self.pagin_url,
            callback=self.pagin_parser
        )


    def pagin_parser(self, response):
        article_urls = response.xpath('//section/div/div/section/div/div/h2/a/@href').getall()

        for url in article_urls:
            
            yield scrapy.Request(
                url,
                callback=self.article_parser
            )

        next_page = response.xpath('//a[@class="btn btn-default posts-nav"]')[-1]
        next_page = next_page.xpath('@href').get() if 'Следующая страница' in next_page.get() else None

        if next_page:
            yield scrapy.Request(
                next_page,
                callback=self.pagin_parser
            )

    def article_parser(self, response):

        tags = response.xpath('//div[@class="d-flex flex-wrap"]/div/a/text()').getall()
        tags = ';'.join(tags)

        title = response.xpath('//h1/text()').get()
        
        content = response.xpath('//article[@class="col-12"]/p/text()').getall()
        content = ''.join(content).replace('\t', '').replace('\n', '').replace('\r', '').strip()

        date = response.xpath('//div[@class="time mb-2 mb-lg-0 mr-2 d-flex align-items-center ml-0"]/span/text()').get()
        
        instance = (title, content, tags, date)
        self.saver.AddToDB(instance)

        