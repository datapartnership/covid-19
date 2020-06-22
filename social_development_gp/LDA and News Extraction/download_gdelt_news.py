"""
This script pulls daily multilingual files from the GDELT Coronavirus Narrative Database.
Schedule a cron job to run this on a schedule.

"""
#Import packages
import wget
import requests
from datetime import datetime
from datetime import timedelta
import os
import csv
import gzip
import pandas as pd

#Change to appropriate directory
os.chdir('/mnt/alicia/indonesian_news')
#Pull all the multilingual files
url = "http://data.gdeltproject.org/blog/2020-coronavirus-narrative/live_onlinenews/MASTERFILELIST.TXT"
#Grab the links
page = requests.get(url)    
data = page.text
#Make a list of the links
links = data.splitlines()
#Get yesterday's date
yesterday = datetime.today() - timedelta(days = 1)
yesterday = yesterday.strftime('%Y%m%d')
#Evaluate yesterday's files
yesterday_files = [x for x in links if yesterday in x]
multilingual_yesterday_files = [x for x in yesterday_files if "multilingualurls" in x]
multilingual_files = [x for x in links if "multilingualurls" in x]
#Only pull yesterday's files
multilingual_files = list(set(multilingual_yesterday_files))

#def delete_old_files(del_dir):
    # loop through all files in directory and delete them
#    for each_file in os.listdir(del_dir):
#        target_file = '{}\{}'.format(del_dir, each_file)
#        os.remove(target_file)
#        print('deleting {}'.format(target_file))
#    pass
#missing_files = ["http://data.gdeltproject.org/blog/2020-coronavirus-narrative/live_onlinenews/20200531-multilingualurls.csv.gz",
#"http://data.gdeltproject.org/blog/2020-coronavirus-narrative/live_onlinenews/20200601-multilingualurls.csv.gz", 
#]

#Wget. download them into the directory
for f in multilingual_files:
    wget.download(f, '/mnt/alicia/indonesian_news')

#Grab the filenames
file_names = [x[77:]for x in multilingual_files]
#Depending on how far back you want to go, you can can get files from 2015
#file_names.remove('20151130-20200329-multilingualurls.csv.gz')

#Filter out any non-Indonesian files, append onto the old files
for fname in file_names:
    with gzip.open(fname, mode= 'rt') as infile:
        reader = csv.reader(infile)
        #Grab the appropriate rows, in this case, Indonesian news
        filtered = filter(lambda row: 'ind' == row[3], reader)
        csv.writer(open(r"indonesia_news_filtered.csv", 'a+'), delimiter=',').writerows(filtered)

#Filter and clean dates and text
df = pd.read_csv("indonesia_news_filtered.csv", sep=',', names = ["date", "text", "Image", "Language", "URL"])
#Drop duplicates if any exist
df = df.drop_duplicates()
#Clean the dates
df["date"]= pd.to_datetime(df["date"], format='%Y%m%d%H%M%S', errors = 'coerce').dt.date
df["text"] = [str(x) for x in df["text"]]
#Constrain the date range
startdate = pd.to_datetime("2020-03-24").date()
df = df[df["date"] > startdate]
#Output to csv
df.to_csv("clean_indonesia_news.csv", index=False)