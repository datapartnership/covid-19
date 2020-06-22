"""
Module to extract word-level data used for policy issue viz based on Twitter Word2Vec
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import os
import argparse
import pandas as pd
import numpy as np
import gensim
import re
from tqdm import tqdm

from preprocessing_text import sentences_cleaner

forbidden_keywords_list = []
with open('/mnt/louis/Issue Monitoring/forbidden_keywords.txt','r') as f:
	for line in f:
		forbidden_keywords_list.append(re.sub('\n','',line).lower())
forbidden_keywords_list.append('')
forbidden_keywords_list.append('covid19')

def main():

	#Load Model
	model_all = gensim.models.Word2Vec.load('/mnt/louis/Issue Monitoring/model/w2v_insta_all_300.model')

	SOURCE_general = '/mnt/louis/Issue Monitoring/topic/general/'
	SOURCE_new_normal = '/mnt/louis/Issue Monitoring/topic/new_normal/'

	_,_,filenames_general = next(os.walk(SOURCE_general))
	_,_,filenames_new_normal = next(os.walk(SOURCE_new_normal))


	#Import insta corpus
	df_insta = pd.read_csv('/mnt/louis/Dataset/Instagram/Final/agg_final_data_insta.csv',usecols=['created_at','text'])
	df_insta['created_at'] = pd.to_datetime(df_insta['created_at'])
	df_insta['created_week'] = df_insta['created_at'].apply(lambda x: x.weekofyear)
	df_insta = df_insta[(df_insta.created_week>=13)].reset_index(drop=True)
	df_insta['created_date'] = df_insta['created_at'].apply(lambda x: x.date())


	#Create Similar Keyword Dataframe
	df = pd.DataFrame(columns=['topic','keyword','similar_keyword','cosine_similarity','keyword_count','similar_keyword_count'])


	#Iterate through all topics corpus
	print("-------------------------- Extracting Similar General Keyword for each Topic")
	for topic_file in tqdm(filenames_general):
		topic = ' '.join(re.sub('_',' ',topic_file.split('.')[0]).split()[1:])
		keyword_list = []
		with open(SOURCE_general + topic_file, "r") as f:
			for line in f:
				keyword_list.append(sentences_cleaner(line))

		keyword_list = [keyword_list[i] for i in range(len(keyword_list)) if keyword_list[i] not in forbidden_keywords_list]

		for word in keyword_list:
			try:
				similar_word_list = model_all.most_similar(word, topn = 10)
				for similar_word in similar_word_list:
					if (similar_word[0] not in forbidden_keywords_list) and (not similar_word[0].isdigit()):
						df = df.append({
							'topic':topic,
							'keyword':word,
							'keyword_count': model_all.wv.vocab[word].count,
							'similar_keyword': similar_word[0],
							'similar_keyword_count': model_all.wv.vocab[similar_word[0]].count,
							'cosine_similarity':similar_word[1]}
							,ignore_index=True)
			except Exception as e:
				print(e)
				
	df.to_csv('/mnt/louis/Issue Monitoring/insta_TOP_10_Similar_Issue_Keyword.csv',index=False)
	

	#Extract count of all aggregated keywords for each topic daily
	print("-------------------------- Extracting Keyword Count for each Topic Daily")

	#Create Weekly Keyword Count Dataframe
	df_topic_daily = pd.DataFrame(columns=['topic','date','count','tweets_volume'])

	#Iterate through all topic and tweets in each week
	for topic in tqdm(list(df['topic'].unique())):
		df_topic_keyword_temp = df[df.topic==topic].reset_index(drop=True) 
		keyword_list = list(df_topic_keyword_temp['similar_keyword'].unique())
		for keyword in list(df_topic_keyword_temp['keyword'].unique()):
			keyword_list.append(keyword)

		keyword_list = [keyword_list[i] for i in range(len(keyword_list)) if keyword_list[i] not in forbidden_keywords_list]

		for date in list(df_insta['created_date'].unique()):
			cnt = 0
			df_filter_date = df_insta[df_insta['created_date']==date]
			corpus = df_filter_date['text'].to_list()
			for tweets in corpus:
				for keyword in keyword_list:
					if (keyword in tweets) and (keyword not in forbidden_keywords_list) and (not keyword.isdigit()):
						cnt += 1

			df_topic_daily = df_topic_daily.append({
				'topic':topic,
				'date':date,
				'count':cnt,
				'tweets_volume': len(df_filter_date)
				},ignore_index=True)

	df_topic_daily.to_csv('/mnt/louis/Issue Monitoring/insta_daily_keyword_count.csv',index=False)

	
	#Extract the evolution of similar topic keyword weekly
	print("-------------------------- Extracting Evolution of Similar Keyword for each Topic Weekly")

	#Create Similar Keyword Evolution Dataframe
	df_keyword_evolution = pd.DataFrame(columns=['topic','week_of_the_year','keyword','similar_keyword','cosine_similarity','keyword_count','similar_keyword_count'])

	#Iterate through all topic and similar keyword in each week
	for topic in tqdm(list(df['topic'].unique())):
		keyword_list = []
		df_topic_keyword_temp = df[df.topic==topic].reset_index(drop=True)
		for keyword in list(df_topic_keyword_temp['keyword'].unique()):
			keyword_list.append(keyword)

		keyword_list = [keyword_list[i] for i in range(len(keyword_list)) if keyword_list[i] not in forbidden_keywords_list]

		for week in list(df_insta['created_week'].unique()):
			#Load Model
			model = gensim.models.Word2Vec.load('/mnt/louis/Issue Monitoring/model/w2v_insta_week_{}_300.model'.format(week))

			for word in keyword_list:
				try:
					similar_word_list = model.most_similar(word, topn = 10)

					for similar_word in similar_word_list:

						if (similar_word[0] not in forbidden_keywords_list) and (not similar_word[0].isdigit()):
							df_keyword_evolution = df_keyword_evolution.append({
								'topic':topic,
								'week_of_the_year':week,
								'keyword':word,
								'similar_keyword': similar_word[0],
								'cosine_similarity':similar_word[1],
								'keyword_count': model.wv.vocab[word].count,
								'similar_keyword_count': model.wv.vocab[similar_word[0]].count
								}
								,ignore_index=True)
				except Exception as e:
					print(e)

	df_keyword_evolution.to_csv('/mnt/louis/Issue Monitoring/insta_TOP_10_Evolution_Weekly_Similar_Issue_Keyword.csv',index=False)


	########################################## New Normal Keyword ##########################################

	#Iterate through all topics corpus
	new_normal_keyword_list = []

	for topic_file in filenames_new_normal:
		with open(SOURCE_new_normal + topic_file, "r") as f:
			for line in f:
				new_normal_keyword_list.append(sentences_cleaner(line))

	new_normal_keyword_list = [new_normal_keyword_list[i] for i in range(len(new_normal_keyword_list)) if new_normal_keyword_list[i] not in forbidden_keywords_list]

	#Create Similar Keyword Dataframe
	df_new_normal = df[df['keyword'].isin(new_normal_keyword_list)].reset_index(drop=True)
	

	#Extract count of all aggregated keywords for each topic daily
	print("-------------------------- Extracting New Normal Keyword Count for each Topic Daily")

	#Create Weekly Keyword Count Dataframe
	df_topic_daily_new_normal = pd.DataFrame(columns=['topic','date','count','tweets_volume'])

	#Iterate through all topic and tweets in each week
	for topic in tqdm(list(df_new_normal['topic'].unique())):
		df_topic_keyword_temp = df_new_normal[df_new_normal.topic==topic].reset_index(drop=True) 
		keyword_list = list(df_topic_keyword_temp['similar_keyword'].unique())
		for keyword in list(df_topic_keyword_temp['keyword'].unique()):
			keyword_list.append(keyword)

		keyword_list = [keyword_list[i] for i in range(len(keyword_list)) if keyword_list[i] not in forbidden_keywords_list]

		for date in list(df_insta['created_date'].unique()):
			cnt = 0
			df_filter_date = df_insta[df_insta['created_date']==date]
			corpus = df_filter_date['text'].to_list()
			for tweets in corpus:
				for keyword in keyword_list:
					if (keyword in tweets) and (keyword not in forbidden_keywords_list) and (not keyword.isdigit()):
						cnt += 1

			df_topic_daily_new_normal = df_topic_daily_new_normal.append({
				'topic':topic,
				'date':date,
				'count':cnt,
				'tweets_volume': len(df_filter_date)
				},ignore_index=True)

	df_topic_daily_new_normal.to_csv('/mnt/louis/Issue Monitoring/insta_daily_keyword_count_new_normal.csv',index=False)

if __name__ == '__main__':
	main()

