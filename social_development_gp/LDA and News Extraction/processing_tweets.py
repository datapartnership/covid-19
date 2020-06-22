"""
This script extracts the date and text of a Tweet.

"""
#Import packages
import pandas as pd
import os
import numpy as np
import glob
import csv
from collections import Counter
import re
from datetime import datetime
from dateutil.parser import parse
import unicodedata
from io import StringIO
#from pandas.io.json import json_normalize
import json
import ast
import re
from ast import literal_eval
from tqdm import tqdm
#import pickle
import random
#import bz2
from random import random as rand
#Set seed
random.seed(2020)

#Get paths
path_to_geo_file = "/mnt/twitter_geolocation_data"
path_to_hashtag_file = "/mnt/twitter_hashtag_data"
path_to_my_folder = "/mnt/alicia"

#Get all the hashtag text file names
hashtag_filenames = glob.glob('/mnt/twitter_hashtag_data/tweets_about_coronavirus_indonesia*.txt')

#Get all the geo text file names
geo_filenames = glob.glob('/mnt/twitter_geolocation_data/indonesia_location_tweets*.txt')


#change the directory to alicia
os.chdir(path_to_my_folder)

#Helper Functions
#Correct Strings
def perfectEval(anonstring):
    try:
        ev = ast.literal_eval(anonstring)
        return ev
    except ValueError:
        corrected = "\'" + anonstring + "\'"
        ev = ast.literal_eval(corrected)
        return ev

#Clean tweets (string representations of dictionaries)
def main():
        #Get Hashtag Files
        dic_hashtag = {'date': [], 'text': []}
        count=0
        for fname in hashtag_filenames:
            with open(fname, 'r') as infile:
                for i, line in tqdm(enumerate(infile)):
                    if rand() >= .80:
                    #Gets 20% random sample
                        try:
                            tweet = perfectEval(line)
                            try:
                                date = tweet["created_at"]
                                text = tweet["text"]
                                dic_hashtag["date"].append(date)
                                dic_hashtag["text"].append(text)
                            except:
                                pass
                        except SyntaxError:
                            count+=1
        df_hashtag = pd.DataFrame.from_dict(dic_hashtag) 
        df_hashtag.to_csv("/mnt/alicia/hashtag_tweets.csv", index=False)
        df_hashtag.columns = ["date", "text"]
        #Get geo file names 
        dic_geo = {'date': [], 'text': []}
        for fname in geo_filenames:
            with open(fname, 'r') as infile:
                 for i, line in tqdm(enumerate(infile)):
                    if rand() >= .80:
                        try:
                            tweet = perfectEval(line)
                            try:
                                date = tweet["created_at"]
                                text = tweet["text"]
                                dic_geo["date"].append(date)
                                dic_geo["text"].append(text)
                            except:
                                pass
                        except SyntaxError:
                            count+=1
        df_geo = pd.DataFrame.from_dict(dic_geo)
        df_geo.columns = ["date", "text"]
        df_geo.to_csv("/mnt/alicia/geo_tweets.csv", index=False)

if __name__ == "__main__":
    main()