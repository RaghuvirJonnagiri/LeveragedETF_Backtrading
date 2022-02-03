# Stock Market Analysis

#### This project is to use python and explore stock market. 
<br>

## LeveragedETF_Backtrading.ipynb:
- Creates a widget app to compare the performance of major ETFs and Leveraged ETFs. 
- ETF options : SPY, QQQ, DIA, IWM.
- Leverage Options : 1,2,3.
- Time Options : Any period between 1993 and current.
- Strategy Options : BuyAndHold, Moving Average Cross.

[Click here](https://mybinder.org/v2/gh/RaghuvirJonnagiri/StockMarketAnalysis/HEAD?labpath=LeveragedETF_Backtrading.ipynb) to run this notebook interactively on mybinder. Or use the logo at the bottom for the main repository. Since binder needs to create the environment, it might take a minute or two to load. 


<br>

## SP500_AnalystRatingAnalysis.ipynb:
- Creates a widget app to detect price dislocated stocks based on historical analyst consensus upside
- Marketbeat.com data of historical analyst price target is collected and historical average consensus upside is calculated
- Difference between this average consensus upside and current consensus upside is considered as mean reversion upside.
- This mean reversion upside is plotted against expected EPS (Earnings Per Share) growth and ratings webscraped from Zacks.com

[Click here](https://mybinder.org/v2/gh/RaghuvirJonnagiri/StockMarketAnalysis/HEAD?labpath=SP500_AnalystRatingAnalysis.ipynb) to run this notebook interactively on mybinder. Or use the logo at the bottom for the main repository. Since binder needs to create the environment, it might take a minute or two to load.

UPDATE : mybinder has an issue with webdriver installation. Notebook should still run on a PC if all required installations as included in the code are allowed.
<br>

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/RaghuvirJonnagiri/StockMarketAnalysis/HEAD)
