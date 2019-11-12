import scrapy

class WikipediaSpider(scrapy.Spider):
    name = "wikipedia"
    start_urls = [
        'https://en.wikipedia.org/wiki/LinkedIn',
        # Competitors
        'https://en.wikipedia.org/wiki/Viadeo',
        'https://en.wikipedia.org/wiki/XING',
        'https://en.wikipedia.org/wiki/Glassdoor',
        # Acquisitions
        'https://en.wikipedia.org/wiki/Drawbridge_(company)',
        'https://en.wikipedia.org/wiki/SlideShare',
        'https://en.wikipedia.org/wiki/Bright.com',
        'https://en.wikipedia.org/wiki/LinkedIn_Pulse',
    ]
    
    custom_settings = {
        'DEPTH_LIMIT': 1, # Maximum depth to follow links
        'ROBOTSTXT_OBEY': True,
    }
    
    def parse(self, response):
        title = response.css('h1::text').get()
        table_rows = response.xpath('//*[@id="mw-content-text"]/div/table[2]/*/tr')
        table_data = [
            (tr.xpath('th//text()').getall(), tr.xpath('td//text()').getall())
            for tr in table_rows]
        self.log('Number of rows: %s ' % len(table_rows.getall()))
        self.log('Scraped  %s' % response.url)
        
        # Gets wiki links inside of the main content of the page
        wiki_links = response.xpath("//*/div[starts-with(@id, 'content')]//*/a[starts-with(@href, '/wiki')]")
        for link in wiki_links:
            # print(link.attrib['href'])
            yield response.follow(link)
        
        yield {
            'html': response.body.decode(),
            'table_data': table_data,
            'title': title,
            }