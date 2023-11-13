import asyncio
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.bookspider import BookspiderSpider
from scrapy_redis import get_redis
from twisted.internet import asyncioreactor

# Set the default event loop policy
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Set the asyncio reactor
asyncioreactor.install(asyncio.get_event_loop())

# Create a CrawlerProcess instance
process = CrawlerProcess(get_project_settings())

# Connect to Redis
redis_conn = get_redis()

# Create multiple instances of your spider classes
spiders = [
    BookspiderSpider,
    BookspiderSpider
]

# Generate start URLs dynamically
start_urls = []
for i in range(1, 51):
    url = f'https://books.toscrape.com/catalogue/page-{i}.html'
    start_urls.append(url)

# Clear existing URLs in Redis queue
for spider_class in spiders:
    redis_conn.delete(f'{spider_class.name}:start_urls')

# Push start URLs to Redis queue
for spider_class in spiders:
    redis_conn.rpush(f'{spider_class.name}:start_urls', *start_urls)

# Start each spider in the process
for spider_class in spiders:
    process.crawl(spider_class, name=spider_class.name, redis_conn=redis_conn)

# Start the process
process.start()
