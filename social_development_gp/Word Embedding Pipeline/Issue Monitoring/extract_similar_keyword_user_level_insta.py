"""
Module to extract user-level data used for policy issue viz based on Instagram Word2Vec
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
from collections import defaultdict
import argparse

from preprocessing_text import sentences_cleaner

forbidden_keywords_list = []
with open('/mnt/louis/Issue Monitoring/forbidden_keywords.txt','r') as f:
	for line in f:
		forbidden_keywords_list.append(re.sub('\n','',line).lower())
forbidden_keywords_list.append('')
forbidden_keywords_list.append('covid19')

def get_args():
    parser = argparse.ArgumentParser(description='Data Preprocessing')
    parser.add_argument('--start_week', type=int, required=True, help='Starting Week')
    return parser.parse_args()


def main():
	args = get_args()

	#Import tweets corpus
	df_insta = pd.read_csv('/mnt/louis/Dataset/Instagram/Final/agg_final_data_insta.csv',usecols=['created_at','text','user_id','comments_count','likes_count','sentiment_score'])
	df_insta['created_at'] = pd.to_datetime(df_insta['created_at'])
	df_insta['created_week'] = df_insta['created_at'].apply(lambda x: x.weekofyear)
	df_insta = df_insta[(df_insta.created_week>=args.start_week)].reset_index(drop=True)
	df_insta['created_date'] = df_insta['created_at'].apply(lambda x: x.date())

	#Create list of unique week
	unique_week_list = list(df_insta['created_week'].unique())

	#Import Similar Keyword Dataframe or Create Similar Keyword Dataframe
	if args.start_week>13:
		df_weekly_general = pd.read_csv('/mnt/louis/Issue Monitoring/insta_TOP_10_Evolution_Weekly_Issue_Keyword_user_level.csv')
		df_weekly_general = df_weekly_general[df_weekly_general['week_of_the_year']<args.start_week].reset_index(drop=True)

		df_weekly_new_normal = pd.read_csv('/mnt/louis/Issue Monitoring/insta_TOP_10_Evolution_Weekly_Issue_Keyword_user_level_new_normal.csv')
		df_weekly_new_normal = df_weekly_new_normal[df_weekly_new_normal['week_of_the_year']<args.start_week].reset_index(drop=True)
	else:
		df_weekly_general = pd.DataFrame(columns=['user_id','tweets_count','week_of_the_year','comments_count','likes_count','sentiment_score'])
		df_weekly_new_normal = pd.DataFrame(columns=['user_id','tweets_count','week_of_the_year','comments_count','likes_count','sentiment_score'])


	SOURCE_general = '/mnt/louis/Issue Monitoring/topic/general/'
	SOURCE_new_normal = '/mnt/louis/Issue Monitoring/topic/new_normal/'

	_,_,filenames_general = next(os.walk(SOURCE_general))
	_,_,filenames_new_normal = next(os.walk(SOURCE_new_normal))

	#Iterate through all topics corpus week by week
	topic_keyword_dict_weekly_general = {}
	topic_keyword_dict_weekly_new_normal = {}
	for week in unique_week_list:
		#Load Model
		model = gensim.models.Word2Vec.load('/mnt/louis/Issue Monitoring/model/w2v_insta_week_{}_300.model'.format(week))

		for topic_file in tqdm(filenames_general):
			topic = ' '.join(re.sub('_',' ',topic_file.split('.')[0]).split()[1:])
			keyword_list_temp = []
			with open(SOURCE_general + topic_file, "r") as f:
				for line in f:
					keyword_list_temp.append(sentences_cleaner(line))

			keyword_list_temp = [keyword_list_temp[i] for i in range(len(keyword_list_temp)) if keyword_list_temp[i] not in forbidden_keywords_list]

			keyword_list = keyword_list_temp.copy()

			for word in keyword_list_temp:
				try:
					similar_word_list = model.most_similar(word, topn = 10)
					for similar_word in similar_word_list:
						if (similar_word[0] not in keyword_list) and (similar_word[0] not in forbidden_keywords_list) and (not similar_word[0].isdigit()):
							keyword_list.append(similar_word[0])
				except Exception as e:
					print(e)
		
			topic_keyword_dict_weekly_general[str(week)+'_'+topic] = keyword_list

		for topic_file in tqdm(filenames_new_normal):
			topic = ' '.join(re.sub('_',' ',topic_file.split('.')[0]).split()[1:])
			keyword_list_temp = []
			with open(SOURCE_new_normal + topic_file, "r") as f:
				for line in f:
					keyword_list_temp.append(sentences_cleaner(line))

			keyword_list_temp = [keyword_list_temp[i] for i in range(len(keyword_list_temp)) if keyword_list_temp[i] not in forbidden_keywords_list]

			keyword_list = keyword_list_temp.copy()

			for word in keyword_list_temp:
				try:
					similar_word_list = model.most_similar(word, topn = 10)
					for similar_word in similar_word_list:
						if (similar_word[0] not in keyword_list) and (similar_word[0] not in forbidden_keywords_list) and (not similar_word[0].isdigit()):
							keyword_list.append(similar_word[0])
				except Exception as e:
					print(e)
		
			topic_keyword_dict_weekly_new_normal[str(week)+'_'+topic] = keyword_list

	#Optimize Looping so that Only work on unique tweets
	unique_tweets_dict = {}
	df_insta_index = [i for i in range(len(df_insta))]

	tweets_list = df_insta['text'].to_list()

	for dup in list_duplicates(tweets_list):
		unique_tweets_dict[dup[0]] = dup[1]

	unique_df_insta_index = [df_insta_index[unique_tweets_dict[x][-1]] for x in unique_tweets_dict.keys()]
	length_duplicate_df_insta_index = [len(unique_tweets_dict[x]) for x in unique_tweets_dict.keys()]

	j = 0

	weekly_general_dict = {}
	weekly_new_normal_dict = {}

	for i in tqdm(unique_df_insta_index):
		dict_temp_weekly_general = {
		'user_id': df_insta.loc[i,'user_id'],
		'tweets_count': length_duplicate_df_insta_index[j],
		'week_of_the_year': df_insta.loc[i,'created_week'],
		'comments_count' : df_insta.loc[i,'comments_count'],
		'likes_count' : df_insta.loc[i,'likes_count'],
		'sentiment_score' : df_insta.loc[i,'sentiment_score']
		}

		dict_temp_weekly_new_normal = dict_temp_weekly_general.copy()

		for topic in ['confidence in government','economic policy','employment','food access','health care','health protocol','mobility','stigma']:
			if any(keyword in df_insta.loc[i,'text'] for keyword in topic_keyword_dict_weekly_general[str(dict_temp_weekly_general['week_of_the_year'])+'_'+topic]):
				dict_temp_weekly_general[topic] = 1
			else:
				dict_temp_weekly_general[topic] = 0

		for topic in ['confidence in government new normal','economic policy new normal','employment new normal','health care new normal','health protocol new normal','mobility new normal']:
			if any(keyword in df_insta.loc[i,'text'] for keyword in topic_keyword_dict_weekly_new_normal[str(dict_temp_weekly_new_normal['week_of_the_year'])+'_'+topic]):
				dict_temp_weekly_new_normal[topic] = 1
			else:
				dict_temp_weekly_new_normal[topic] = 0

		weekly_general_dict[i] = dict_temp_weekly_general

		weekly_new_normal_dict[i] = dict_temp_weekly_new_normal

		j+=1

	df_weekly_general = df_weekly_general.append(pd.DataFrame.from_dict(weekly_general_dict,orient='index'),ignore_index=True)
	df_weekly_new_normal = df_weekly_new_normal.append(pd.DataFrame.from_dict(weekly_new_normal_dict,orient='index'),ignore_index=True)
		
	df_weekly_general.to_csv('/mnt/louis/Issue Monitoring/insta_TOP_10_Evolution_Weekly_Issue_Keyword_user_level.csv',index=False)
	df_weekly_new_normal.to_csv('/mnt/louis/Issue Monitoring/insta_TOP_10_Evolution_Weekly_Issue_Keyword_user_level_new_normal.csv',index=False)


def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items())


if __name__ == '__main__':
	main()