import scrapy

class WikipediaSpider(scrapy.Spider):
    name = "wikipedia"
    start_urls = [
        'https://en.wikipedia.org/wiki/LinkedIn',
    ]
    
    def parse(self, response):
        title = response.css('h1::text').get()
        table_rows = response.xpath('//*[@id="mw-content-text"]/div/table[2]/*/tr')
        table_data = [
            (''.join(tr.xpath('th//text()').getall()), ''.join(tr.xpath('td//text()').getall()))
            for tr in table_rows]
        self.log('Number of rows: %s ' % len(table_rows.getall()))
        self.log('Scraped  %s' % response.url)
        yield {
            'html': response.body,
            'table_data': table_data,
            'title': title,
            }