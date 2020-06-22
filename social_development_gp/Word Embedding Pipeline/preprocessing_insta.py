"""
Module to do preprocessing on instagram data
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import argparse
from tqdm import tqdm
import json
import string
import ast
import re
import timestamp
import datetime
from preprocessing_text import sentences_cleaner


def get_args():
    parser = argparse.ArgumentParser(description='Data Preprocessing')
    parser.add_argument('--start_date', type=int, required=True, help='Starting Date')
    parser.add_argument('--start_month', type=int, required=True, help='Starting Month')
    parser.add_argument('--file_name', type=str, required=True, help='input file name')
    return parser.parse_args()


def main():
	args = get_args()

	with open('/mnt/instagram/'+args.file_name+'.json','r') as f:
		for line in tqdm(f):
			try: #in case there are data which not well-formatted
				try:
					data = json.loads(line)
				except:
					data = ast.literal_eval(line)

				caption_list = data['data']['hashtag']['edge_hashtag_to_media']['edges']

				dict_output = {}

				for i in range(len(caption_list)):
					date = datetime.datetime.fromtimestamp(caption_list[i]['node']['taken_at_timestamp']).date()
					if datetime.datetime(date.year,date.month,date.day) >= datetime.datetime(2020,args.start_month,args.start_date): #Get new data only
						dict_output['created_at'] = str(date.month)+'/'+str(date.day)+'/'+str(date.year)
						dict_output['user_id'] = caption_list[i]['node']['owner']['id']
						text = caption_list[i]['node']['edge_media_to_caption']['edges'][0]['node']['text']
						dict_output['text'] = sentences_cleaner(text)
						dict_output['hashtags'] = re.findall(r'#[A-Za-z0-9_]+',text)
						dict_output['comments_count'] = caption_list[i]['node']['edge_media_to_comment']['count']
						dict_output['likes_count'] = caption_list[i]['node']['edge_media_preview_like']['count'] #count of likes including organic likes & sponsored likes
					
						with open(DATA_PATH+"Cleaned/"+"cleaned_insta_1.txt",'a+') as f_out:
							json.dump(dict_output,f_out)
							f_out.write('\n')
			
			except Exception as e:
				print(e)
	
	
if __name__ == '__main__':

	main()

	


