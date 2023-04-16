## Import packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mlt
import seaborn as sns
sns.set()
mlt.rcParams['font.family'] = 'sans-serif'
import mplfinance as mpf # still need this?
import yfinance as yf

## Global variables & Configuration
sma = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
#sma = [4,19]
sma_type = 'Close' # or 'Open'
csv = 'results.csv'
charts = 'charts/'
df_list = []
hodl = []
asset = yf.Ticker("BTC-USD")
#quarterlies = 'charts/quarterlies/'
# Define test periods
#start1 = pd.Timestamp(year=2011,month=11,day=1,tz='UTC') # This period not available with yfinacne api...
#end1 = pd.Timestamp(year=2013,month=11,day=1,tz='UTC')
start2 = pd.Timestamp(year=2015,month=1,day=1,tz='UTC')# inclusive
end2 = pd.Timestamp(year=2017,month=12,day=2,tz='UTC') # non-inclusive
start3 = pd.Timestamp(year=2019,month=1,day=1,tz='UTC')
end3 = pd.Timestamp(year=2021,month=11,day=2,tz='UTC')
test_periods =[ 
    #[start1, end1],
    [start2, end2],
    [start3, end3]
]

## Functions
def findDrawDowns(series):
    i = 0
    drawdown_percentages = np.array([])
    while i < len(series):
        if i+1 < len(series) and series[i+1] < series[i]: # start of a price decline id'd
            peak_index = i # save peak index
            peak = series[i] # save peak value
            search_series = np.array(series[peak_index+1:]) # convert series to array, from values after peak to end
            try: # If remaining values make or match current peak, make end index
                end_index = int(np.argwhere(search_series >= peak)[0])
            except: # otherwise, make end of series the end index
                end_index = len(series)
            search_series = search_series[:int(end_index)] # Remove unnecessary search values, if any
            trough = np.min(search_series) # Get trough value
            percent_decline = ((peak - trough) / peak) * 100 # Calculate percentage drawdown
            drawdown_percentages = np.append(drawdown_percentages, percent_decline) # Save to array
            i += int(int(end_index)) # Resume search for next drawdown
        else:
            i += 1 # Resume search for next drawdown
    return drawdown_percentages

def makePairs(sma):
    pairs = []
    if len(sma) > 2:
        for i in sma:
            right_slice = sma[i:]
            for ii in right_slice:
                pairs.append((i,ii))
    elif len(sma) == 2:
        pairs.append((sma[0],sma[1]))
    return pairs


# Define summary performance csv layout
output_df = pd.DataFrame(
    columns=['SMAs','Test Period','Max DD%','DD Freq','Trades','Return Multiple','HODL Benchmark Multiple','Multiple Ratio']
)

# Preprocess SMA list
pairs = makePairs(sma)

## Calculate SMAs
for period in test_periods:
    df = asset.history(
        start = period[0]-pd.Timedelta(np.max(sma),'d'),
        end = period[1]
    )
    sma_columns = [df[sma_type].rolling(k).mean().rename(f'sma_{k}') for k in sma]
    df = pd.concat([df] + sma_columns, axis=1)
    df = df.drop(columns=['Dividends', 'Stock Splits'])
    df['Trades'] = 0
    df = df.loc[period[0]:period[1]]
    hodl.append(
        round(df['Close'][-1] / df['Close'][0],2)
    )
    df_list.append(df)

#print(hodl)

## Run strategy
test_period_count = 0
sma_pair_count = 0 # Track which sma pair

