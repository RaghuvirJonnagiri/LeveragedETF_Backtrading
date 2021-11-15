# -*- coding: utf-8 -*-
"""
Created on Sun Sep 19 15:33:58 2021

@author: Raghuvir
@References: teddykoker@github
"""

###--------------IMPORTING ALL REQUIRED LIBRARIES-----------------
import numpy as np ; import matplotlib.pyplot as plt; import seaborn as sns
import pandas as pd; import pandas_datareader.data as pd_data
from datetime import datetime
import yfinance as yf 
from tabulate import tabulate
import backtrader as bt
###--------------INITIATING VARIABLES-----------------------------

inv_initial = 1 # Initial investment 
start_time = datetime(1993,6,23) # investment initiated time
end_time = datetime(2021,9,1) # investment withdrawing time

#--------------DEFINING ALL NECESSARY FUNCTIONS-----------------

# Function returns investment value, assuming initial value of 1,  as stock price changes 
def stock_returns(stock_price):
    return (1+stock_price.pct_change(1, fill_method = 'ffill')).cumprod()
    #return stock_price.div(stock_rice[0])*1

# Function returns Compound Annual Growth Rate (CAGR) of a stock or portfolio
def stock_CAGR(stock_price):
    dt_years = (stock_price.index[-1]-stock_price.index[0]).days/365 # number of years
    total_return_ratio = stock_price[-1]/stock_price[0] # ratio of final to initial stock value
    return (total_return_ratio**(1/dt_years) - 1)*100

# Function returns Average Average Annual Growth Rate (AAGR) of a stock or portfolio
def stock_AAGR(stock_price):
    dt_years = (stock_price.index[-1]-stock_price.index[0]).days/365 # number of years
    total_return_ratio = stock_price[-1]/stock_price[0] # ratio of final to initial stock value
    return (total_return_ratio/dt_years)

# Function returns drawdown of a stock or portfolio
def stock_drawdown(stock_price):
    stock_returns_val = stock_returns(stock_price) # _val added to avoid conflict with function
    return round(-(stock_returns_val.cummax()-stock_returns_val).div(stock_returns_val.cummax())*100,2)

# Function returns time required to break even in future if invested on that particular day
def stock_timetillprofit(stock_price):
    stock_price_trimmed = stock_price.iloc[0:stock_price.argmax()] #trimming data to highest value
    len_data = len(stock_price_trimmed) # size of resulting data
    days_timetillprofit = stock_price_trimmed*0
    #print(len(days_timetillprofit))
    for i in range(len_data-1) :
        timetillprofit_dummy1 = (stock_price_trimmed > stock_price_trimmed.iloc[i]).astype(int)
        timetillprofit_dummy2 = (timetillprofit_dummy1.iloc[i+1:len_data].idxmax() - 
                                 timetillprofit_dummy1.index[i]).days
        days_timetillprofit.iloc[i] = timetillprofit_dummy2
    return days_timetillprofit

# Function returns leveraged returns of a stock accounting for expense ratio
def stock_leveraged_returns(stock_price, leverage_mul, expense_ratio = 0.0093, inv_initial=1):
    # Assuming number of trading days as 252 in an year
    stock_lev_returns = (1 + (stock_price.pct_change(1) - expense_ratio/252)*leverage_mul ).cumprod()
    stock_lev_returns[0] = 1
    return stock_lev_returns*inv_initial

# Choosing the stocks
SPY = yf.download('SPY',start_time, end_time, progress=False)['Adj Close'].rename('SPY')
SPXL = yf.download('SPXL', start_time, end_time, progress=False)['Adj Close'].rename('SPXL')
SPXL = stock_leveraged_returns(SPY, 3, 0.0093, inv_initial)

# Plotting returns
plt.plot(stock_returns(SPY), color = 'g', label = 'SPY')
plt.plot(stock_returns(SPXL), color = 'r', label = 'SPXL')
plt.legend(); plt.title('SPY vs SPXL : Initial Investment is {}$'.format(inv_initial)) ; #plt.show();
plt.savefig('ReturnsComparison.pdf')

