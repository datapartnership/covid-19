"""
Module to summarize the result from age_gender_infer_100.py --data instagram
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import pandas as pd

df_insta_demographic = pd.read_csv('/mnt/louis/instagram_demographic_100.csv')

df_insta_demographic['age_class'] = df_insta_demographic['age_class'].apply(lambda x: "<=18" if x<=18 else "19-29" if x<=29 else "30-39" if x<=39 else ">=40")
df_insta_demographic['gender_class'] = df_insta_demographic['gender_class'].apply(lambda x: "male" if x==1 else "female")

df = pd.read_csv('/mnt/louis/Dataset/Instagram/Final/agg_final_data_insta.csv',usecols=['user_id'])

print('Unique Users: {}'.format(len(df['user_id'].unique())))

print(df_insta_demographic['age_class'].value_counts())

print(df_insta_demographic['gender_class'].value_counts())