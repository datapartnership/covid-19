"""
Module to extract the misinformation news id related to each tweet (if any)
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""


import numpy as np
import pandas as pd
import argparse
import gensim
import time
from tqdm import tqdm
import os
from collections import defaultdict
from preprocessing_text import sentences_cleaner

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


def get_args():
    parser = argparse.ArgumentParser(description='Extract closest news')
    parser.add_argument('--type', type=str, choices=['keyword','tfidf_keyword','ngram','keyword_expanded'], required=True, help='model type')
    parser.add_argument('--start_at', type=int, default=0, help='start iteration on agg_final_data')
    return parser.parse_args()


def main():
    args = get_args()


    #Import aggregated final data
    df = pd.read_csv(SCRIPT_PATH+'/Dataset/Final/agg_final_data.csv')

    #Extract closest news id for unique tweets
    print("------------------------- Extracting Closest News ID List -------------------------")
    if args.type == 'keyword':
        unique_closest_news_id_list, unique_tweets_dict = extract_closest_news_id_by_keyword(args.start_at,type='keyword')
    elif args.type == 'tfidf_keyword':
        unique_closest_news_id_list, unique_tweets_dict = extract_closest_news_id_by_keyword(args.start_at,type='keyword',keyword_type='tfidf')
    elif args.type == 'ngram':
        unique_closest_news_id_list, unique_tweets_dict = extract_closest_news_id_by_ngram(args.start_at)
    else: #args.type == 'keyword_expanded':
        unique_closest_news_id_list, unique_tweets_dict = extract_closest_news_id_by_keyword(args.start_at,type='keyword',keyword_type='expanded')

    #Pool the unique tweets into list so it can be accessed by index
    unique_tweets_dict_keys_list = [x for x in unique_tweets_dict.keys()]

    # Transform back to the original duplicated list
    print("------------------------- Transforming to Original List -------------------------")
    closest_news_id_list = pd.Series([0 for x in range(len(df.text))])
    length = len(unique_closest_news_id_list)
    for i in tqdm(range(length)):
        closest_news_id_list[unique_tweets_dict[unique_tweets_dict_keys_list[i]]] = unique_closest_news_id_list[i]
    closest_news_id_list = closest_news_id_list.to_list()

    #Join the result into the previous data
    if args.start_at > 0:        
        full_closest_news_id_list = df.loc[:start_at,'closest_news_id_'+args.type].to_list()

        for i in range(len(closest_news_id_list)):
            full_closest_news_id_list.append(closest_news_id_list[i])
    else:
        full_closest_news_id_list = closest_news_id_list

    df['closest_news_id_'+args.type] = full_closest_news_id_list

    df.to_csv(SCRIPT_PATH+'/Dataset/Final/agg_final_data.csv',index=False)


def extract_closest_news_id_by_keyword(start_at,type,keyword_type='manual'):
    '''
    Function to extract closest news id by keyword
    '''
    #Import Tweets List
    unique_tweets_dict = {}

    df = pd.read_csv(SCRIPT_PATH+'/Dataset/Final/agg_final_data.csv')  
    tweets_list = df.loc[start_at:,'text'].to_list()

    for dup in list_duplicates(tweets_list):
        unique_tweets_dict[dup[0]] = dup[1]

    tweets_list = [tweets_list[unique_tweets_dict[x][0]] for x in unique_tweets_dict.keys()]

    #Import News List
    news_list = []
    with open(SCRIPT_PATH+"/Dataset/news_corpus.txt", "r", encoding='utf-8') as f:
        for line in f:
            news_list.append(sentences_cleaner(line))
 
    #Import News Keyword List
    news_keyword_list = []
    if keyword_type=='manual':
        news_keyword_list_path = "/mnt/louis/Dataset/news_corpus_keyword.txt"
    elif keyword_type =='W2VxKeyword':
        news_keyword_list_path = "/mnt/louis/W2VxKeyword/data/news_corpus_similar_keyword.txt"
    elif keyword_type =='tfidf':
        news_keyword_list_path = "/mnt/louis/Dataset/news_corpus_tfidf_keyword.txt"
    elif keyword_type == 'expanded':
        news_keyword_list_path = "/mnt/louis/Dataset/news_corpus_keyword_expanded.txt"

    if keyword_type != 'expanded':
        with open(news_keyword_list_path, "r", encoding='utf-8') as f:
            for line in f:
                line = line.lower()
                line = re.sub('\n','',line)
                keyword_list = line.replace(' ',',').split(',')
                keyword_list = [sentences_cleaner(x) for x in keyword_list]
                news_keyword_list.append(keyword_list)

    else: #keyword_type == 'expanded'
        news_verb_keyword_list = []
        with open(news_keyword_list_path, "r", encoding='utf-8') as f:
            for line in f:
                line = line.lower()
                line = re.sub('\n','',line)
                verb_non_verb_list = line.split(';')
                non_verb_list = verb_non_verb_list[0].split()
                non_verb_list = [sentences_cleaner(x) for x in non_verb_list]
                
                verb_non_verb_list.pop(0)

                verb_list = []
                while True:
                    if verb_non_verb_list:
                        list_tmp = verb_non_verb_list[0].split()
                        list_tmp = [sentences_cleaner(x) for x in list_tmp]
                        verb_list.append(list_tmp)
                        verb_non_verb_list.pop(0)
                    else:
                        break

                news_keyword_list.append(non_verb_list)
                news_verb_keyword_list.append(verb_list)

    if type == "W2VxBoW_key":
        #Import News Similar List
        news_similar_list = []
        with open(SCRIPT_PATH+"/Word EmbeddingxBoW/data/corpus_similar.txt", "r", encoding='utf-8') as f:
            for line in f:
                news_similar_list.append(line)
    elif type =='keyword':
        news_similar_list = news_list.copy()

    #Match keyword in each tweet and each news
    unique_closest_news_id_list = []
    for tweet in tqdm(tweets_list):
        word_list = tweet.split()
        
        rule_passed = (len(word_list)>=3) and ('pap' not in word_list) and ('vcs' not in word_list) and ('vc' not in word_list) and ('wa' not in word_list)

        if not rule_passed:
            unique_closest_news_id_list.append(-1)
        else:
            count_list = []
            i = 0
            for news_similar in news_similar_list:
                cnt = 0
                for word in word_list:
                    news_match_list = [x for x in news_similar.split() if ((x!='video') and (x!='link') and (x!='foto'))]
                    if word in news_match_list:
                        cnt+=1
                
                keyword_list = news_keyword_list[i]
                
                abbreviation_keyword_list = [keyword for keyword in keyword_list if len(keyword)<=3]


                if keyword_type == 'W2VxKeyword':

                    if 'corona' in keyword_list: #if 'corona' in keyword then check all related 'corona' keyword
                        if any(keyword in tweet for keyword in keyword_list) and (('corona' in tweet) or ('covid' in tweet) or ('covid19' in tweet) or ('covid-19' in tweet)):#if all keyword from keywords list are in this tweet then multiply the cnt by 2
                            if len(abbreviation_keyword_list)>0: #check if there is abbreviaton keyword
                                if all(keyword in word_list for keyword in abbreviation_keyword_list):
                                    count_list.append(cnt)
                                else:
                                    count_list.append(-1)
                            else:
                                count_list.append(cnt)
                        else:
                            count_list.append(-1)
                    else:
                        if any(keyword in tweet for keyword in keyword_list):#if all keyword from keywords list are in this tweet then multiply the cnt by 2
                            if len(abbreviation_keyword_list)>0: #check if there is abbreviaton keyword
                                if all(keyword in word_list for keyword in abbreviation_keyword_list):
                                    count_list.append(cnt)
                                else:
                                    count_list.append(-1)
                            else:
                                count_list.append(cnt)
                        else:
                            count_list.append(-1)

                else: #keyword_type == 'manual' or keyword_type == 'tfidf' or keyword_type == 'expanded' 

                    extra_rules_passed = True

                    if keyword_type == 'expanded':
                        verb_keyword_lists = news_verb_keyword_list[i]
                        for verb_keyword_list in verb_keyword_lists:
                            if all(verb not in tweet for verb in verb_keyword_list):
                                extra_rules_passed = False

                    if extra_rules_passed:
                        if 'corona' in keyword_list: #if 'corona' in keyword then check all related 'corona' keyword
                            if (all(keyword in tweet for keyword in keyword_list)) and (('corona' in tweet) or ('covid' in tweet) or ('covid19' in tweet) or ('covid-19' in tweet)):#if all keyword from keywords list are in this tweet then multiply the cnt by 2
                                if len(abbreviation_keyword_list)>0: #check if there is abbreviaton keyword
                                    if all(keyword in word_list for keyword in abbreviation_keyword_list):
                                        count_list.append(cnt*2)
                                    else:
                                        count_list.append(-1)
                                else:
                                    count_list.append(cnt*2)
                            else:
                                count_list.append(-1)
                        else:
                            if (all(keyword in tweet for keyword in keyword_list)):#if all keyword from keywords list are in this tweet then multiply the cnt by 2
                                if len(abbreviation_keyword_list)>0: #check if there is abbreviaton keyword
                                    if all(keyword in word_list for keyword in abbreviation_keyword_list):
                                        count_list.append(cnt*2)
                                    else:
                                        count_list.append(-1)
                                else:
                                    count_list.append(cnt*2)
                            else:
                                count_list.append(-1)

                    else:
                        count_list.append(-1)
                
                i+=1 #iteration of keyword / verb_keyword list

            if (keyword_type=='W2VxKeyword') and (not (any(i>(len(word_list)//3) for i in count_list))):
                unique_closest_news_id_list.append(-1)
            else:       
                #check if the proposed tweet contain strict word (region, organization, position) like the news (not news_similar) did
                check_tweet_news_strict_word = find_words_in_strict_word_list(news_list[np.argmax(count_list)].split())
                if len(check_tweet_news_strict_word)>0: 
                    if all(word in word_list for word in check_tweet_news_strict_word):
                        unique_closest_news_id_list.append(np.argmax(count_list))
                    else:
                        unique_closest_news_id_list.append(-1)
                else:
                    unique_closest_news_id_list.append(np.argmax(count_list))
 
    return unique_closest_news_id_list, unique_tweets_dict


def extract_closest_news_id_by_ngram(start_at):
    '''
    Function to extract closest news id by n-gram matching
    '''
    #Import Tweets List
    unique_tweets_dict = {}

    df = pd.read_csv(SCRIPT_PATH+'/Dataset/Final/agg_final_data.csv')  
    tweets_list = df.loc[start_at:,'text'].to_list()

    for dup in list_duplicates(tweets_list):
        unique_tweets_dict[dup[0]] = dup[1]

    tweets_list = [tweets_list[unique_tweets_dict[x][0]] for x in unique_tweets_dict.keys()]

    #Import News List
    news_list = []
    with open(SCRIPT_PATH+"/Dataset/news_corpus.txt", "r", encoding='utf-8') as f:
        for line in f:
            news_list.append(sentences_cleaner(line))

    #Import News Keyword List
    news_keyword_lists = []
    with open("/mnt/louis/Dataset/news_corpus_keyword.txt", "r", encoding='utf-8') as f:
        for line in f:
            line = line.lower()
            line = re.sub('\n','',line)
            keyword_list = line.replace(' ',',').split(',')
            news_keyword_lists.append(keyword_list)

    #Extract bigram and trigram for each news
    news_bigram_lists = []
    news_trigram_lists = []
    for news in news_list:
        news_word_list = [x for x in news.split() if ((x!='video') and (x!='link') and (x!='foto'))]
        news_bigram_lists.append(extract_bigrams(news_word_list))
        news_trigram_lists.append(extract_trigrams(news_word_list))

    #Match bigram & trigram in each tweet and each news
    unique_closest_news_id_list = []

    for tweet in tqdm(tweets_list):
        word_list = tweet.split()
        
        rule_passed = (len(word_list)>=3) and ('pap' not in word_list) and ('vcs' not in word_list) and ('vc' not in word_list) and ('wa' not in word_list)

        if not rule_passed:
            unique_closest_news_id_list.append(-1)
        else:
            count_list = []
            bigram_list = extract_bigrams(word_list)
            trigram_list = extract_trigrams(word_list)
            for i in range(len(news_list)):
                cnt_word = 0
                cnt_bigram = 0
                cnt_trigram = 0
                news_keyword_list = news_keyword_lists[i]
                news_bigram_list = news_bigram_lists[i]
                news_trigram_list = news_trigram_lists[i]

                for word in news_keyword_list:
                    if word=='corona':
                        if ('corona' in tweet) or ('covid' in tweet) or ('covid19' in tweet) or ('covid-19' in tweet):
                            cnt_word+=1
                    else:
                        if len(word)>3: 
                            if (word in tweet) and (not word.isdigit()):
                                cnt_word+=1
                        else: #Abbreviation Word
                            if (word in word_list) and (not word.isdigit()):
                                cnt_word+=1

                for bigram in news_bigram_list:
                    if (bigram in bigram_list) and (not any(word.isdigit() for word in bigram.split())) and ('corona' not in bigram) and ('covid' not in bigram) and ('covid19' not in bigram) and ('covid-19' not in bigram):
                        cnt_bigram+=1

                for trigram in news_trigram_list:
                    if (trigram in trigram_list) and (not any(word.isdigit() for word in trigram.split())) and ('corona' not in trigram) and ('covid' not in trigram) and ('covid19' not in trigram) and ('covid-19' not in trigram):
                        cnt_trigram+=1

                if (cnt_word > len(news_keyword_list)*7//8) and (cnt_bigram >= 2) and (cnt_trigram >= 1):
                    count_list.append(cnt_word + cnt_bigram + cnt_trigram)
                else:
                    count_list.append(0)

            if any(cnt>0 for cnt in count_list):
                unique_closest_news_id_list.append(np.argmax(count_list))
            else:
                unique_closest_news_id_list.append(-1)
 
    return unique_closest_news_id_list, unique_tweets_dict


def extract_bigrams(word_list):
    '''
    Function to generate bigram list
    '''
    a = word_list
    b = a[1:]
    bigrams_list = []

    for i in range(len(b)):
        bigrams_list.append(a[i].lower() + ' ' + b[i].lower())

    return bigrams_list


def extract_trigrams(word_list):
    '''
    Function to generate bigram list
    '''
    a = word_list
    b = a[1:]
    c = a[2:]
    trigrams_list = []

    for i in range(len(c)):
        trigrams_list.append(a[i].lower() + ' ' + b[i].lower() + ' ' + c[i].lower())

    return trigrams_list


def find_words_in_strict_word_list(lst):
	'''
	Function to find the word in the given list which is contains in the strict_world_list
	'''
	output = []

	for wrd in lst:
		if wrd in strict_word_list:
			output.append(wrd)

	return output


def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items())


#---------------------------------------------------------------------------------------------------------
with open(SCRIPT_PATH+"/Supporting Files/combined_position_degree_words.txt") as f:
    position_degree_words_list = f.read().splitlines()

position_degree_words_list = [x.lower() for x in position_degree_words_list]

with open(SCRIPT_PATH+"/Supporting Files/combined_region_words.txt") as f:
    region_words_list = f.read().splitlines()

region_words_list = [x.lower() for x in region_words_list]

with open(SCRIPT_PATH+"/Supporting Files/organization_words.txt") as f:
    organization_words_list = f.read().splitlines()

organization_words_list = [x.lower() for x in organization_words_list]


strict_word_list = position_degree_words_list.copy()

for word in region_words_list:
	strict_word_list.append(word)

for word in organization_words_list:
	strict_word_list.append(word)


if __name__ == '__main__':
    main()