"""
Module to extract sentiment for top 10 retweeted/replied users in each topic
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import argparse
import pandas as pd
import re
from tqdm import tqdm
tqdm.pandas()

from collections import defaultdict

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
factory = StemmerFactory()
stemmer = factory.create_stemmer()

def get_args():
    parser = argparse.ArgumentParser(description='Sentiment Analysis on TOP Users')
    parser.add_argument('--criteria', choices=['retweet','reply'], required=True, help='Order Criteria')
    return parser.parse_args()


def main():
	args = get_args()

	topic_list = ['confidence in government','economic policy','employment','food access','health care','health protocol','mobility','stigma']

	#Specify desired columns to be imported
	columns = ['user_id','confidence in government','economic policy','employment','food access','health care','health protocol','mobility','stigma']
	if args.criteria=='retweet':
		order_criteria = 'retweet_count'
		columns.append(order_criteria)
	else:
		order_criteria = 'reply_count'
		columns.append(order_criteria)		

	#Import and Prep on TOP_10_Evolution_Weekly_Issue_Keyword_user_level.csv
	df = pd.read_csv("/mnt/louis/Issue Monitoring/TOP_10_Evolution_Weekly_Issue_Keyword_user_level.csv",usecols=columns)


	print('---------------------Import Twitter user_id mapping')
	#Import Twitter user_id mapping
	twitter_user_id_mapping_dict={}
	with open("/mnt/kiran/all_users_profiles_twitter.txt","r") as f:
		for line in f:
			if (line.split('\t')[0]).isdigit():
				twitter_user_id_mapping_dict[line.split('\t')[0]] = re.sub('\n','',line.split('\t')[1]) 


	print('---------------------Extract Top 10 Users for Each Topic')
	#Get the top 10 users for each topic
	top_10_users_dict = {}

	forbidden_users = {
	'confidence in government' : ['NadimMakarim','VVIPTerlengkap'],
	'economic policy' : ['ArnoldPoernomo','G_ShalzaJKT48','handokotjung'],
	'employment' : ['NadimMakarim','thesandblazt','radenrauf','SMTOWN_Idn'],
	'food access' : ['KAI121','JeniusConnect','SMTOWN_Idn','NadimMakarim','radenrauf','ArnoldPoernomo'],
	'health care' : ['goodghan'],
	'health protocol' : ['VVIPTerlengkap','ArnoldPoernomo','SMTOWN_Idn','smartfrenworld'],
	'mobility' : ['thesandblazt','radenrauf','SMTOWN_Idn','tokopedia'],
	'stigma' : ['thesandblazt','radenrauf']
	}

	for topic in tqdm(topic_list):	
		sentiment_dict = {}

		df_temp = df[df[topic]==1][['user_id',order_criteria]]
		group_by_object = df_temp.groupby('user_id')
		top_30_user_id_list = group_by_object.sum()[[order_criteria]].reset_index().sort_values(order_criteria,ascending=False).head(30)['user_id'].to_list()
		
		top_10_user_id_list = []
		while True:
			if (str(top_30_user_id_list[0]) in twitter_user_id_mapping_dict) and (twitter_user_id_mapping_dict[str(top_30_user_id_list[0])] not in forbidden_users[topic]):
				top_10_user_id_list.append(top_30_user_id_list[0])
			
			if len(top_10_user_id_list) == 10:
				break

			top_30_user_id_list.pop(0)

		top_10_users_dict[topic] = top_10_user_id_list


	print('---------------------Extract Keywords for Each Topic')
	#Import and Prep on TOP_10_Evolution_Weekly_Similar_Issue_Keyword.csv
	df_weekly = pd.read_csv('/mnt/louis/Issue Monitoring/TOP_10_Evolution_Weekly_Similar_Issue_Keyword.csv',usecols=['topic','keyword','similar_keyword','week_of_the_year'])
	df_weekly = df_weekly[df_weekly['week_of_the_year']>=13]

	df_weekly_prepared = pd.DataFrame(columns=['topic','keyword'])
	for topic in tqdm(topic_list):
		df_temp = df_weekly[df_weekly.topic==topic].reset_index(drop=True)
		
		for i in range(len(df_temp)):
			df_weekly_prepared = df_weekly_prepared.append({'topic':topic,'keyword':df_temp.loc[i,'keyword']},ignore_index=True)

			df_weekly_prepared = df_weekly_prepared.append({'topic':topic,'keyword':df_temp.loc[i,'similar_keyword']},ignore_index=True)

	df_weekly_prepared = df_weekly_prepared.drop_duplicates()


	print('---------------------Create Dictionary of Keyword for each topic')
	#Create Dictionary of Keyword for each topic
	topic_keyword_dict = {}
	for topic in tqdm(topic_list):
		topic_keyword_dict[topic] = df_weekly_prepared[df_weekly_prepared['topic']==topic]['keyword'].to_list()


	print('---------------------Import Tweets Corpus')
	#Import tweets corpus
	df_tweets = pd.read_csv('/mnt/louis/Dataset/Final/agg_final_data.csv',usecols=['created_at','text','user_id',order_criteria])
	df_tweets['created_at'] = pd.to_datetime(df_tweets['created_at'])
	df_tweets['created_week'] = df_tweets['created_at'].apply(lambda x: x.weekofyear)
	df_tweets = df_tweets[(df_tweets.created_week>=13)].reset_index(drop=True)


	print('---------------------Extract Sentiment Score through each topic for the top 10 users')
	#Initialize dataframe to store sentiment score information
	df_sentiment = pd.DataFrame(columns = ['topic','user_id','sentiment_score'])

	#Initialize dataframe to store top tweet information
	df_top_tweet = pd.DataFrame(columns=['topic','user_id','top_tweet'])

	#Extract Sentiment Score through each topic for the top 10 users
	for topic in topic_list:
		print('-----------------Extracting Topic: {}'.format(topic))

		top_10_user_id_list = top_10_users_dict[topic]

		df_temp = df_tweets[df_tweets['user_id'].isin(top_10_user_id_list)][['user_id','text',order_criteria]]

		df_temp = df_temp.sort_values(by=[order_criteria],ascending=False)

		df_temp = df_temp[['user_id','text']].drop_duplicates()

		df_temp[topic] = df_temp['text'].apply(lambda x: 1 if any(keyword in x for keyword in topic_keyword_dict[topic]) else 0)

		df_temp = df_temp[df_temp[topic]==1].reset_index(drop=True)

		user_id_list = df_temp['user_id'].apply(lambda x: twitter_user_id_mapping_dict[str(x)]).to_list()

		print('-------------Stemming Word')
		df_temp['text'] = df_temp['text'].progress_apply(lambda x: stemmer.stem(x))
		sentiment_score_list =  df_temp['text'].apply(lambda x: extract_sentiment(x)).to_list()

		print('-------------Appending Data to Dataframe')
		for i in range(len(user_id_list)):
			sentiment_dict = {
			'topic' : topic,
			'user_id' : user_id_list[i],
			'sentiment_score' : sentiment_score_list[i]
			}

			df_sentiment = df_sentiment.append(sentiment_dict,ignore_index=True)


		print('-------------Extracting Top Tweet through each topic for the top 10 users')
		top_tweeted_idx_list = []

		for dup in list_duplicates(user_id_list):
			top_tweeted_idx_list.append(dup[1][0])

		df_top_tweet_temp = df_temp.loc[top_tweeted_idx_list].reset_index(drop=True)

		for i in range(len(top_tweeted_idx_list)):
			tweet_dict = {
			'topic' : topic,
			'user_id' : twitter_user_id_mapping_dict[str(df_top_tweet_temp.loc[i,'user_id'])],
			'top_tweet' : df_top_tweet_temp.loc[i,'text']
			}

			df_top_tweet = df_top_tweet.append(tweet_dict,ignore_index=True)


	df_top_tweet.to_csv('/mnt/louis/Issue Monitoring/top_tweet_top_10_{}_users.csv'.format(args.criteria),index=False)


	df_sentiment.to_csv('/mnt/louis/Issue Monitoring/sentiment_top_10_{}_users.csv'.format(args.criteria),index=False)


	print('---------------------Extract Tweets Percentage for each of the top 10 users')
	col_percentage_tweets = topic_list.copy()
	col_percentage_tweets.append('user_id')
	df_percentage_tweets = pd.DataFrame(columns=col_percentage_tweets)

	#Combine All Top 10 Users from All Topic
	all_top_10_user_id_list = []

	for topic in topic_list:
		top_10_user_id_list = top_10_users_dict[topic]
		for user_id in top_10_user_id_list:
			if user_id not in all_top_10_user_id_list:
				all_top_10_user_id_list.append(user_id)

	for user_id in all_top_10_user_id_list:
		df_temp = df_tweets[df_tweets['user_id']==user_id][['user_id','text']]

		df_temp = df_temp[['user_id','text']].drop_duplicates()

		tweet_percentage_dict = {'user_id' : twitter_user_id_mapping_dict[str(user_id)]}

		for topic in topic_list:
			is_topic = df_temp['text'].apply(lambda x: 1 if any(keyword in x for keyword in topic_keyword_dict[topic]) else 0)
			tweet_percentage_dict[topic] = is_topic.sum()

		df_percentage_tweets = df_percentage_tweets.append(tweet_percentage_dict,ignore_index=True)

	df_percentage_tweets.to_csv('/mnt/louis/Issue Monitoring/tweets_percentage_top_10_{}_users.csv'.format(args.criteria),index=False)


def extract_sentiment(sentence):
	'''
	Function to extract sentiment from sentence based on positive and negative corpus
	'''
	sentiment_series = pd.Series(sentence.split()).apply(lambda x: 1 if x in positive_words_list else -1 if x in negative_words_list else 0)

	return sentiment_series.mean()


def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items())


with open("/mnt/louis/Supporting Files/combined_positive_words.txt") as f:
    positive_words_list = f.read().splitlines()

with open("/mnt/louis/Supporting Files/combined_negative_words.txt") as f:
    negative_words_list = f.read().splitlines()


if __name__ == '__main__':
	main()


