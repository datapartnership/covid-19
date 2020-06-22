"""
Module to extract verb from the misinformation news corpus
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

from preprocessing_text import sentences_cleaner

from flair.data_fetcher import NLPTaskDataFetcher, NLPTask
from flair.data import Sentence
from flair.embeddings import TokenEmbeddings, WordEmbeddings, StackedEmbeddings, BertEmbeddings
from flair.trainers import ModelTrainer
from flair.models import SequenceTagger
from typing import List


def main():

    #Uncomment this block of code if you haven't train the POS-tagging model

    # # 1. get the corpus
    # corpus = NLPTaskDataFetcher.load_corpus(NLPTask.UD_INDONESIAN)

    # # 2. what tag do we want to predict?
    # tag_type = 'upos'

    # # 3. make the tag dictionary from the corpus
    # tag_dictionary = corpus.make_tag_dictionary(tag_type=tag_type)
    # print(tag_dictionary.idx2item)

    # # 4. initialize embeddings
    # embedding_types: List[TokenEmbeddings] = [
    #     WordEmbeddings('id-crawl'),
    #     WordEmbeddings('id'),
    #     #WordEmbeddings('glove'),
    #     #BertEmbeddings('bert-base-multilingual-cased')
    # ]

    # embeddings: StackedEmbeddings = StackedEmbeddings(embeddings=embedding_types)

    # # 5. initialize sequence tagger
    # tagger: SequenceTagger = SequenceTagger(hidden_size=256,
    #                                         embeddings=embeddings,
    #                                         tag_dictionary=tag_dictionary,
    #                                         tag_type=tag_type,
    #                                         use_crf=True)

    # # 6. start training
    # trainer: ModelTrainer = ModelTrainer(tagger, corpus)

    # trainer.train('resources/taggers/example-universal-pos',
    #               learning_rate=0.1,
    #               mini_batch_size=32,
    #               max_epochs=10)

    #7. Import News List
    news_list = []
    with open("/mnt/louis/Dataset/news_corpus.txt", "r", encoding='utf-8') as f:
        for line in f:
            news_list.append(sentences_cleaner(line))

    #8. Predict POS Tag for each news
    tag_pos = SequenceTagger.load('resources/taggers/example-universal-pos/best-model.pt')
    for news in news_list:
        sentence = Sentence(news)
        tag_pos.predict(sentence)
        sentence_list = sentence.to_tagged_string().split()

        verb_word_list = []
        for i,token in enumerate(sentence_list):
            if token == '<VERB>':
                verb_word_list.append(sentence_list[i-1])
        
        if verb_word_list:
            verbs = verb_word_list[0]
            verb_word_list.pop(0)
            while True:
                if verb_word_list:
                    verbs += ',' + verb_word_list[0]
                    verb_word_list.pop(0)
                else:
                    break
        else:
            verbs = ''

        with open("/mnt/louis/Dataset/news_corpus_verb.txt","a+") as f_out:
                f_out.write(verbs + '\n')


if __name__ == '__main__':
    main()