"""
The spider for reuters.

TODO:
- Parse raw date.

"""

from datetime import datetime
import re

from nltk.tokenize import WordPunctTokenizer as WPTker

from scrapy.spider import Spider
from scrapy.http import Request

from ScraReuters.items import NewsItem
from ScraReuters import company

from bs4 import BeautifulSoup


class MediaType:
    """The base type of wire media"""
    def __init__(self, name, re):
        self.name = name
        self.re = re

    def check(self, url):
        return self.re.search(url) != None

PRN_REG = re.compile('\+PRN\d{8}')
BW_REG = re.compile('\+BW\d{8}')
MW_REG = re.compile('\+MW\d{8}')
GNW_REG = re.compile('\+GNW\d{8}')


class PRN(MediaType):
    def __init__(self):
        MediaType.__init__(self, 'PRN', PRN_REG)


class BW(MediaType):
    def __init__(self):
        MediaType.__init__(self, 'BW', BW_REG)


class MW(MediaType):
    def __init__(self):
        MediaType.__init__(self, 'MW', MW_REG)


class GNW(MediaType):
    def __init__(self):
        MediaType.__init__(self, 'GNW', GNW_REG)

MEDIA_FILTERS = [PRN(), BW(), MW(), GNW()]


def is_wire(url):
    """Checks if a URL is a type of wire media"""
    for filter in MEDIA_FILTERS:
        if filter.check(url):
            print url
            return True
    return False

tker = WPTker()


def normalize_title(title):
    title = re.sub('Reuters', '', title)
    title = re.sub('\|', '', title)
    tokens = [e.lower() for e in tker.tokenize(title)]
    return ' '.join(tokens)
    

class ReutersSpider(Spider):
    name = 'ReutersSpider'
    allowed_domains = ['reuters.com']

    def __init__(self, year, month, day):
        year, month, day = [int(e) for e in [year, month, day]]
        self.date = datetime(year, month, day)
        self.start_urls = ['http://www.reuters.com/resources/archive/us/%4d%02d%02d.html' % (year, month, day)]
        self.is_index = True

    def parse(self, response):
        if self.is_index:
            return self.parse_index(response)
        else:
            return self.parse_news(response)

    def parse_index(self, response):
        """Parses the index page"""
        self.is_index = False

        self.titles = {}
        for target in response.xpath('//div[@class="headlineMed"]'):
            try:
                title = normalize_title(target.xpath('a/text()').extract()[0])
                link = target.xpath('a/@href').extract()[0]
                #str_time = item.select('text()').extract()[0][1:]
                #time = parse(str_time)
                if 'C O R R E C T I O N' in title or title in self.titles:
                    continue

                if link.startswith('http://www.reuters.com/news/video/'):
                    continue

                self.titles[title] = link
                yield Request(link, callback=self.parse_news)

            except Exception as e:
                print e

    @staticmethod
    def find_symbols(body):
        """
        Extract the related symbols in the news.

        e.g. The script in the html is like
        <script type="text/javascript">
                Reuters.info.sRelatedStocks = 'VOD.L,LAND.L,RBS.L,LSE.L,NDAQ.O';
        </script>
        """
        raw_symbols = re.findall('Reuters.info.sRelatedStocks = \'([\w\.\,\d]+)\';', body)
        if len(raw_symbols) > 0:
            return raw_symbols[0].split(',')
        else:
            return []

    def parse_news(self, response):
        """Parse news pages"""
        print '.',
        #hxs = HtmlXPathSelector(response)
        item = NewsItem()
        raw_title = response.xpath('//title/text()').extract()[0]
        item['title'] = normalize_title(raw_title)
        item['link'] = response.url
        
        # # Find symbols from the page
        # # item['symbols'] = ReutersSpider.find_symbols(response.body)
        # item['symbols'] = company.get_symbols_in_title(item['title'])
        #
        # # FIXME: debug
        # if len(item['symbols'])>0:
        #     print '\n\t', item['title'], item['symbols']
        #
        # # Return None if no symbol is found
        # """if not len(item['symbols'])>0:
        #     return"""
        
        # Get sectors from the page
        sectors = []
        for li in response.css('.related-topics span:nth-child(2)'):
            sectors.append(li.xpath('a/text()').extract())
        item['sectors'] = sectors

        # Get text from the page
        item['text'] = ''
        for target in response.xpath('//span[@id="articleText"]'):

            for p in target.xpath('.//pre | .//p'):
                raw_text = p.extract()
                soup = BeautifulSoup(raw_text)
                item['text'] += soup.get_text()
        
        raw_date = response.xpath('//div[@class="article-header"]/span[@class="timestamp"]/text()').extract()[0]
        dt_obj = datetime.strptime(raw_date, "%a %b %d, %Y %I:%M%p %Z")
        item['date'] = dt_obj.strftime('%H:%M %d %B %Y (UTC)')
        
        return item
