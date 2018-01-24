import requests
from lxml import html
import datetime
import numpy as np
import pandas as pd

def get_allTickers():
    data = pd.read_csv("tickersList.csv")
    data =  (data['Symbol'].tolist())
    return data

myList = []
Required_date = (datetime.datetime.now() - datetime.timedelta(days=5)).date()
for each in get_allTickers():
	url = 'https://www.reuters.com/finance/stocks/insider-trading/'+each+'.O'
	try:
		page = requests.get(url)
		tree = html.fromstring(page.content)
		lastDate = tree.xpath('//tr[@class="dataSmall stripe"]/td/text()')[0]
		orderType = (tree.xpath('//tr[@class="dataSmall stripe"]/td/text()')[2]).strip()
		lastDate = datetime.datetime.strptime(lastDate, '%d %b %Y').date()
		if lastDate >= Required_date:
			myList.append((each,orderType))
	except:
		pass
print(myList)