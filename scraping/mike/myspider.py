import scrapy

class WikipediaSpider(scrapy.Spider):
    name = "wikipedia"
    start_urls = [
        'https://en.wikipedia.org/wiki/LinkedIn',
    ]
    
    custom_settings = {
        'DEPTH_LIMIT': 1, # Maximum depth to follow links
        'ROBOTSTXT_OBEY': True,
    }
    
    def parse(self, response):
        title = response.css('h1::text').get()
        table_rows = response.xpath('//*[@id="mw-content-text"]/div/table[2]/*/tr')
        table_data = [
            (''.join(tr.xpath('th//text()').getall()), ''.join(tr.xpath('td//text()').getall()))
            for tr in table_rows]
        self.log('Number of rows: %s ' % len(table_rows.getall()))
        self.log('Scraped  %s' % response.url)
        
        # Gets wiki links inside of the main content of the page
        wiki_links = response.xpath("//*/div[starts-with(@id, 'content')]//*/a[starts-with(@href, '/wiki')]")
        for link in wiki_links:
            # print(link.attrib['href'])
            yield response.follow(link)
        
        yield {
            # 'html': response.body.decode(),
            'table_data': table_data,
            'title': title,
            }