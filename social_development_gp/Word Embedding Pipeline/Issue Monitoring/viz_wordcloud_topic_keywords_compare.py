"""
Module to generate english translated word cloud visualization 
for confidence in government topic, comparing between 
twitter, instagram, and gdelt news
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

from wordcloud import WordCloud, ImageColorGenerator
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
import urllib.request
import argparse

def get_args():
    parser = argparse.ArgumentParser(description='Data Preprocessing')
    parser.add_argument('--data', required=True, choices=['twitter','insta','gdelt'],help='Data Source')
    return parser.parse_args()


def Google_Translate_API(word):
    '''
    API to Google Translate
    '''
    url = 'https://translate.google.com/m?sl=%s&tl=%s&ie=UTF-8&prev=_m&q=%s' % ('id', 'en',word.replace(" ","+")) 
    agent = {'User-Agent':'Mozilla/5.0'}
    request = urllib.request.Request(url, headers=agent)
    page = urllib.request.urlopen(request).read().decode('utf-8')
    result = page.split('class="t0">')[1].split('<')[0]
    return result


def my_tf_color_func(dictionary,similar_keyword_list):
	def my_tf_color_func_inner(word, font_size, position, orientation, random_state=None, **kwargs):
		if word in similar_keyword_list:
			return "hsl(0, 0%%, %d%%)" % (dictionary[word]) #GREY
		else:
			return "hsl(360, 50%%, 50%%)" % (dictionary[word])	#RED
	return my_tf_color_func_inner


if __name__ == '__main__':
    args = get_args()

    char_mask = np.load("F:/WB/Dataset/corona_image.npy")
    image_colors = ImageColorGenerator(char_mask)

    translate_dict={'bantuan':'aid',
    'apd':'ppe',
    'garda':'guard',
    'psbb':'lssr',
    'drpd':'instead of',
    'jgn':'do not',
    'garda terdepan':'front guard',
    'hasile':'result',
    'kasi':'give',
    'kasih' : 'give',
    'gausah':'no need',
    'liwat':'through',
    'santuy':'relax',
    'kenacorona':'infectedbycorona',
    'videowarga':'citizensvideo',
    'dunia covid':'covid world',
    'warga menolak':'citizens refused',
    'jenazah covid':'covid corpse',
    'jenazah covid19':'covid19 corpse',
    'jenazah corona':'corona corpse',
    'mudik':'mudik',
    'dilarang mudik':'prohibited to mudik',
    'kampung lindungi':'protect the village',
    '19 ditolak':'19 rejected',
    'jenazah dalam':'corpse inside',
    'nolak jenazah':'refuse corpse',
    'didoakan musuh':'prayed by the enemies',
    'ditolak gede':'big refusal',
    'ditolak tpu':'refuse tpu',
    'dki bertambah':'dki increases',
    'jawa menghadang':'jawa blocks',
    'depok kota':'depok city',
    'rs rujukan':'referral hospital',
    'rs darurat':'emergency hospital',
    'nakes':'healthworkers',
    'atlet kemayoran':'kemayoran athletes',
    "wisma atlet":"athelete's homestead",
    'pelindung apd':'ppe protector',
    'atlet rs':'athlete hospital',
    'masker n95':'n95 mask',
    'bedah n95':'n95 surgery',
    'n95 petugas':'n95 officer',
    'kartu pra kerja':'pre work card',
    'kartu prakerja':'prework card',
    '19 achmad':'19 achmad',
    '2 meter':'2 meters',
    '2m':'2m',
    '4m':'4m',
    '25m':'25m',
    '05m':'05m',
    '1 meter':'1 meter',
    '2mfacility':'2mfacilities',
    '80rbkain':'80 thousands fabric',
    'rumah keperluan':'home needs',
    'rumah urgent': 'house urgent',
    'keluar dalem':'inside out',
    'physical distancing':'physical distancing',
    'blt' : 'cash transfer',
    'phk': 'work termination',
    'sdm' : 'human resources'}

    topic = 'confidence in government'

    print('Generating Confidence in Government Word Cloud for Data: {}'.format(args.data))
    
    dict_temp = {}
    similar_keyword_list = []
    
    if args.data=='twitter':
        name = ''
    else:
        name = args.data + '_'

    df = pd.read_csv('F:/WB/Issue Monitoring/data/{}TOP_10_Similar_Issue_Keyword.csv'.format(name))
    df_temp = df[df.topic==topic].reset_index(drop=True)

    for i in range(len(df_temp)):
        keyword = re.sub(r'[^a-zA-Z-0-9]','',df_temp.loc[i,'keyword'])

        if (not keyword.isdigit()) and (keyword not in dict_temp):
            try:
                keyword = translate_dict[re.sub(r'[^a-zA-Z-0-9]','',keyword).lower()]
            except:
                try:
                   keyword = re.sub(r'[^a-zA-Z-0-9]','',Google_Translate_API(re.sub(r'[^a-zA-Z-0-9]','',keyword)))
                except:
                    pass
         
            dict_temp[keyword] = df_temp.loc[i,'keyword_count']


        similar_keyword = re.sub(r'[^a-zA-Z-0-9]','',df_temp.loc[i,'similar_keyword'])
        if ((topic=='food access') and (similar_keyword in ['apd','tim'])) or ((topic=='health care') and (similar_keyword in ['dokter'])):
            continue

        if (not similar_keyword.isdigit()):
            try:
                similar_keyword = translate_dict[re.sub(r'[^a-zA-Z-0-9]','',similar_keyword).lower()]
            except:
                try:
                   similar_keyword = re.sub(r'[^a-zA-Z-0-9]','',Google_Translate_API(re.sub(r'[^a-zA-Z-0-9]','',similar_keyword)))
                except Exception as e:
                    print(e)
         
            dict_temp[similar_keyword] = df_temp.loc[i,'similar_keyword_count']
            similar_keyword_list.append(similar_keyword)

    del dict_temp['covid19']

    wc = WordCloud(collocations=False,background_color="black", max_words=300, width=400, height=400, random_state=1,color_func = my_tf_color_func(dict_temp,similar_keyword_list)).generate_from_frequencies(dict_temp)
    plt.figure(figsize=(15,10),facecolor='black')
    # plt.imshow(np.array(wc.recolor(color_func=image_colors)))
    plt.imshow(np.array(wc))
    plt.title('Word Cloud for Topic: {}'.format(topic),color='grey',fontsize=25)
    plt.axis('off')
    plt.savefig('F:/WB/Issue Monitoring/wordcloud_output/{}english_wordcloud_{}.png'.format(name,topic),edgecolor="none",facecolor='black', transparent=True)