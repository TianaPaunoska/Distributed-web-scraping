import argparse
from twisted.internet import reactor
from twisted.internet.defer import DeferredList
from scrapyd_api import ScrapydAPI
from spiders.bookspider import BookspiderSpider
from spiders.spider2 import Spider2
from spiders.spider3 import Spider3


SPIDER_NAMES = ['bookspider', 'spider2', 'spider3']


if __name__ == '__main__':
     parser = argparse.ArgumentParser()
     parser.add_argument('--project', required=True, help='web_scraping')
     args = parser.parse_args()

     scrapyd = ScrapydAPI('http://localhost:6800')
     deferreds = []

     for spider_name in SPIDER_NAMES:
          deferred = scrapyd.schedule(args.project, spider_name)
          deferreds.append(deferred)

     dl = DeferredList(deferreds)
     dl.addBoth(lambda _: reactor.stop())

     reactor.run()