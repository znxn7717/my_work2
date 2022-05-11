import time
import pandas as pd
import pandas_ta as ta
import ccxt

""" This bot gett User (private) , Trade (private) and Market Data (public). """

# # # API request section

''' exchange setting (znxn8585@gmail.com is sandbox) '''
# exchange = ccxt.kucoinfutures({
#     "apiKey": ,
#     "secret": ,
#     "password":
# })
exchange = ccxt.kucoin()
while True:
    ''' function send REST API (or Websocket Feed) request to (GET)ting data for candles chart '''
    def get_ohlcv(sym, tf, bar):

        ''' make a table with this column headers '''
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

        ''' ccxt's function send request to get candles data from exchange '''
        candles = exchange.fetch_ohlcv(symbol=sym, timeframe=tf, limit=bar)

        ''' panda's function convert list of list to pandas dataframe and put it in made table '''
        df = pd.DataFrame(data=candles, columns=columns)

        ''' panda's function convert millisecond unix timestamp to pandas datetime timestamp '''
        df['timestamp'] = pd.to_datetime(arg=df['timestamp'], unit='ms')

        return df

    ''' function send REST API (or Websocket Feed) request to (GET)ting data for indicators chart '''
    def iget_ohlcv(sym, tf, bar):
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        candles = exchange.fetch_ohlcv(symbol=sym, timeframe=tf, limit=bar)
        df = pd.DataFrame(data=candles, columns=columns)
        df['timestamp'] = pd.to_datetime(arg=df['timestamp'], unit='ms')
        return df

# # # chart and strategy section

    ''' used to execute code only if the main.py file was run directly, and not imported '''
    if __name__ == '__main__':

        ''' chart and indicator settings (notice: xxx-xxx symbol format is for Kucoin exchange API only) '''
        symbol = 'BTC-USDT'
        bar = 300
        timeframe = '3m'
        quantity = 1.0
        cdataframe = get_ohlcv(symbol, timeframe, bar)

        ''' option to set separately timeframe for indicator (but defval=chart timaframe) '''
        itimeframe = timeframe
        idataframe = iget_ohlcv(symbol, itimeframe, bar)

        ''' run sleep time calculating (second) '''
        sleep_time = int(timeframe[:-1])*60

        ''' start calculation operation '''
        print('\n\n\n\n')
        msg = ' bot is started! '
        new_msg = msg.center(70, '*')
        print(new_msg)
        print('\n')
        
        ''' the bot must be idle by default '''
        long_position = False
        short_position = False

        ''' take last candle (notice: last indexed candle is open yet. we need the last closed candle for following) '''
        last_row = len(cdataframe.index) - 2
        last_closed_candle_cprice = cdataframe['close'][last_row]
        last_closed_candle_time = cdataframe['timestamp'][last_row]

        ''' calculate some indicator for strategy by panda_ta's function and add columns for them in our defined table (notice: if NaNs are because we have limit bars for do calculation) '''
        idataframe['EMA50'] = ta.ema(idataframe['close'], length=50)
        idataframe['EMA200'] = ta.ema(idataframe['close'], length=200)

        ''' conditions of strategy '''
        idataframe['long'] = ta.cross(series_a=idataframe['EMA50'], series_b=idataframe['EMA200'], above=True)
        idataframe['short'] = ta.cross(series_a=idataframe['EMA200'], series_b=idataframe['EMA50'], above=True)

        # print(idataframe[['timestamp','close','EMA50','EMA200','long','short']])

        ''' the bot go active and positioning if the conditions are occur '''
        if not long_position:
            if idataframe['long'][last_row] == 1:
                print(f'long entry for {symbol} on {last_closed_candle_cprice} at {last_closed_candle_time}')
                # exchange.create_market_buy_order(symbol, quantity)
                long_position = True
        else:
            if idataframe['long'][last_row] == -1:
                print(f'long stop for {symbol} on {last_closed_candle_cprice} at {last_closed_candle_time}')
                # exchange.create_market_buy_order(symbol, quantity)
                long_position = False
        
        if not short_position:
            if idataframe['short'][last_row] == 1:
                print(f'short entry for {symbol} on {last_closed_candle_cprice} at {last_closed_candle_time}')
                # exchange.create_market_buy_order(symbol, quantity)
                long_position = True
        else:
            if idataframe['short'][last_row] == -1:
                print(f'short stop for {symbol} on {last_closed_candle_cprice} at {last_closed_candle_time}')
                # exchange.create_market_buy_order(symbol, quantity)
                long_position = False
                
    time.sleep(sleep_time)