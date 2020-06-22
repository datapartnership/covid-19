"""
Module to extract URL from tweets corpus
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import os
import argparse
import re
import json
import ast
from tqdm import tqdm
from preprocessing_text import sentences_cleaner


def get_args():
    parser = argparse.ArgumentParser(description='Data Preprocessing')
    parser.add_argument('--file_name', type=str, required=True, help='input file name')
    parser.add_argument('--type', choices=['hashtag','geo'], required=True,default='hashtag', help='type of tweets')
    return parser.parse_args()

def main():
	args = get_args()

	if args.type == 'geo':
		root_path = '/mnt/louis/Dataset/Raw/'
	else:
		root_path = '/mnt/twitter_hashtag_data/' 

	with open(root_path+args.file_name+'.txt','r') as f:
		for line in tqdm(f):
			try: #in case there are tweets which not well-formatted and make ast failed to compile
				try:
					tweet = ast.literal_eval(line)
				except:
					tweet = json.loads(line)

				try: #to get the full version of the tweets if it is a retweeted text				
					urls = tweet['retweeted_status']['extended_tweet']['entities']['urls']
					if urls:
						created_at = tweet['created_at']
						text = sentences_cleaner(tweet['retweeted_status']['extended_tweet']['full_text'])
						line = created_at + ',' + text  
						for i in range(len(urls)):
							url = urls[i]['expanded_url']
							if 'twitter' not in url:
								line += ',' + url

						with open("/mnt/louis/Dataset/tweet_URL_list.txt","a+") as f_out:
							f_out.write(line+'\n')
				except:
					try:
						urls = tweet['retweeted_status']['entities']['urls']
						if urls:
							created_at = tweet['created_at']
							text = sentences_cleaner(tweet['retweeted_status']['text'])
							line = created_at + ',' + text  
							for i in range(len(urls)):
								url = urls[i]['expanded_url']
								if 'twitter' not in url:
									line += ',' + url

							with open("/mnt/louis/Dataset/tweet_URL_list.txt","a+") as f_out:
								f_out.write(line+'\n')
					except:
						try: 
							urls = tweet['extended_tweet']['entities']['urls']
							if urls:
								created_at = tweet['created_at']
								text = sentences_cleaner(tweet['extended_tweet']['full_text'])
								line = created_at + ',' + text
								for i in range(len(urls)):
									url = urls[i]['expanded_url']
									if 'twitter' not in url:
										line += ',' + url

								with open("/mnt/louis/Dataset/tweet_URL_list.txt","a+") as f_out:
									f_out.write(line+'\n')
						except:
							urls = tweet['entities']['urls']
							if urls:
								created_at = tweet['created_at']
								text = sentences_cleaner(tweet['text'])
								line = created_at + ',' + text
								for i in range(len(urls)):
									url = urls[i]['expanded_url']
									if 'twitter' not in url:
										line += ',' + url

								with open("/mnt/louis/Dataset/tweet_URL_list.txt","a+") as f_out:
									f_out.write(line+'\n')

			except Exception as e:
				print(e)


if __name__ == '__main__':
	main()