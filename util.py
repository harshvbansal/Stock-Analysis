#code from https://github.com/bradlucas/get-yahoo-quotes-python
import pandas as pd
import matplotlib.pyplot as plt
import re
import sys
import time
import datetime
import requests
import pandas as pd

def split_crumb_store(v):
    return v.split(':')[2].strip('"')

def find_crumb_store(lines):
    # Looking for
    # ,"CrumbStore":{"crumb":"9q.A4D1c.b9
    for l in lines:
        if re.findall(r'CrumbStore', l):
            return l
    print("Did not find CrumbStore")


def get_cookie_value(r):
    return {'B': r.cookies['B']}


def get_page_data(symbol):
    url = "https://finance.yahoo.com/quote/%s/?p=%s" % (symbol, symbol)
    r = requests.get(url)
    cookie = get_cookie_value(r)

    # Code to replace possible \u002F value
    # ,"CrumbStore":{"crumb":"FWP\u002F5EFll3U"
    # FWP\u002F5EFll3U
    lines = r.content.decode('unicode-escape').strip(). replace('}', '\n')
    return cookie, lines.split('\n')


def get_cookie_crumb(symbol):
    cookie, lines = get_page_data(symbol)
    crumb = split_crumb_store(find_crumb_store(lines))
    return cookie, crumb


def get_data(symbol, start_date, end_date, cookie, crumb):
    filename = 'data/%s.csv' % (symbol)
    url = "https://query1.finance.yahoo.com/v7/finance/download/%s?period1=%s&period2=%s&interval=1d&events=history&crumb=%s" % (symbol, start_date, end_date, crumb)
    response = requests.get(url, cookies=cookie)
    with open (filename, 'wb') as handle:
        for block in response.iter_content(1024):
            handle.write(block)


def get_now_epoch():
    # @see https://www.linuxquestions.org/questions/programming-9/python-datetime-to-epoch-4175520007/#post5244109
    return int(time.time())


def download_quotes(symbol):
    start_date = 0
    end_date = get_now_epoch()
    cookie, crumb = get_cookie_crumb(symbol)
    get_data(symbol, start_date, end_date, cookie, crumb)


def get_SPTickers():
    data = pd.read_csv("SP500.csv")
    return (data.ticker.tolist())

if __name__ == '__main__':
    tickers = get_SPTickers()
    for i in range(0, len(tickers)):
        try:
            symbol = tickers[i]
            print("--------------------------------------------------")
            print("Downloading %s to %s.csv" % (symbol, symbol))
            download_quotes(symbol)
            print("--------------------------------------------------")
        except:
            pass

def get_data(tickers, sd, ed):
    data = pd.DataFrame()
    for ticker in tickers:
        try:
            df = pd.read_csv(("data/{}.csv").format(ticker))
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')
            df = df[sd:ed]['Adj Close']
            df = df.rename(ticker)
            data = pd.concat([data,df],axis = 1)
        except:
            pass
    data = data.dropna(axis=1, how='all')
    return data

def getBollingerBands(data):
    mva20day = pd.stats.moments.rolling_mean(data,20)
    sd20day = pd.stats.moments.rolling_std(data,20)
    lowerBand = mva20day - (sd20day*2)
    upperBand = mva20day + (sd20day*2)
    return lowerBand, upperBand