"""
Module to extract the Twitter users demographic data accross region
based on the inference results from Kiran 
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import pandas as pd
import re


def extract_location(_dict,username):
	try:
		return _dict[username]
	except:
		return ''


if __name__ == "__main__":

	#Import Twitter Demographic Data
	twitter_username_list = []
	twitter_gender_class_list = []
	twitter_age_class_list = []
	with open('/mnt/kiran/twitter_age_gender.txt','r') as f:
		for line in f:
			twitter_username_list.append(line.split('\t')[0])
			twitter_gender_class_list.append(line.split('\t')[1])
			twitter_age_class_list.append(line.split('\t')[2])

	df = pd.DataFrame([twitter_username_list,twitter_gender_class_list,twitter_age_class_list]).T
	df.columns = ['username','gender_class','age_class']

	user_location_dict = {}
	#Import User Location
	with open('/mnt/kiran/user_profile_locations.txt','r') as f:
		for line in f:
			lst = re.sub('\n','',line).split('\t')
			try:
				user_location_dict[lst[0]] = lst[1]
			except Exception as e:
				print(e)

	df['location'] = df['username'].apply(lambda x: extract_location(user_location_dict,re.sub(r'.jpeg$','',x)))

	demographic_region_df = df.groupby(['location','gender_class','age_class']).count().reset_index()

	demographic_region_df.to_csv('/mnt/louis/twitter_demographic_100_region.csv',index=False)