# Performance metrics
df_perf = pd.DataFrame({'Stock':['SPY','SPXL'], 'AAGR':[stock_AAGR(SPY),stock_AAGR(SPXL) ], 'CCGR':[stock_CAGR(SPY),stock_CAGR(SPXL)]  })
SPY_drawdown = stock_drawdown(SPY); SPXL_drawdown = stock_drawdown(SPXL)
df_perf['Max_Drawdown'] = [str(SPY_drawdown.min())+'%('+str(SPY_drawdown.idxmin().date())+')',
                           str(SPXL_drawdown.min())+'%('+str(SPXL_drawdown.idxmin().date())+')']
print(tabulate(df_perf,headers='keys',showindex=False))

# plotting drawdown 
plt.figure()
plt.plot(SPXL_drawdown.index, SPXL_drawdown, label = 'SPY', color='red', alpha = 1)                                                     
plt.plot(SPY_drawdown.index, SPY_drawdown, label = 'SPXL', color='green', alpha = 1)     
plt.legend();plt.title('SPY vs SPXL : Drawdown percentage')                                                
plt.savefig('DrawdownComparison.pdf')                                                             

# plotting time to break even
fig, (axs1,axs2) = plt.subplots(2,1,gridspec_kw={'height_ratios':[2,1]})
axs1.plot(stock_returns(SPY),'-g', label='SPY')
axs1.plot(stock_returns(SPXL), '-r', label='SPXL')
axs1.legend();
axs1.tick_params(axis='y',labelcolor='black'); axs1.set_ylabel('Stock Returns : starting with {}$'.format(inv_initial))
ax11 = axs1.twinx()
ax11.plot(stock_timetillprofit(SPY), color='green', alpha=0.3)
ax11.plot(stock_timetillprofit(SPXL), color = 'red', alpha=0.3); #ax11.set_yscale('log')
ax11.tick_params(axis='y', labelcolor = 'black'); ax11.set_ylabel('Days To Profit', color='black',alpha=0.4)
fig.suptitle('Stock Returns, Drawdown and DaysToProfit')

axs2.plot(SPXL_drawdown.index, SPXL_drawdown, label = 'SPY', color='red', alpha = 1)                                                     
axs2.plot(SPY_drawdown.index, SPY_drawdown, label = 'SPXL', color='green', alpha = 1)  
axs2.set_ylabel('Drawdown %')

plt.savefig('ReturnsDrawdownProfittimeComparison.pdf')


import pandas as pd
import pandas_datareader.data as web
import datetime
import backtrader as bt
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (10, 6) # (w, h)

def sim_leverage(proxy, leverage=1, expense_ratio = 0.0, initial_value=1.0):
    """
    Simulates a leverage ETF given its proxy, leverage, and expense ratio.
    
    Daily percent change is calculated by taking the daily percent change of
    the proxy, subtracting the daily expense ratio, then multiplying by the leverage.
    """
    pct_change = proxy.pct_change(1)
    pct_change = (pct_change - expense_ratio / 252) * leverage
    sim = (1 + pct_change).cumprod() * initial_value
    sim[0] = initial_value
    return sim

start = datetime.datetime(1986, 5, 19)
end = datetime.datetime(2019, 1, 1)

#vfinx = web.DataReader("VFINX", "yahoo", start, end)["Adj Close"]
#vustx = web.DataReader("VUSTX", "yahoo", start, end)["Adj Close"]
vfinx = yf.download('SPY',start_time, end_time, progress=False)['Adj Close'].rename('SPY')
vustx = yf.download('SPXL', start_time, end_time, progress=False)['Adj Close'].rename('SPXL')
upro_sim = sim_leverage(vfinx, leverage=3.0, expense_ratio=0.0092).to_frame("close")
tmf_sim = sim_leverage(vustx, leverage=3.0, expense_ratio=0.0109).to_frame("close")

for column in ["open", "high", "low"]:
    upro_sim[column] = upro_sim["close"]
    tmf_sim[column] = tmf_sim["close"]
    
upro_sim["volume"] = 0
tmf_sim["volume"] = 0

upro_sim = bt.feeds.PandasData(dataname=upro_sim)
tmf_sim = bt.feeds.PandasData(dataname=tmf_sim)
vfinx = bt.feeds.YahooFinanceData(dataname="VFINX", fromdate=start, todate=end)

class BuyAndHold(bt.Strategy):
    def next(self):
        if not self.getposition(self.data).size:
            self.order_target_percent(self.data, target=1.0)
            
