"""
Module to extract top news url from tweets corpus
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

from tqdm import tqdm
import pandas as pd
import re
import os


def main():
	created_at = []
	urls = []
	with open('/mnt/louis/Dataset/tweet_URL_list.txt','r') as f:
		for line in tqdm(f):
			lst = re.sub('\n','',line).split(',')
			for i in range(2,len(lst)):
				created_at.append(lst[0])
				urls.append(lst[i])

	#Filter only news URL
	df_gdelt = pd.read_csv('/mnt/alicia/indonesian_news/clean_indonesia_news.csv',usecols=['URL'])
	gdelt_url_list = list(df_gdelt['URL'].unique())
	urls_series = pd.Series(urls)
	urls_series = urls_series[urls_series.isin(gdelt_url_list)].reset_index(drop=True)

	top_20_url = urls_series.value_counts().head(20).index.to_list()

	df = pd.DataFrame({'created_at':created_at,'URL':urls})
	df = df[df.URL.isin(top_20_url)]
	df = df[~pd.isnull(df.created_at)]
	df['created_at'] = pd.to_datetime(df['created_at'])
	df['created_week'] = df['created_at'].apply(lambda x: x.weekofyear)
	df = df[df['created_week']>=13]

	df = df.groupby(['created_week','URL']).size().rename('freq').reset_index()

	df.to_csv('/mnt/louis/Dataset/TOP_URLs.csv',index=False)

if __name__=='__main__':
	main()