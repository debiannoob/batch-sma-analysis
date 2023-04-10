# BTC Trendfollwoing
This repo contians four scripts tasked with testing a simple automated trend following strategy. The asset under evalutaion is BTC/USD. This strategy can be summarised as follows:

## 1. Long only bull market strategy
  a. A long position is opened when the short term SMA crosses above the long term SMA.
  b. A long position is closed when the the short term SMA falls below the long term SMA.

## 2. Short only bear market strategy
  a. A short position is opened when the short term SMA falls below the long term SMA.
  b. A short position is closed when the short term SMA crosses above the long term SMA.

## 3. Long / short bull market strategy
  a. A long position is opened and a short position is closed when the short term SMA crosses above the long term SMA.
  b. A long position is closed and a short position is opened when the the short term SMA falls below the long term SMA.
  
## 4. Long / short bear market strategy
  a. Strategy 3 implemented over a bear market

## Criteria for success
Regarding the first strategy, the goal is to identify which SMA pairings can most closely match (or potentially exceed) the performance of a buy and hold strategy for the three historical bull markets:
  1. 2011-11-01 to 2013-11-01
  2. 2015-01-01 to 2017-12-01
  3. 2019-01-01 to 2021-11-01
A perfect bear market low entry and bull market high exit constitutes a given bull markets' HODL permformance. Having identified the top 5 SMA pairs which most closely matches the HODL performance of the three respective bull markets, statistical methods will be employed to identify likely contenders of high performing SMA pairs for the anticipated 2024 bull market. In order to have any likilihood of outperforming a simple buy and hold strategy in 23/24, a high performing SMA pair must be coupled with an apropriate degreee of leverage, a level which can withstand the elevated volatility risk of this burgeoning asset class.

The goal of the second strategy is to indentify SMA pairs which can closely match (or potentially exceed) the performance of a short and hold strategy for the three historical bear markets:
  1. 2013-12-01 to 2015-01-01
  2. 2017-12-01 to 2018-12-01
  3. 2021-11-01 to 2022-11-01
A perfect bull market high entry and bear market low exit constitutes a given bear markets' HODL permformance. Having identified the top 5 SMA pairs which most closely matches the HODL performance of the ??? respective bear markets, statistical methods will be employed to identify likely contenders of high performing SMA pairs for the bear expected to follow the 2024 bull market. As discussed in the first strategy, to have any liklihood of outperforming a simple short and hold strategy, a high performing SMA pair must be coupled with an apropriate degreee of leverage.

