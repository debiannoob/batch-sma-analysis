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
import sys
import os

## Global variables & Configuration
sma = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
sma_type = 'Close' # or 'Open'
csv = 'results_current_bull.xlsx'
charts = 'charts/current_bull/'
df_list = []
hodl = []
asset = yf.Ticker("BTC-USD")
#quarterlies = 'charts/quarterlies/'
# Define test periods
#start1 = pd.Timestamp(year=2011,month=11,day=1,tz='UTC') # This period not available with yfinacne api...
#end1 = pd.Timestamp(year=2013,month=11,day=1,tz='UTC')
start2 = pd.Timestamp(year=2022,month=11,day=21,tz='UTC')# inclusive
end2 = pd.Timestamp.today(tz='UTC') # non-inclusive


test_periods =[ 
    #[start1, end1],
    [start2, end2],
]

## Functions
def findDrawDowns(series):
    i = 0
    drawdown_percentages = np.array([])
    while i < len(series):
        #print('i: '+str(i))
        if i+1 < len(series) and series[i+1] < series[i]: # start of a price decline id'd
            peak_index = i # save peak index
            #print('peak index: '+str(peak_index))
            peak_value = series[i] # save peak value
            #print('peak value: '+str(peak_value))
            search_series = np.array(series[peak_index+1:]) # convert series to array, from values after peak to end
            try: # If remaining values make or match current peak, make end index
                end_index = int(np.argwhere(search_series >= peak_value)[0])
            except: # otherwise, make end of series the end index
                end_index = len(series)
            search_series = search_series[:int(end_index)] # Remove unnecessary search values, if any
            #print('searching for trough in search_series: '+str(search_series))
            trough_value = np.min(search_series) # Get trough value
            percent_decline = ((peak_value - trough_value) / peak_value) * 100 # Calculate percentage drawdown
            drawdown_percentages = np.append(drawdown_percentages, percent_decline) # Save to array
            #print('end_index in in pre sliced sub series: '+str(end_index))
            i += end_index+1 # Resume search for next drawdown
            #print('......')
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
        #starting_portfolio_value = 100
        starting_portfolio_value = df['Close'][0]
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
        output_df.loc[sma_pair_count] = [f'{sma[0]} vs {sma[1]}', f'{df.iloc[0].name.date()} - {df.iloc[-1].name.date()}',max_dd,len(dd),trade_count,rtn_multiple,hodl[test_period_count],multiple_ratio]
        #print(output_df)
        '''
        # Plot/Save charts
        sns.set_style('white')
        fig, ax = plt.subplots(figsize=(15,9))
        labels = ['Trading rule', 'Buy & hold']
        ax.plot(np.log(df['Cumulative return']))
        ax.plot(np.log(df['Close']))
        title = f'Long {sma[0]} vs {sma[1]} {df.iloc[0].name.year} - {df.iloc[-1].name.year}'
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel("Returns (log)", fontsize=13)
        ax.set_xlabel('Date', fontsize=13)
        plt.xticks(rotation=45)
        ax.legend(labels = labels, fontsize = 'large', loc = 'lower right')
        
        ax.text(
            x = 0.05, 
            y = 0.95,
            fontsize = 14,
            s = f"Max DD: {max_dd}% \nDD Freq: {len(dd)} \nTrades: {trade_count} \nReturn multiple: {rtn_multiple}x \nHODL Multiple {hodl[test_period_count]}x \nMultiple Ratio: {multiple_ratio}", 
            transform = ax.transAxes,  
            bbox=dict(alpha=0.3,facecolor='white', edgecolor='black', pad=10),
            verticalalignment='top'
        )
        sns.despine()
        plt.savefig(f'{charts}{title}.png')
        '''
        #sys.exit()
        
        sma_pair_count += 1
        # reset variables for next test period
        returns = []
        #names = []
        long = False
        trade_count = 0
        position_tracker = []
        
    # Iterate p
    test_period_count += 1
    
    output_df = output_df.sort_values('Multiple Ratio', ascending=False)
    
    '''
    if os.path.exists(csv):
        output_df.to_csv(csv, mode='a', header=False)
    else:
        output_df.to_csv(csv, mode='w')
    '''
    
    if os.path.exists(csv):
        with pd.ExcelWriter(csv, mode='a', engine='openpyxl') as writer:
            # append the new worksheet to the file
            output_df.to_excel(writer, sheet_name=f'{end2.date()}', index=False)
    else:
        with pd.ExcelWriter(csv, mode='w', engine='openpyxl') as writer:
            output_df.to_excel(writer, sheet_name=f'{end2.date()}', index=False)
