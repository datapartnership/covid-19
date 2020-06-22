"""
Module to train Word2Vec in overall format based on Instagram Data
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import logging
import os
import pandas as pd
from gensim.models.word2vec import Word2Vec
from tqdm import tqdm


def create_corpus():
	#Import Data
	df = pd.read_csv('/mnt/louis/Dataset/Instagram/Final/agg_final_data_insta.csv',usecols=['created_at','text'])
	df['created_at'] = pd.to_datetime(df['created_at'])
	df['created_week'] = df['created_at'].apply(lambda x: x.weekofyear)
	df = df[(df.created_week>=13)].reset_index(drop=True)

	text_list = df['text'].to_list()

	corpus = []

	for text in tqdm(text_list):
		#Unigram
		word_list = text.split()
		corpus.append(word_list)

		#Bigram
		bigram_list = []

		b = word_list[1:]

		for i in range(len(b)):
			bigram = word_list[i] + ' ' + b[i]
			if bigram not in bigram_list:
				bigram_list.append(bigram)

		corpus.append(bigram_list)

	return corpus


def main():

    logging.info('Creating Corpus...')
    corpus = create_corpus()

    logging.info('Training W2V model...')
    model = Word2Vec(corpus, sg=1, hs=1, size=300, workers=4, iter=5, min_count=15)
    logging.info('Training done.')

    # Save model
    logging.info('Saving model..')
    model.save('/mnt/louis/Issue Monitoring/model/w2v_insta_all_300.model')
    logging.info('Done training word2vec model!')


if __name__ == "__main__":
    logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.INFO)
    os.makedirs('Issue Monitoring/model/', exist_ok=True)
    main()