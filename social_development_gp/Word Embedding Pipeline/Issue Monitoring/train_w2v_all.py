"""
Module to train Word2Vec in overall format based on Twitter Data
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import logging
import os
import pandas as pd
from gensim.models.word2vec import Word2Vec
from tqdm import tqdm


def main():

    logging.info('Creating Corpus...')
    corpus = create_corpus()

    logging.info('Training W2V model...')
    model = Word2Vec(corpus, sg=1, hs=1, size=300, workers=4, iter=5, min_count=15)
    logging.info('Training done.')

    # Save model
    logging.info('Saving model..')
    model.save('/mnt/louis/Issue Monitoring/model/w2v_all_300.model')
    logging.info('Done training word2vec model!')


def create_corpus():
	#Import Data
	df = pd.read_csv('/mnt/louis/Dataset/Final/agg_final_data.csv')
	df['created_at'] = pd.to_datetime(df['created_at'])
	df['created_week'] = df['created_at'].apply(lambda x: x.weekofyear)
	df = df[(df.created_week>=13)].reset_index(drop=True)

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