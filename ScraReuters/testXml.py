__author__ = 'shadowtrader'
import json
import urllib
from bs4 import BeautifulSoup

with open('../reuters/20150527.json', 'r') as f:
    stories = json.load(f)

DOC = """<item>
  <headline></headline>
  <body></body>
  <date></date>
  <link></link>
</item>"""

i = 0
for s in stories:
    soup = BeautifulSoup(DOC, features='xml')
    soup.headline.append(s['title'])
    soup.body.append(s['text'])
    soup.date.append(s['date'])
    soup.link.append(s['link'])
    t = soup.prettify().replace('<body>', '<text>').replace('</body>', '</text>')
    i += 1
    with open('../reuters/export/{}.xml'.format(i), 'w') as f:
        f.write(t.encode('utf-8'))



