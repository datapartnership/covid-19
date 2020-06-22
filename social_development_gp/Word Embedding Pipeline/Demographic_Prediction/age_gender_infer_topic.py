"""
Module to extract the Twitter users demographic data accross policy issue topic
based on the inference results from Kiran 
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import pandas as pd
import argparse
import re


def get_args():
    parser = argparse.ArgumentParser(description='Data Preprocessing')
    parser.add_argument('--data', choices=['twitter','instagram'], required=True, help='Data Source')
    return parser.parse_args()


def extract_age(age_dict,user_id):
	try:
		return age_dict[user_id]
	except:
		return -1


def extract_gender(gender_dict,user_id):
	try:
		return gender_dict[user_id]
	except:
		return -1


def main():
	args = get_args()

	if args.data=='twitter':
		#Import data
		df = pd.read_csv('/mnt/louis/Issue Monitoring/TOP_10_Evolution_Weekly_Issue_Keyword_user_level.csv',usecols=['user_id','confidence in government','food access','health care','job loss','mask for all','social distancing','stigma','travel restrictions'])

		#Import Twitter user_id mapping
		twitter_user_id_mapping_dict={}
		with open("/mnt/kiran/all_users_profiles_twitter.txt","r") as f:
			for line in f:
				if (line.split('\t')[0]).isdigit():
					twitter_user_id_mapping_dict[line.split('\t')[1]] = re.sub('\n','',line.split('\t')[0]) 

		#Import Twitter Demographic Data
		age_class_dict = {}
		gender_class_dict = {}
		with open('/mnt/kiran/twitter_age_gender.txt','r') as f:
			for line in f:
				if line.split('\t')[0] in twitter_user_id_mapping_dict:
					user_id = twitter_user_id_mapping_dict[line.split('\t')[0]]
					age_class_dict[user_id] = line.split('\t')[2]
					gender_class_dict[user_id] = line.split('\t')[1]


	df['age_class'] = df['user_id'].apply(lambda x: extract_age(age_class_dict,str(x)))
	df['gender_class'] = df['user_id'].apply(lambda x: extract_gender(gender_class_dict,str(x)))

	df_age_gender_topic = pd.DataFrame(columns=['topic','<=18','19-29','30-39','>=40','male','female','age_nan','gender_nan'])

	for topic in ['confidence in government','food access','health care','job loss','mask for all','social distancing','stigma','travel restrictions']:
		age_class_count = df[df[topic]==1]['age_class'].value_counts()
		gender_class_count = df[df[topic]==1]['gender_class'].value_counts()

		age_gender_topic_dict = {'topic':topic,'age_nan':age_class_count[-1],'gender_nan':gender_class_count[-1],'male':gender_class_count['male'],'female':gender_class_count['female']}
		for age_class in ['<=18','19-29','30-39','>=40']:
			age_gender_topic_dict[age_class] = age_class_count[age_class]

		df_age_gender_topic = df_age_gender_topic.append(age_gender_topic_dict,ignore_index=True)

	df_age_gender_topic.to_csv('/mnt/louis/{}_demographic_topic.csv'.format(args.data),index=False)

if __name__=='__main__':
	main()