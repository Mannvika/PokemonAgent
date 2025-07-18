from pathlib import Path
import scrapy

class PokemonCrawler(scrapy.Spider):
    name = 'pokemon'

    start_urls = [
        'https://bulbapedia.bulbagarden.net/wiki/List_of_cities_and_towns',
    ]
        
    def parse(self, response):
        print(f"Parsing URL: {response.url}")
        for url in response.css('table.sortable td:first-child a::attr(href)').getall():
            print(f"Found URL: {url}")
            if url.startswith('/wiki/') and not url.startswith('/wiki/File:'):
                print(f"Following URL: {url}")
                yield response.follow(url, self.parse_lore)
    
    def parse_lore(self, response):
        title = response.css("span.mw-page-title-main::text").get()
        
        lore_paragraphs = response.xpath('//h2[1]/preceding-sibling::p').css('::text').getall()
        
        lore_text = ' '.join(p.strip() for p in lore_paragraphs).strip()
        
        yield {
            'title': title,
            'lore': lore_text,
        }


