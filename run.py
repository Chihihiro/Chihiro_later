import os
from scrapy import cmdline

# cmdline.execute("scrapy crawl nihongo".split())

from scrapy.cmdline import execute

spiders = [
    'scrapy crawl nihongo',

]

if __name__ == '__main__':
    for i in spiders:
        execute('scrapy crawl nihongo'.split())