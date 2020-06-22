"""
Module to do preprocessing on the given sentence
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import random
import re
import pandas as pd
import numpy as np
import json
import string
from tqdm import tqdm

#Resources are available at https://github.com/louisowen6/NLP_bahasa_resources
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

    return re.sub(' +',' ',stripped).strip()