def backtest(datas, strategy, plot=False, **kwargs):
    cerebro = bt.Cerebro()
    for data in datas:
        cerebro.adddata(data)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addstrategy(strategy, **kwargs)
    results = cerebro.run()
    if plot:
        cerebro.plot()
    return (results[0].analyzers.drawdown.get_analysis()['max']['drawdown'],
            results[0].analyzers.returns.get_analysis()['rnorm100'],
            results[0].analyzers.sharperatio.get_analysis()['sharperatio'])

dd, cagr, sharpe = backtest([vfinx], BuyAndHold, plot=True)
print(f"Max Drawdown: {dd:.2f}%\nCAGR: {cagr:.2f}%\nSharpe: {sharpe:.3f}")

dd, cagr, sharpe = backtest([upro_sim], BuyAndHold)
print(f"Max Drawdown: {dd:.2f}%\nCAGR: {cagr:.2f}%\nSharpe: {sharpe:.3f}")


'''
SPXL_sim = stock_leveraged_returns(SPY, leverage_mul=3.0, expense_ratio=0.0092).to_frame("close")
for column in ["open", "high", "low"]:
    SPXL[column] = SPXL_sim["close"]
    
SPXL_sim["volume"] = 0

SPXL_sim = bt.feeds.PandasData(dataname=SPXL_sim)

class MaCrossStrategy(bt.Strategy):
 
    def __init__(self):
        ma_fast = bt.ind.SMA(period = 10)
        ma_slow = bt.ind.SMA(period = 50)
         
        self.crossover = bt.ind.CrossOver(ma_fast, ma_slow)
 
    def next(self):
        if not self.position:
            if self.crossover > 0: 
                self.buy()
        elif self.crossover < 0: 
            self.close()
 
cerebro = bt.Cerebro()
 
#data = bt.feeds.YahooFinanceData(dataname = 'AAPL', fromdate = datetime(2010, 1, 1), todate = datetime(2020, 1, 1))
cerebro.adddata(SPXL_sim)
 
cerebro.addstrategy(MaCrossStrategy)
 
cerebro.broker.setcash(1000000.0)
 
cerebro.addsizer(bt.sizers.PercentSizer, percents = 10)
 
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name = "sharpe")
cerebro.addanalyzer(bt.analyzers.Transactions, _name = "trans")
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name = "trades")
 
back = cerebro.run()
 
cerebro.broker.getvalue()
 
back[0].analyzers.sharpe.get_analysis()
 
back[0].analyzers.trans.get_analysis()
 
back[0].analyzers.trades.get_analysis()
 
cerebro.plot()
'''

'''
# Getting feeds from backtrader framework 
# SPY_bt = bt.feeds.YahooFinanceData(dataname='SPY',from_date = start_time, to_date = end_time)
SPXL_bt = bt.feeds.YahooFinanceData(dataname='SPY',from_data = start_time, to_date = end_time)

class strategy_200ma (bt.Strategy):
    def __init__(self):
        #self.stock_ref = self.datas[0]
        #self.stock_main = self.datas[1]
        sma20 = bt.ind.SimpleMovingAverage(self,period=20)
        sma50 = bt.ind.SimpleMovingAverage(self,period=50)
        sma100 = bt.ind.SimpleMovingAverage(self,period=100)
        sma200 = bt.ind.SimpleMovingAverage(self,period=200)
        self.crossover200ma = bt.ind.CrossOver(self, sma200)
        self.crossunder200ma = bt.ind.CrossOver(sma200, self)
    def next(self):
        if not self.position:
            if self.crossover200ma:
                self.buy()
            elif self.crossunder200ma:
                self.close()
                
                
        
    
bt_cerebro = bt.Cerebro(); bt_cerebro.broker.setcash(inv_initial);
#bt_cerebro.adddata(SPY);
bt_cerebro.adddata(SPXL_bt);
bt_cerebro.addstrategy(strategy_200ma);
bt_cerebro.addanalyzer(bt.analyzers.SharpeRatio)
bt_cerebro.addanalyzer(bt.analyzers.Returns)
bt_cerebro.addanalyzer(bt.analyzers.DrawDown)
output = bt_cerebro.run(); 

bt_cerebro.plot();
sharpe_ratio = output[0].analyzers.sharperatio.get_analysis()['sharperatio']
max_drawdown = output[0].analyzers.drawdown.get_analysis()['max']['drawdown']
print('Sharpe Ratio : {}'.format(sharpe_ratio))
print('Max DrawDown : {}'.format(max_drawdown))
'''