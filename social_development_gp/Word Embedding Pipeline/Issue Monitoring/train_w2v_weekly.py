"""
Module to train Word2Vec in weekly format based on Twitter Data
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import logging
import os
import pandas as pd
from gensim.models.word2vec import Word2Vec
from tqdm import tqdm
import argparse


def get_args():
    parser = argparse.ArgumentParser(description='Data Preprocessing')
    parser.add_argument('--start_week', type=int, required=True, help='Starting Week')
    return parser.parse_args()


def main():
    args = get_args()
    #Import Data
    df = pd.read_csv('/mnt/louis/Dataset/Final/agg_final_data.csv')
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['created_week'] = df['created_at'].apply(lambda x: x.weekofyear)
    df = df[(df.created_week>=args.start_week)].reset_index(drop=True)
    unique_week_list = list(df['created_week'].unique())

    for week in unique_week_list:
        logging.info('Creating Corpus for week {}'.format(week))
        corpus = create_corpus(df[df['created_week']==week])

        if len(corpus) < 100:
            min_count = 1
            iteration = 20
        elif len(corpus) < 500:
            min_count = 2
            iteration = 18
        elif len(corpus) < 1000:
            min_count = 2
            iteration = 15
        elif len(corpus) < 5000:
            min_count = 2
            iteration = 13
        elif len(corpus) < 10000:
            min_count = 2
            iteration = 10
        elif len(corpus) < 25000:
            min_count = 2
            iteration = 8
        elif len(corpus) < 50000:
            min_count = 5
            iteration = 8
        else:
            min_count = 8
            iteration = 5

        logging.info('Training W2V model for week {}'.format(week))
        model = Word2Vec(corpus, sg=1, hs=1, size=300, workers=2, iter=iteration, min_count=min_count)
        logging.info('Training done.')

        # Save model
        logging.info('Saving model for week {}'.format(week))
        model.save('/mnt/louis/Issue Monitoring/model/w2v_week_{}_300.model'.format(week))
        logging.info('Done training word2vec model for week {}!'.format(week))
        

def create_corpus(df):
	tweets_list = df['text'].to_list()

	corpus = []

	for tweet in tqdm(tweets_list):
		#Unigram
		word_list = tweet.split()
		corpus.append(word_list)

		#Bigram
		bigram_list = []

		b = word_list[1:]

		for i in range(len(b)):
			bigram = word_list[i] + ' ' + b[i]
			if bigram not in bigram_list:
				bigram_list.append(bigram)

		corpus.append(bigram_list)

		#Trigram
		trigram_list = []

		c = word_list[2:]

		for i in range(len(c)):
			trigram = word_list[i] + ' ' + b[i] + ' ' + c[i]
			if trigram not in trigram_list:
				trigram_list.append(trigram)

		corpus.append(trigram_list)

	return corpus


if __name__ == "__main__":
    logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.INFO)
    os.makedirs('Issue Monitoring/model/', exist_ok=True)
    main()