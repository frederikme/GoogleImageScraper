from scraper import GoogleImageScraper

if __name__ == '__main__':
    scraper = GoogleImageScraper()
    # By default, directory='images' and amount='50'
    scraper.downloadImages(query="Christiano ronaldo", directory='images', amount=30)
