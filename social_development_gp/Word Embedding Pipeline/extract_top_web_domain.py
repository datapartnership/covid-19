"""
Module to extract top news web domain from tweets corpus
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

from tqdm import tqdm
import pandas as pd
import os
import re

tqdm.pandas()

def main():
	created_at = []
	domain = []
	with open('/mnt/louis/Dataset/tweet_URL_list.txt','r') as f:
		for line in tqdm(f):
			lst = re.sub('\n','',line).split(',')
			for i in range(2,len(lst)):
				created_at.append(lst[0])
				domain.append(extract_domain(lst[i]))

	#Filter only news domain
	df_gdelt = pd.read_csv('/mnt/alicia/indonesian_news/clean_indonesia_news.csv',usecols=['URL'])
	gdelt_url_series = pd.Series(df_gdelt['URL'].unique())
	gdelt_news_domain_list = list(gdelt_url_series.progress_apply(lambda x: extract_domain(x)))
	domain_series = pd.Series(domain)
	domain_series = domain_series[domain_series.isin(gdelt_news_domain_list)].reset_index(drop=True)

	top_10_domain = domain_series.value_counts().head(10).index.to_list()

	df = pd.DataFrame({'created_at':created_at,'root_domain':domain})
	df = df[df.root_domain.isin(top_10_domain)]
	df = df[~pd.isnull(df.created_at)]
	df['created_at'] = pd.to_datetime(df['created_at'])
	df['created_week'] = df['created_at'].apply(lambda x: x.weekofyear)
	df = df[df['created_week']>=13]

	df = df.groupby(['created_week','root_domain']).size().rename('freq').reset_index()

	df.to_csv('/mnt/louis/Dataset/TOP_domain.csv',index=False)


def extract_domain(URL):
	'''
	Function to extract domain from the given URL
	'''
	try:
		return URL.split('://')[1].split('/')[0]
	except:
		return URL


if __name__=='__main__':
	main()