"""
Module to aggregate all not aggregated final instagram data
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import os
import pandas as pd

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH  = os.path.join(SCRIPT_PATH, 'Dataset/Instagram/Final/')

if __name__=='__main__':

	SOURCE = DATA_PATH+'Not_Aggregated/'
	 
	_,_,filenames = next(os.walk(SOURCE))

	print(filenames[0])
	df = pd.read_csv(SOURCE+filenames[0],error_bad_lines=False) 
	df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
	df = df.dropna(subset=['created_at'])
	df = df[~pd.isnull(df.text)]
	df = df.sort_values(by='created_at').reset_index(drop=True)
	filenames.pop(0)

	for filename in filenames:
		print(filename)
		df_temp = pd.read_csv(SOURCE+filename,error_bad_lines=False)
		df_temp['created_at'] = pd.to_datetime(df_temp['created_at'], errors='coerce')
		df_temp = df_temp.dropna(subset=['created_at'])
		df_temp = df_temp[~pd.isnull(df_temp.text)]
		df_temp = df_temp.sort_values(by='created_at').reset_index(drop=True)
		df = df.append(df_temp, ignore_index = True)
		df[[col for col in df.columns if col not in ['user_id','created_at','text','sentiment_score','comments_count','likes_count']]] = df[[col for col in df.columns if col not in ['user_id','created_at','text','sentiment_score','comments_count','likes_count']]].fillna(value=0)

	df = df.sort_values(by='created_at')
	df['year'] = df['created_at'].apply(lambda x: x.year)
	df = df[df.year>=2020]
	df = df[[x for x in df.columns if x !='year']]
	
	df.to_csv(DATA_PATH+'agg_final_data_insta.csv',index=False) 