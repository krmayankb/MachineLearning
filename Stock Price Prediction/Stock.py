import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


install("alpaca-trade-api")

import time 
import alpaca_trade_api as alpaca 
# import backtrader as bt

from alpaca_trade_api.rest import REST, TimeFrame
from alpaca_trade_api.stream import Stream
ENDPOINT="https://paper-api.alpaca.markets"
API_KEY_ID='PKFJXFBKWMP4083G3CRF' # Put in yours here - Needed for paper trading
SECRET_KEY='qTTKNpPOxArhNP7qliV75erLpWMEvxFUkh7qW3bO' # Put in yours here - Needed for paper trading
rest_api = REST(API_KEY_ID, SECRET_KEY, 'https://paper-api.alpaca.markets',api_version='v2')

# obtain account information
account = rest_api.get_account()
# print(account)


class TradingStrategy:
    def __init__(self,STOCK):
        self.api = alpaca.REST(API_KEY_ID, SECRET_KEY, ENDPOINT)
        self.STOCK = STOCK
        self.SELL_LIMIT_FACTOR = 1.01 # 1 percent margin
        self.days = 90
        self.time_list = []
        self._short = 0
        self._long = 0
        self.big = 10
        self.mode = 'test'
        self.get_past_closing_prices(self.days) # Default is 90 days 
        self.get_past_opening_prices(self.days) # Default is 90 days
        self.get_date(self.mode)
        self.buy = 0
        self.data = []
        self.short_window = []
        self.long_window = []
        self.high = 0 
        self.low = 0
        self.close = 0
        self.buy_sell_strategy(self.data, self.short_window, self.long_window, self.big)
        self.get_all_price(self.days)
        self.money_flow_multiplier(self.close, self.high, self.low)
        self.signals_MFM (self.data)
        self.get_volume(self.days)
        self.price_list = []

        
    def buy_sell_strategy(self, data, short_window, long_window, big):
        signal = 0 
        buy_price = []
        sell_price = []
        trade_signal = []       
        for i in range(0, len(data)) :
          if i > big:
            if short_window[i] > long_window[i]:
                if signal != 1:                     #BUY
                    buy_price.append(data[i])
                    sell_price.append(np.nan)
                    signal = 1
                    trade_signal.append(signal)
                else: 
                    buy_price.append(np.nan)
                    sell_price.append(np.nan)
                    trade_signal.append(0)
            elif short_window[i] < long_window[i]:  #SELL
                if signal != -1: 
                    buy_price.append(np.nan)
                    sell_price.append(data[i])
                    signal = -1
                    trade_signal.append(signal)
                else:
                    buy_price.append(np.nan)
                    sell_price.append(np.nan)
                    trade_signal.append(0)
            else: 
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                trade_signal.append(0)
          else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            trade_signal.append(0)
                
        return buy_price, sell_price, trade_signal

    def get_past_closing_prices(self, days):  
        barset = self.api.get_barset(self.STOCK, 'day', limit= days) 
        bars = barset[self.STOCK]
        self.past_closing_prices = [bars[index].c for index in range(len(bars))]
        #self.past_closing_prices_time = [bars[index].t for index in range(len(bars))].      ###tried but found more efficient implementation
        return self.past_closing_prices
    
    def get_past_opening_prices(self, days):  
        barset = self.api.get_barset(self.STOCK, 'day', limit= days) 
        bars = barset[self.STOCK]
        self.past_opening_prices = [bars[index].o for index in range(len(bars))]
        self.past_opening_prices_time = [bars[index].t for index in range(len(bars))]
        return self.past_opening_prices

    def get_all_price(self, days):
        barset = self.api.get_barset(self.STOCK, 'day', limit= days) 
        bars = barset[self.STOCK]
        self.opening_prices = [bars[index].o for index in range(len(bars))]
        self.closing_prices = [bars[index].c for index in range(len(bars))]
        self.high_price = [bars[index].h for index in range(len(bars))]
        self.low_price = [bars[index].l for index in range(len(bars))]
        self.alist = [self.opening_prices, self.closing_prices, self.high_price, self.low_price]
        return self.alist

    def get_volume(self, days):
        barset = self.api.get_barset(self.STOCK, 'day', limit= days) 
        bars = barset[self.STOCK]
        self.vol = [bars[index].v for index in range(len(bars))]
        return self.vol

    def get_date(self, mode):
        """
        get timestamp for data collected
        """
        if mode == 'test':
          date = self.past_opening_prices_time
          self.time_list = [x.date() for x in date]
        else:
          date = self.past_opening_prices_time
          self.time_list = [x.date() for x in date]
          self.time_list = pd.DatetimeIndex(self.time_list, yearfirst= True)
        return self.time_list
    
    def money_flow_multiplier(self, close, high, low):
        diff = high-low
        if diff == 0:
            diff = 1e-3

        multiplier = ((close-low) - (high -close))*100 / diff 
        return multiplier
    

    def signals_MFM (self, MFM_dataframe):
        #buy = 1 , no_action = 0, sell = -1 
        low_thres = -85
        high_thres = 85
        list_signals = [0 for x in MFM_dataframe]
        index = 0 
        for i in range(2,len(MFM_dataframe)):
            if MFM_dataframe[i] <= low_thres and (MFM_dataframe[i-1] >= low_thres and MFM_dataframe[i-2] >= low_thres):
                list_signals[i] = 1
                if index == 0:
                    index = i

            elif MFM_dataframe[i] >= high_thres and (MFM_dataframe[i-1] <= high_thres and MFM_dataframe[i-2] <= high_thres): 
                list_signals[i] = -1
                
        for i in range(len(list_signals)):
            if i < index:
                list_signals[i] = 0 
        
        return list_signals

    # def chaikainOscialltor(self, )

    def live_signals(self):
      days = 3
      low_thres = -90
      high_thres = 90
      signal = 0 
      barset = self.api.get_barset(self.STOCK, 'day', limit= days) 
      bars = barset[self.STOCK]
      self.closing_prices = [bars[index].c for index in range(len(bars))]
      self.high_price = [bars[index].h for index in range(len(bars))]
      self.low_price = [bars[index].l for index in range(len(bars))]
      moneyFlow =[]
      for i in range(len(self.closing_prices)):
        moneyFlow.append(self.money_flow_multiplier(self.closing_prices[i], self.high_price[i], self.low_price[i]))
      
      if moneyFlow[2] <= low_thres and (moneyFlow[1] >= low_thres and moneyFlow[0] >= low_thres):
        signal = 1
      elif moneyFlow[2] >= high_thres and (moneyFlow[1] <= high_thres and moneyFlow[0] <= high_thres):
        signal = -1
      
      return signal

    def get_current_price(self):
        return float(self.api.get_last_trade(self.STOCK).price)
    
    def get_quantity_buy(self):
        if int(float(self.api.get_account().cash)) > 0:
              principal = float(self.api.get_account().cash)
              price = float(self.get_current_price())
              amount = principal * 0.2
              if amount//price == 0:
                amount = principal*0.5
              if principal//price == 0:
                amount = principal
              num_stock = amount/price
              return num_stock
           # return int((float(self.api.get_account().cash)*0.1) \
           #            /self.get_current_price())
        else:
            return 0
        
    def exists_buy_order(self):
        # Identifies if a buy order exists for a stock
        orders = self.api.list_orders()
        for order in orders:
            if order.side=="buy" and order.symbol==self.STOCK:
                return True
        
        return False
    
    def have_bought_stock(self):
        positions=self.api.list_positions()
        for position in positions:
            if position.symbol==self.STOCK and int(position.qty)==self.NEW_QUANTITY + self.EXISTING_QUANTITY:
                return True
        return False
        
        
    def get_buy_price(self):
        # Identify the buying price for a stock
        positions=self.api.list_positions()
        for position in positions:
            if position.symbol==self.STOCK:
                return float(position.cost_basis)/int(position.qty)
    
    
    def buy_market_order(self):
        # Buy the stock at market price (This is for paper-trading)
        if self.NEW_QUANTITY > 0 and self.live_signals() == 1 :
        #if self.NEW_QUANTITY > 0 :
            self.api.submit_order(self.STOCK, \
                        qty=self.NEW_QUANTITY,\
                        side="buy",\
                        type="market", \
                        time_in_force="day",
                        order_class=None)
            self.price_list.append(self.get_current_price()*self.NEW_QUANTITY)
        
    def buy_limit_order(self,base_price):
        pass

    def sell_limit_order(self):
        # (This is for paper-trading)
        pass
        # Your code if you want to sell at limit
        # Check Alpaca docs on selling at limit
        
    def identify_strategy_for_selling(self):
        # If you have multiple strategies
        # Pick between them here - Or use ML to help identify 
        # your strategy
        tempProfit = (self.get_current_price() * self.EXISTING_QUANTITY) - sum(self.price_list)
        if (tempProfit >= (0.1*sum(self.price_list)))  and (self.live_signals() == 0 and self.NEW_QUANTITY>0):
          self.api.submit_order(self.STOCK, self.NEW_QUANTITY, side='sell', type='market', time_in_force='day')
          self.price_list = []
        pass
        
        
    def market_buy_strategy(self):
        # Providing a simple trading strategy here:
        # Buy at market price if conditions are favorable for buying
        # Sell at a limit price that is determined based on buying price
        # This strategy doesn't use any ML here - You may want to use
        # appropriate libraries to train models + use the trained strategy 
        # here
        
        # Get existing quantity
        positions = self.api.list_positions()
        self.EXISTING_QUANTITY = 0
        for position in positions:
            if position.symbol == self.STOCK:
                self.EXISTING_QUANTITY += int(position.qty)
                
        # MARKET BUY order
        self.NEW_QUANTITY=self.get_quantity_buy()
        
        if self.NEW_QUANTITY == 0:
            return "ZERO EQUITY"
        
        if not self.exists_buy_order():
            self.buy_market_order()
            
        
        # BRACKET SELL order
        # Initiate sell order if stock has been bought
        # If not, wait for it to be bought
        while not self.have_bought_stock():
            #print(self.api.positions)
            #print(self.NEW_QUANTITY + self.EXISTING_QUANTITY)
            time.sleep(1)
        
        if self.have_bought_stock():
            
            # Initiate Sell order
            self.identify_strategy_for_selling()
      
    def your_best_strategy(self):
        # Implement here or add other methods to do the same
        pass
        
 

 # # # Get an instance of all our stocks
# strategy_msft = TradingStrategy('MSFT')
# strategy_msft.market_buy_strategy() # Initiates a market buy and limit sell order

# strategy_goog = TradingStrategy('GOOG')
# strategy_goog.market_buy_strategy() # Initiates a market buy and limit sell order

# strategy_aapl = TradingStrategy('AAPL')
# strategy_aapl.market_buy_strategy() # Initiates a market buy and limit sell order

# strategy_nflx = TradingStrategy('NFLX')
# strategy_nflx.market_buy_strategy() # Initiates a market buy and limit sell order

# strategy_qcom = TradingStrategy('QCOM')
# strategy_qcom.market_buy_strategy() # Initiates a market buy and limit sell order

# # # This will accept a order only during market hours. However you can 
# # # use the market data api outside hours


