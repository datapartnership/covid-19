"""
Module to extract sentiment for top 10 news domain
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import pandas as pd
import os
import re
from tqdm import tqdm
tqdm.pandas()

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
factory = StemmerFactory()
stemmer = factory.create_stemmer()


def main():
	created_at = []
	text = []
	domain = []

	print('-------------Extracting Top 10 Root News Domain')
	with open('/mnt/louis/Dataset/tweet_URL_list.txt','r') as f:
		for line in tqdm(f):
			lst = re.sub('\n','',line).split(',')
			for i in range(2,len(lst)):
				created_at.append(lst[0])
				text.append(lst[1])
				domain.append(extract_domain(lst[i]))

	#Filter only news domain
	df_gdelt = pd.read_csv('/mnt/alicia/indonesian_news/clean_indonesia_news.csv',usecols=['URL'])
	gdelt_url_series = pd.Series(df_gdelt['URL'].unique())
	gdelt_news_domain_list = list(gdelt_url_series.progress_apply(lambda x: extract_domain(x)))
	domain_series = pd.Series(domain)
	domain_series = domain_series[domain_series.isin(gdelt_news_domain_list)].reset_index(drop=True)

	top_10_domain = domain_series.value_counts().head(10).index.to_list()

	print(top_10_domain)

	print('-------------Generating Dataframe')
	df = pd.DataFrame({'created_at':created_at,'text':text,'root_domain':domain})
	df = df[~pd.isnull(df.text)]
	df = df[~pd.isnull(df.created_at)]
	df['created_at'] = pd.to_datetime(df['created_at'])
	df['created_week'] = df['created_at'].apply(lambda x: x.weekofyear)
	df = df[df['created_week']>=13]
	df = df[['text','root_domain']]
	df = df.drop_duplicates()
	df = df[df.root_domain.isin(top_10_domain)].reset_index(drop=True)
	

	print('-------------Stemming Word')
	df['text'] = df['text'].progress_apply(lambda x: stemmer.stem(x))


	print('-------------Extracting Sentiment')
	df['sentiment_score'] = df['text'].apply(lambda x: extract_sentiment(x))


	print('-------------Exporting DataFrame')
	df[['root_domain','sentiment_score']].to_csv('/mnt/louis/Issue Monitoring/sentiment_top_10_urls.csv',index=False)


def extract_sentiment(sentence):
	'''
	Function to extract sentiment from sentence based on positive and negative corpus
	'''
	sentiment_series = pd.Series(sentence.split()).apply(lambda x: 1 if x in positive_words_list else -1 if x in negative_words_list else 0)

	return sentiment_series.mean()


def extract_domain(URL):
	'''
	Function to extract domain from the given URL
	'''
	try:
		return URL.split('://')[1].split('/')[0]
	except:
		return URL


with open("/mnt/louis/Supporting Files/combined_positive_words.txt") as f:
    positive_words_list = f.read().splitlines()

with open("/mnt/louis/Supporting Files/combined_negative_words.txt") as f:
    negative_words_list = f.read().splitlines()


if __name__=='__main__':
	main()