# BTC Trendfollwoing
This repo contains four scripts tasked with testing a simple automated trend following strategy. The asset under evaluation is BTC/USD. This strategy can be summarised as follows:

## 1. Long only bull market strategy
  * A long position is opened when the short term SMA crosses above the long term SMA.
  * A long position is closed when the the short term SMA falls below the long term SMA.

## 2. Short only bear market strategy
  * A short position is opened when the short term SMA falls below the long term SMA.
  * A short position is closed when the short term SMA crosses above the long term SMA.

## Criteria for success
### Strategy 1
The goal is to identify which SMA pairings can most closely match (or potentially exceed) the performance of a buy and hold strategy for the three historical bull markets:
  1. 2011-11-01 to 2013-11-01
  2. 2015-01-01 to 2017-12-01
  3. 2019-01-01 to 2021-11-01

A perfect bear market low entry and bull market high exit constitutes a given bull markets' HODL performance. Having identified the top n SMA pairs which most closely matches the HODL performance of the three respective bull markets, statistical methods will be employed to identify likely contenders of high performing SMA pairs for the anticipated 23/24 bull market. In order to have any likelihood of outperforming a simple buy and hold strategy in 23/24, a high performing SMA pair must be coupled with an appropriate degree of leverage, a level which can withstand the elevated volatility risk of this burgeoning asset class.

### Strategy 2
The goal of the second strategy is to identify SMA pairs which can closely match (or potentially exceed) the performance of a short and hold strategy for the three historical bear markets:
  1. 2013-12-01 to 2015-01-01
  2. 2017-12-01 to 2018-12-01
  3. 2021-11-01 to 2022-11-01

A perfect bull market high entry and bear market low exit constitutes a given bear markets' HODL performance. Having identified the top n SMA pairs which most closely matches the HODL performance of the three respective bear markets, statistical methods will be employed to identify likely contenders of high performing SMA pairs for the bear market expected to follow the 23/24 bull market. As discussed in the first strategy, to have any likelihood of outperforming a simple short and hold strategy, a high performing SMA pair must be coupled with an appropriate degree of leverage.
