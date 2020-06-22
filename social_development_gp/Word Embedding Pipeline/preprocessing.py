"""
Module to do preprocessing on twitter data
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import os
import argparse
from tqdm import tqdm
import json
import string
import ast
from preprocessing_text import sentences_cleaner


SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH  = os.path.join(SCRIPT_PATH, 'Dataset/')


def get_args():
    parser = argparse.ArgumentParser(description='Data Preprocessing')
    parser.add_argument('--iter', type=int, required=True, help='Iteration Number of Tweets need to be processed')
    parser.add_argument('--file_name', type=str, required=True, help='input file name')
    parser.add_argument('--type', choices=['hashtag','geo'], required=True,default='hashtag', help='type of tweets')
    return parser.parse_args()


def main():
	args = get_args()

	i = 1

	if args.type == 'geo':
		root_path = SCRIPT_PATH+'/Dataset/Raw/'
	else:
		root_path = '/mnt/twitter_hashtag_data/' 


	thres = 0
	if os.path.exists(DATA_PATH+'Cleaned/'+"cleaned_tweets_{}.txt".format(args.iter)):
		with open(DATA_PATH+'Cleaned/'+"cleaned_tweets_{}.txt".format(args.iter),"r") as f:
			for line in f:
				thres +=1

	with open(root_path+args.file_name+'.txt','r') as f:
		for line in tqdm(f):
			if i > thres:
				try: #in case there are tweets which not well-formatted and make ast failed to compile
					try:
						tweet = ast.literal_eval(line)
					except:
						tweet = json.loads(line)

					json_output = {}

					try: #to get the full version of the tweets if it is a retweeted text
						text = tweet['retweeted_status']['extended_tweet']['full_text']
						json_output['hashtags'] = tweet['retweeted_status']['extended_tweet']['entities']['hashtags']
					except:
						try:
							text = tweet['retweeted_status']['text']
							json_output['hashtags'] = tweet['retweeted_status']['entities']['hashtags']
						except:
							try: #to get the full version of the tweets
								text = tweet['extended_tweet']['full_text']
								json_output['hashtags'] = tweet['extended_tweet']['entities']['hashtags']
							except:
								text = tweet['text']
								json_output['hashtags'] = tweet['entities']['hashtags']

					if args.type == 'hashtag':
						json_output['text'] = sentences_cleaner(text)
					else:
						json_output['text'] = text

					if json_output['text'] != '':
						try:
							json_output['created_at'] = tweet['retweeted_status']['created_at']
						except:
							json_output['created_at'] = tweet['created_at']

						try:
							json_output['location'] = tweet['retweeted_status']['place']['full_name'].split(',')[0]
						except:
							try:
								json_output['location'] = tweet['retweeted_status']['place']
							except:
								try:
									json_output['location'] = tweet['place']['full_name'].split(',')[0]
								except:
									json_output['location'] = tweet['place']

						try:
							json_output['tweet_id'] = tweet['retweeted_status']['id_str']
							json_output['user_id'] = tweet['retweeted_status']['user']['id_str']
							json_output['verified'] = tweet['retweeted_status']['user']['verified']
							json_output['reply_count'] = tweet['retweeted_status']['reply_count']
							json_output['retweet_count'] = tweet['retweeted_status']['retweet_count']
							json_output['favorite_count'] = tweet['retweeted_status']['favorite_count']
						except:
							json_output['tweet_id'] = tweet['id_str']
							json_output['user_id'] = tweet['user']['id_str']
							json_output['verified'] = tweet['user']['verified']
							json_output['reply_count'] = tweet['reply_count']
							json_output['retweet_count'] = tweet['retweet_count']
							json_output['favorite_count'] = tweet['favorite_count']
					

						with open(DATA_PATH+'Cleaned/'+"cleaned_tweets_{}.txt".format(args.iter),'a+') as f_out:
							json.dump(json_output,f_out)
							f_out.write('\n')
				
				except Exception as e:
					print(e)
			i+=1
	
	
if __name__ == '__main__':

	main()

	


