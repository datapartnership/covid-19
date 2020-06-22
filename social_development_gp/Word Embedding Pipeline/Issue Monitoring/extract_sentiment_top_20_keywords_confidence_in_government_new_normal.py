"""
Module to extract sentiment for top 20 new normal keywords
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import pandas as pd
import os
import datetime
from tqdm import tqdm
tqdm.pandas()

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
factory = StemmerFactory()
stemmer = factory.create_stemmer()

def main():
	#Extract New Normal Keyword List
	forbidden_keywords_list = []
	with open('/mnt/louis/Issue Monitoring/forbidden_keywords.txt','r') as f:
		for line in f:
			forbidden_keywords_list.append(re.sub('\n','',line).lower())

	SOURCE_new_normal = '/mnt/louis/Issue Monitoring/topic/new_normal/'
	_,_,filenames_new_normal = next(os.walk(SOURCE_new_normal))

	new_normal_keyword_list = []

	for topic_file in filenames_new_normal:
		with open(SOURCE_new_normal + topic_file, "r") as f:
			for line in f:
				new_normal_keyword_list.append(sentences_cleaner(line))

	new_normal_keyword_list = [new_normal_keyword_list[i] for i in range(len(new_normal_keyword_list)) if new_normal_keyword_list[i] not in forbidden_keywords_list]


	#Import and Prep on TOP_10_Evolution_Weekly_Similar_Issue_Keyword.csv
	df_weekly = pd.read_csv('/mnt/louis/Issue Monitoring/TOP_10_Evolution_Weekly_Similar_Issue_Keyword.csv')

	df_weekly = df_weekly[df_weekly['week_of_the_year']>=13]

	#Filter only new normal keyword list
	df_weekly = df_weekly[df_weekly['keyword'].isin(new_normal_keyword_list)].reset_index(drop=True)

	df_weekly_prepared = pd.DataFrame(columns=['keyword','count'])
	df_temp = df_weekly[df_weekly.topic=='confidence in government'].reset_index(drop=True)
	for i in range(len(df_temp)):
		df_weekly_prepared = df_weekly_prepared.append({'keyword':df_temp.loc[i,'keyword'],'count':df_temp.loc[i,'keyword_count']},ignore_index=True)

		df_weekly_prepared = df_weekly_prepared.append({'keyword':df_temp.loc[i,'similar_keyword'],'count':df_temp.loc[i,'similar_keyword_count']},ignore_index=True)

	df_weekly_prepared = df_weekly_prepared.drop_duplicates()

	#Filter out inappropriate similar keywords
	exclude_keyword_list = ['roti','tawar','meses','ikan']
	df_weekly_prepared = df_weekly_prepared[~df_weekly_prepared['keyword'].isin(exclude_keyword_list)]


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

	df_sentiment.to_csv('/mnt/louis/Issue Monitoring/sentiment_top_20_keywords_confidence_in_government_new_normal.csv',index=False)


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

#------------------------------------------------------------------------------------------

import random
import re
import pandas as pd
import numpy as np
import json
import string
from tqdm import tqdm

with open("/mnt/louis/Supporting Files/combined_slang_words.txt") as f:
    slang_words_dict = json.load(f)

with open("/mnt/louis/Supporting Files/combined_stop_words.txt") as f:
    stop_words_list = f.read().splitlines()


def deEmojify(inputString):
    '''
    Function to remove emoji
    '''
    return inputString.encode('ascii', 'ignore').decode('ascii')


def isfloat(value):
    ''' 
    Check if value is float or not
    '''
    try:
        float(value)
        return True
    except ValueError:
        return False


def elongated_word(word):
    """
    Replaces an elongated word with its basic form, unless the word exists in the lexicon 
    """
    count = {}
    for s in word:
        if s in count:
            count[s] += 1
        else:
            count[s] = 1

    for key in count:
        if count[key]>2:
            return ''
            break
    
    return word


def word_cleaner(word):
    '''
    clean input word
    '''
    #Transfrom slang word into its normal words based on slang_words corpus
    if word in slang_words_dict.keys():
        word = slang_words_dict[word]

    #Transform elongated word to normal word
    if (not isfloat(word)) and (word!=''):
        word = elongated_word(word)

    return word


def sentences_cleaner(sentence):
    '''
    clean input sentence  
    '''
    mention_pat= r'@[A-Za-z0-9_]+'
    mention_2_pat=r'@[A-Za-z0-9_]+:\s'
    http_pat = r'https?://[^ ]+'
    www_pat = r'www.[^ ]+'
    hashtag_pat = r'#[A-Za-z0-9_]+'
    linebreak_pat = r'\n'

    #Remove Emoji
    stripped = deEmojify(sentence)

    #Delete mention
    stripped = re.sub(mention_2_pat,'', stripped)
    stripped = re.sub(mention_pat,'', stripped)

    #Remove url
    stripped = re.sub(http_pat, '', stripped)
    stripped = re.sub(www_pat, '', stripped)

    #Remove hashtag
    stripped = re.sub(hashtag_pat, '', stripped)

    #Remove linebreak
    stripped = re.sub(linebreak_pat,'',stripped)

    #Remove Punctuation
    stripped = [re.sub(r'[^\w\s]',' ',x) for x in stripped.split(string.punctuation)][0]

    #Remove Non Alphabet and Non Number Characters
    stripped = re.sub(' +',' ',re.sub(r'[^a-zA-Z-0-9]',' ',stripped)).strip()

    #Lowercase 
    stripped = stripped.lower()

    #Clean word by word
    stripped = ' '.join(pd.Series(stripped.split()).apply(lambda x: word_cleaner(x)).to_list())

    #remove stop words
    lst = pd.Series(stripped.split()).apply(lambda x: 'stopword' if x in stop_words_list else x).to_list()
    lst = [wrd for wrd in lst if wrd!='stopword']
    stripped = ' '.join(lst)

    # #Stem each word
    # stripped = stemmer.stem(stripped)

    # #Sanity check using Kateglo API
    # check = pd.Series(stripped.split()).apply(lambda x: check_kateglo(x)).to_list()
    # check = [wrd for wrd in check if wrd!='']
    # stripped = ' '.join(check)

    return re.sub(' +',' ',stripped).strip()


if __name__ == "__main__":
	main()