# For each test period
for df in df_list:
    returns = []
    #names = []
    long = False
    trade_count = 0
    position_tracker = []
    
    # For each sma pair
    for sma in pairs:
        #print('sma index: ' + str(pairs.index(sma)))
        # For each df record
        for i in range(1,len(df)):
            
            # Rarely, two smas can have equal values
            if df.iloc[i-1][f'sma_{sma[0]}'] == df.iloc[i-1][f'sma_{sma[1]}']:
                returns.append(0)
                position_tracker.append(np.nan)
                #names.append(df.iloc[i].name)
            
            # Bull cross
            if df.iloc[i-1][f'sma_{sma[0]}'] > df.iloc[i-1][f'sma_{sma[1]}']:
                if long == True: # pad returns
                    returns.append(0)
                    position_tracker.append(np.nan)
                    #names.append(df.iloc[i].name)
                if long == False:
                    l_open = df.iloc[i]['Open']
                    position_tracker.append(1) # documents open of long
                    long = True
                    returns.append(0)
                    #names.append(df.iloc[i].name)
                
            # Bear Cross            
            if df.iloc[i-1][f'sma_{sma[0]}'] < df.iloc[i-1][f'sma_{sma[1]}']:
                if long == False:
                    returns.append(0)
                    position_tracker.append(np.nan)
                    #names.append(df.iloc[i].name)
                if long == True:
                    l_close = df.iloc[i]['Open']
                    returns.append((l_close/l_open) - 1)
                    position_tracker.append(2) # documents close of long
                    trade_count += 1
                    long = False
                    #names.append(df.iloc[i].name)
        
        #df['names list'] = names
        '''
        At this point, all df records have been analysed for a given test period against
        one SMA pair.
        '''
        starting_portfolio_value = 100
        # add 0% gain to start of returns to account for 
        # fact that we start analysis on second record
        returns.insert(0,0)
        position_tracker.insert(0,0)
        returns = np.array(returns)
        #print(df['names list'])
        
        # For simple plotting:
        df['Cumulative return'] = starting_portfolio_value * np.cumprod(1 + returns)
        #df['Log'] = np.log(starting_portfolio_value * np.cumprod(1 + returns)) # need this?

        df['Trades'] = position_tracker
        df['Long Open'] = np.where(df['Trades'] == 1, df['Open'], np.nan)
        df['Long Close'] = np.where(df['Trades'] == 2, df['Open'], np.nan)

        dd = findDrawDowns(df['Cumulative return'])
        try:
            max_dd = round(np.max(dd))
        except ValueError:
            max_dd = 0
        
        rtn_multiple = round(df['Cumulative return'][-1] / df['Cumulative return'][0],2)
        multiple_ratio = round(rtn_multiple/hodl[test_period_count],2)
        
        # Append performance data to output dataframe
        output_df.loc[sma_pair_count] = [f'{sma[0]} vs {sma[1]}', f'{df.iloc[0].name.year} - {df.iloc[-1].name.year}',max_dd,len(dd),trade_count,rtn_multiple,hodl[test_period_count],multiple_ratio]
        #print(output_df)
        sma_pair_count += 1
        '''
        # Plot/Save charts
        ax = df[['Cumulative return', 'Close']].plot(figsize=(15,9), secondary_y='Close', logy=True)
        ax.text(
            x = 0.02, 
            y = 0.96,
            #x = 0.375,
            #y = 0.98,
            fontsize = 14,
            s = f"Max DD: {max_dd}% \nDD Freq: {len(dd)} \nTrades: {trade_count} \nReturn multiple: {rtn_multiple}x \nHODL Multiple {hodl[test_period_count]}x \nMultiple Ratio: {multiple_ratio}", 
            transform = ax.transAxes,  
            ha = "left", va = "top",
            bbox=dict(alpha=0.3,facecolor='white', edgecolor='black', pad=10)
        )
        ax.set_title(f'Long {sma[0]} vs {sma[1]} {df.iloc[0].name.year} - {df.iloc[-1].name.year}', fontsize=14)
        plt.savefig(f'{charts}{ax.get_title()}.png')
        '''
        # reset variables for next test period
        returns = []
        #names = []
        long = False
        trade_count = 0
        position_tracker = []
        
    # Iterate p
    test_period_count += 1
    output_df.to_csv(csv, mode='w')
