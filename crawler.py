from pathlib import Path
import scrapy as sc

class PokemonCrawler(sc.Spider):
    name = 'pokemon'

    async def start(self):
        self.start_urls = [
            'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number',
            'https://bulbapedia.bulbagarden.net/wiki/List_of_cities_and_townsr',
            'https://bulbapedia.bulbagarden.net/wiki/List_of_cross-canon_references'
            'https://bulbapedia.bulbagarden.net/wiki/List_of_cross-generational_references'
        ]
        
        for url in urls:
            yield sc.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"pokemons-{page}.html"
        Path('data').mkdir(parents=True, exist_ok=True)
        self.log(f'Saving page {page} to {filename}')