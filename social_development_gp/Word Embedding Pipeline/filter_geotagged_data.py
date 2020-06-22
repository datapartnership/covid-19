"""
Module to filter out geotagged data which not covid-related tweets
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import json
import ast
import os
from tqdm import tqdm
import argparse
import re
from preprocessing_text import sentences_cleaner


def get_args():
    parser = argparse.ArgumentParser(description='Data Preprocessing')
    parser.add_argument('--file_name', type=str, required=True, help='input file name')
    return parser.parse_args()


def main():
    args = get_args()

    cnt = 0
    i = 1
    thres = 0
    if os.path.exists(SCRIPT_PATH+'/Dataset/Raw/filtered_'+args.file_name+'.txt'):
        with open(SCRIPT_PATH+'/Dataset/Raw/filtered_'+args.file_name+'.txt','r') as f:
            for line in f:
                thres+=1

    with open(PATH_TO_DATASET+args.file_name+'.txt','r') as f:
        for line in tqdm(f):
            if i > thres:
                try: #in case there are tweets which not well-formatted and make ast failed to compile
                    tweet = ast.literal_eval(line)
                    try:
                        if tweet['place']['country_code']=='ID': #Because there is non-ID tweet
                            try: #to get the full version of the tweets if it is a retweeted text
                                text = sentences_cleaner(tweet['retweeted_status']['extended_tweet']['full_text'])
                                tweet['retweeted_status']['extended_tweet']['full_text'] = text
                            except:
                                try:
                                    text = sentences_cleaner(tweet['retweeted_status']['text'])
                                    tweet['retweeted_status']['text'] = text
                                except:
                                    try:
                                        text = sentences_cleaner(tweet['extended_tweet']['full_text'])
                                        tweet['extended_tweet']['full_text'] = text
                                    except:
                                        text = sentences_cleaner(tweet['text'])
                                        tweet['text'] = text

                            text_list = text.split()

                            # #filter tweets based on chosen keywords
                            if any(x in text_list for x in keyword_list):
                                with open(SCRIPT_PATH+'/Dataset/Raw/filtered_'+args.file_name+'.txt','a+') as f_out:
                                    json.dump(tweet,f_out)
                                    f_out.write('\n')
                                
                    except: #No Geo Tagged Info
                        pass
                except:
                    cnt+=1
                    print(cnt)

            i+=1

#---------------------------------------------------------------------------------------------------------

forbidden_keywords_list = []
with open('/mnt/louis/Issue Monitoring/forbidden_keywords.txt','r') as f:
    for line in f:
        forbidden_keywords_list.append(re.sub('\n','',line).lower())
forbidden_keywords_list.append('')
forbidden_keywords_list.append('covid19')


PATH_TO_DATASET = '/mnt/twitter_geolocation_data/'
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


SOURCE_general = '/mnt/louis/Issue Monitoring/topic/general/'
_,_,filenames_general = next(os.walk(SOURCE_general))

#Iterate through all topics corpus
keyword_list = []

for topic_file in filenames_general:
    with open(SOURCE_general + topic_file, "r") as f:
        for line in f:
            keyword_list.append(sentences_cleaner(line))

keyword_list = [keyword_list[i] for i in range(len(keyword_list)) if keyword_list[i] not in forbidden_keywords_list]
keyword_list.append('covid19')
keyword_list.append('corona')
keyword_list.append('coronavirus')
keyword_list.append('korona')
keyword_list.append('covid')
keyword_list.append('virus')


if __name__ == '__main__':
    main()

