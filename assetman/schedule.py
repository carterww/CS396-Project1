import datetime
import yfinance as yf
import logging
import schedule
from django.conf import settings
from django.contrib.auth.models import User


from .models import *
from .helpviews import update_model
import os

def update_stock_data() :
    log_text = ''
    stocks = Stock.objects.all()
    log_text += 'OK: Grabbed all stocks from database...\n'

    for stock in stocks :
        # grab stock from database
        yf_stock = yf.Ticker(stock.ticker)
        log_text += f'OK: Currently executing the job on {stock.ticker.upper()}\n'

        # get year's price history
        history = yf_stock.history(period='12mo')
        # grab 52 week high and low
        year_high = history['High'].max()
        year_low = history['Low'].min()
        update_model(stock, {'yearHigh': year_high, 'yearLow': year_low})
        log_text += f'OK: Updated the 52 week high and low\n'


        # grab 1 week history
        history = yf_stock.history(period='5d')

        for index, row in history.iterrows():
            try :
                snapshot = StockSnapshot.objects.get(snapshotDate=index.date(), FK_stock_snapshot=stock)
                log_text += f'SKIPPING: Snapshot with date {index.date():%Y-%m-%d} already exists. Moving on to next row\n'
                break
            except :
                True

            snapshotArgs = {
                'snapshotDate': index.date(),
                'openPrice': row["Open"],
                'closePrice': row["Close"],
                'dayLow': row["Low"],
                'dayHigh': row["High"],
                'volume': row["Volume"],
                'FK_stock_snapshot': stock
            }
            update_model(StockSnapshot(), snapshotArgs)
            log_text += f'OK: Snapshot with date {index.date():%Y-%m-%d} added to database for {stock.ticker.upper()}\n'
    
    # write log to log file

