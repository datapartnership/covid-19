"""
Module to generate sentiment score across time viz
which compares the Twitter and Instagram tone
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""


import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np
import argparse


def get_args():
    parser = argparse.ArgumentParser(description='Data Preprocessing')
    parser.add_argument('--end_date', type=int, required=True, help='Starting Date')
    parser.add_argument('--end_month', type=int, required=True, help='Starting Month')
    return parser.parse_args()


def plot_sentiment_time_series_once(x,y1,y2,y1_band,y2_band):
    '''
    Function to plot sentiment score time series
    '''
    fig, ax = plt.subplots(figsize=(25,15))
    ax.fill_between(x,y1+y1_band,y1-y1_band,alpha=.5)
    ax.plot(x,y1,color='blue',linewidth=5)

    ax.fill_between(x,y2+y2_band,y2-y2_band,alpha=.5)
    ax.plot(x,y2,color='pink',linewidth=5)

    ax.set_xlabel('Date',fontsize=15)
    ax.set_ylabel('Sentiment Score',fontsize=15)
    plt.title('Comparison of Twitter & Instagram Sentiment Score Over Time',fontsize=30)
    ax.legend(['Twitter','Instagram'],fontsize=15)
    ax.tick_params(axis='x', rotation=30,labelsize=15)
    ax.tick_params(axis='y',labelsize=15)
    xticks = ax.xaxis.get_major_ticks()
    remove_date = [i for i in range(len(x)) if i not in [0,6,13,20,27,34,41,48,55,62,69,76,83,90]]
    for i in remove_date:
        xticks[i].set_visible(False)
    fig.savefig('sentiment_timeseries.png', dpi=fig.dpi)


if __name__ == "__main__":
    args = get_args()

    df_twitter = pd.read_csv('/mnt/louis/Dataset/Final/agg_final_data.csv',usecols=['created_at','sentiment_score'])
    df_twitter['created_at'] = pd.to_datetime(df_twitter['created_at'])
    df_twitter['created_date'] = df_twitter['created_at'].apply(lambda x: x.date())
    df_twitter = df_twitter[(df_twitter['created_date']>=datetime.date(2020,3,23)) & (df_twitter['created_date']<=datetime.date(2020,args.end_month,args.end_date))].reset_index(drop=True)
    df_twitter['created_date'] = df_twitter['created_date'].astype(str)

    df_ig = pd.read_csv('/mnt/louis/Dataset/Instagram/Final/agg_final_data_insta.csv',usecols=['created_at','sentiment_score'])
    df_ig['created_at'] = pd.to_datetime(df_ig['created_at'])
    df_ig['created_date'] = df_ig['created_at'].apply(lambda x: x.date())
    df_ig = df_ig[(df_ig['created_date']>=datetime.date(2020,3,23)) & (df_ig['created_date']<=datetime.date(2020,args.end_month,args.end_date))].reset_index(drop=True)
    df_ig['created_date'] = df_ig['created_date'].astype(str)

    x = df_twitter.groupby('created_date').mean().index.to_list()
    y1 = np.array(df_twitter.groupby('created_date').mean()['sentiment_score'].to_list())
    y1_band = np.array(df_twitter.groupby('created_date').std()['sentiment_score'].to_list())
    y2 = np.array(df_ig.groupby('created_date').mean()['sentiment_score'].to_list())
    y2_band = np.array(df_ig.groupby('created_date').std()['sentiment_score'].to_list())

    plot_sentiment_time_series_once(x,y1,y2,y1_band,y2_band)