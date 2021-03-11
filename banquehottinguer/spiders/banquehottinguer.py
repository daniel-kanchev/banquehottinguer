import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from banquehottinguer.items import Article


class BanquehottinguerSpider(scrapy.Spider):
    name = 'banquehottinguer'
    start_urls = ['https://blog.banque-hottinguer.com/2015/10/27/communique-de-presse-du-27-10-2015/']

    def parse(self, response):
        yield response.follow(response.url, self.parse_article, dont_filter=True)
        next_page = response.xpath('//a[@rel="next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//time/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="entry-content"]/*[not(self::div)]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
