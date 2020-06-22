"""
Module to extract sentiment for top 20 keywords
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import pandas as pd
import datetime
from tqdm import tqdm
tqdm.pandas()

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
factory = StemmerFactory()
stemmer = factory.create_stemmer()

def main():
	#Import and Prep on TOP_10_Evolution_Weekly_Similar_Issue_Keyword.csv
	df_weekly = pd.read_csv('/mnt/louis/Issue Monitoring/TOP_10_Evolution_Weekly_Similar_Issue_Keyword.csv')

	df_weekly = df_weekly[df_weekly['week_of_the_year']>=13]

	df_weekly_prepared = pd.DataFrame(columns=['keyword','count'])
	df_temp = df_weekly[df_weekly.topic=='confidence in government'].reset_index(drop=True)
	for i in range(len(df_temp)):
		df_weekly_prepared = df_weekly_prepared.append({'keyword':df_temp.loc[i,'keyword'],'count':df_temp.loc[i,'keyword_count']},ignore_index=True)

		df_weekly_prepared = df_weekly_prepared.append({'keyword':df_temp.loc[i,'similar_keyword'],'count':df_temp.loc[i,'similar_keyword_count']},ignore_index=True)

	df_weekly_prepared = df_weekly_prepared.drop_duplicates()

	TOP_20_keywords_list = list(df_weekly_prepared.groupby('keyword').count()['count'].sort_values(ascending=False).head(20).index)

	#Import Full Data
	df = pd.read_csv('/mnt/louis/Dataset/Final/agg_final_data.csv',usecols=['created_at','text'])
	df['created_at'] = pd.to_datetime(df['created_at'])
	df['created_date'] = df['created_at'].apply(lambda x: x.date())
	df = df[df['created_date']>=datetime.date(2020,3,23)].reset_index(drop=True)
	df = df[['text']]
	df = df.drop_duplicates()

	#Label each tweets is containing top 20 keywords
	df['check'] = 0

	for keyword in TOP_20_keywords_list:
		df['is_{}'.format(keyword)] = df['text'].apply(lambda x: 1 if keyword in x else 0)
		df['check'] = df['check'] + df['is_{}'.format(keyword)]

	#Filter only tweets contain top 20 keywords
	df = df[df['check']>0]

	#Extract sentiment score
	sentiment_dict = {}
	for keyword in TOP_20_keywords_list:
		df_temp = df[df['is_{}'.format(keyword)]==1]
		df_temp['text'] = list(df_temp['text'].progress_apply(lambda x: stemmer.stem(x)))
		print(df_temp)
		sentiment_score_series = df_temp['text'].apply(lambda x: extract_sentiment(x))
		sentiment_dict[keyword] = {}
		sentiment_dict[keyword]['positive'] = len(sentiment_score_series[sentiment_score_series>=0.2])
		sentiment_dict[keyword]['neutral'] = len(sentiment_score_series[(sentiment_score_series<0.2) & (sentiment_score_series>-0.2)])
		sentiment_dict[keyword]['negative'] = len(sentiment_score_series[sentiment_score_series<=-0.2])

	#Store in dataframe
	keyword_list = []
	sentiment_count_list = []
	for keyword in TOP_20_keywords_list:
		for sentiment in ['positive','neutral','negative']:
			keyword_list.append(keyword)
			sentiment_count_list.append(sentiment_dict[keyword][sentiment])

	df_sentiment = pd.DataFrame({
		'keyword' : keyword_list,
		'sentiment' : ['positive','neutral','negative']*20,
		'count' : sentiment_count_list
		})

	df_sentiment.to_csv('/mnt/louis/Issue Monitoring/sentiment_top_20_keywords_confidence_in_government.csv',index=False)


def extract_sentiment(sentence):
	'''
	Function to extract sentiment from sentence based on positive and negative corpus
	'''
	sentiment_series = pd.Series(sentence.split()).apply(lambda x: 1 if x in positive_words_list else -1 if x in negative_words_list else 0)

	return sentiment_series.mean()


with open("/mnt/louis/Supporting Files/combined_positive_words.txt") as f:
    positive_words_list = f.read().splitlines()

with open("/mnt/louis/Supporting Files/combined_negative_words.txt") as f:
    negative_words_list = f.read().splitlines()


if __name__ == "__main__":
	main()