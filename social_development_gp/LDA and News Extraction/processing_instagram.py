"""
This script takes the date and text of an Instagram caption.

"""

#Import packages
import pandas as pd
import os
import numpy as np
import glob
import csv
from collections import Counter
import re
import datetime as dt
from dateutil.parser import parse
import datetime
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
path_to_insta_file = "/mnt/instagram"
path_to_my_folder = "/mnt/alicia"

#change the directory to folder
os.chdir(path_to_my_folder)

#Get the instagram file names
insta_filenames = ['/mnt/instagram/all_posts_23_April_2020.json', '/mnt/instagram/all_posts_13_May_2020.json',
'/mnt/instagram/all_posts_after_2020-05-10.json']
#Helper Functions
def int_or_else(value, else_value=None):
    """
    Given a value, returns the value as an int if possible. 
    If not, returns else_value which defaults to None.
    """
    try:
        return int(value)
    except Exception:
        return else_value

#Correct Strings
def perfectEval(anonstring):
    try:
        ev = ast.literal_eval(anonstring)
        return ev
    except ValueError:
        corrected = "\'" + anonstring + "\'"
        ev = ast.literal_eval(corrected)
        return ev
#Pull a random sample of Instagram Files
def main():
        #Get Insta Files
        count=0
        dic_insta = {'date':[], 'text':[]}
        for fname in insta_filenames:
            with open(fname, 'r') as infile:
                for i, line in tqdm(enumerate(infile)):
                    if rand() >= .90:
                    #Gets 10% random sample
                        try:
                            try:
                                insta = json.loads(line)
                            except:
                                #In case there is malformed lines
                                insta = ast.literal_eval(line)

                            captions = insta['data']['hashtag']['edge_hashtag_to_media']['edges']
                        
                            for i in range(len(captions)):
                                #Grab the caption from the insta post
                                date = datetime.datetime.fromtimestamp(captions[i]['node']['taken_at_timestamp']).date()
                                if datetime.datetime(date.year,date.month,date.day) >= datetime.datetime(2020, 3, 25):
                                    #Takes all posts after 3/25/2020
                                    date = date
                                    #str(date.month) + str(date.day) + str(date.year)
                                    text = captions[i]['node']['edge_media_to_caption']['edges'][0]['node']['text']
                                    dic_insta["date"].append(date)
                                    dic_insta["text"].append(text)
                        except Exception as e:
                            count+=1
                            #print(e)
        dic_insta = pd.DataFrame.from_dict(dic_insta) 
        #dic_insta["date"] = dic_insta["date"].apply(lambda x: dt.datetime.fromtimestamp(int(x)).strftime('%Y-%m-%d %H:%M:%S'))
        #dic_insta = dic_insta[(dic_insta['date'] > '2020-24-03')]
        dic_insta.columns = ["date", "text"] 
        dic_insta.to_csv("/mnt/alicia/instagram_data.csv", index = False)


if __name__ == "__main__":
    main()