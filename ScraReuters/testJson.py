import json
from bs4 import BeautifulSoup

i = 0
with open('iptc1.json', 'r') as f:
    stories = json.load(f)
    for line in stories:
        soup = BeautifulSoup(line["message"])
        print soup.get_text()
        i += 1
        with open('{}.json'.format(i), 'w') as fb:
            json.dump(soup.get_text(), fb)
