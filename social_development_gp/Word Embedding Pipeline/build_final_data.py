"""
Module to build not aggregated final twitter data based on the preprocessed twitter data
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import os
import argparse
import json
import pandas as pd
import re
from tqdm import tqdm

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH  = os.path.join(SCRIPT_PATH, 'Dataset/')

parser = argparse.ArgumentParser()
parser.add_argument('--iter',
	required=True,type=int,
	help="Iteration Number of the CSV Data need to be built")


with open(SCRIPT_PATH+"/Supporting Files/combined_positive_words.txt") as f:
    positive_words_list = f.read().splitlines()

with open(SCRIPT_PATH+"/Supporting Files/combined_negative_words.txt") as f:
    negative_words_list = f.read().splitlines()


def check_hashtags(hashtag,lst):
    if hashtag.lower() in lst:
        return 1
    else:
        return 0

def extract_sentiment(sentence):
	'''
	Function to extract sentiment from sentence based on positive and negative corpus
	'''
	sentiment_series = pd.Series(sentence.split()).apply(lambda x: 1 if x in positive_words_list else -1 if x in negative_words_list else 0)

	return sentiment_series.mean()


if __name__ == "__main__":

	args = parser.parse_args()

	df_list=[]

	hashtags_list = ['#amandirumah','#covid19indonesia','#indonesiamelawancovid19','#bersamalawancorona','#bubarkancegahcorona',
	'#coronaindonesia','#coronajancok','#dansadirumahaja','#diamdirumah','#dikosanaja','#dirumah','#dirumahajacekalcorona',
	'#dirumahajadulu','#dirumahajaya','#dirumahlebihbaik','#dirumahsaja','#distudioaja','#kerjadarirumah','#dpocorona',
	'#fokustanganicovid19','#gerakanphysicaldistancing','#gerakansocialdistancing','#guengantor','#inasoscorona',
	'#indonesia_lockdownplease','#indonesiatanpalockdown','#jagajarak','#jagajarakdulu','#jakartaselatan','#jakarhasimur',
	'#kitadirumahajaya','#lawancorona','#lawancoronabersama','#lawancovid19','#lawanviruspolitikcorona','#lockdownindonesia',
	'#lockdownnasionalserentak','#lockdownataumusnah','#polricegahcorona','#putusrantaicovid19','#rebahanaja','#rebahanlawancorona',
	'#salingjaga','#serudirumah','#stoppolitisasicorona','#terawan','#tergagapcorona','#unbk','#unbk2020','#indonesiatetapbelajar',
	'#waspadacegahcorona','#mudik','#mudik2020','#mudikmembawapetaka','#janganmudik','#janganmudikdulu','#tundamudikcekalcorona',
	'#maskeruntuksemua','#pakaimaskercekalcorona','#pengusahapedulinkri','#westandwithsaiddidu','#luhutpengkhianatri','#luhutpenghianatri',
	'#luhuttherealpresident','#luhutbinsarpandjaitan','#luhutlebihbahayadaricovid19','#lbphancurkanindonesia','#lbptherealvirus',
	'#tolaknapikoruptorbebas','#daruratsipil','#tolakdaruratsipil','#karantinawilayah','#psbb','#psbbjakarta','#aniesbaswedan',
	'#apdforcorona','#daruratapd','#patunganapd','#negaraabaikanrakyat','#prioritaskannyawarakyat','#yasonnalaoly','#dokterperawatminimapd',
	'#apduntukmedis','#perppucorona','#jokowidibawahketiakluhut','#krisismasker','#sembako','#hargasembako','#hargapangan','#listrikgratis',
	'#idiharusjujur','#awasprovokasilockdown','#jakartalockdown','#papualockdown','#tegallockdown','#bandunglockdown','#balilockdown',
	'#resesi','#coronabukaborokrezim','#cekalcoronasaveekonomi','#nomudiksavelives','#hentikankedzalimanrezim','#anarkotunggangicorona',
	'#MendikbudDicariMahasiswa','#NadiemManaMahasiswaMerana.','#BersiapMenujuNewNormal','#NewNormalCegahPHK','#NewNormalPulihkanEkonomi',
	'#DisiplinKunciNewNormal','#IndonesiaAbnormal','#Tatakehidupanbaru','#Disiplinpolahidupbaru','#kartuprakerja','#kawalkartuprakerja',
	'#prakerja','#JakartaTanggapCorona','#SemangatMelawanCovid19','#DataterbaruCorona','#LockdownIndonesia','#JKTlemotanganicorona',
	'#Karantinawilayah','#PSBL','#PSBB','#SuratIzinKeluarMasuk','#SIKM','#Weallstandwithsaiddidu','#INASOSCorona','#lawancovid19',
	'#ridwankamil','#jabarjuara','#adaptasinewnormal','#PCRtest','#rapidtest','#WaspadaLaskarPengacauNegara','#OperasiKetupat2020',
	'#KebhinekaanIndonesia','#rezimlaknat','#jokowidekatdihati','#kegagalanamiesitunyata','#JKWTumbangRakyatSenang','#Produktiferanewnormal',
	'#Balikindanahaji','#Dipecatkokdibela','#Rakyatdukungnewpresident','#IndonesiaTerserah','#IndonesiaTerserahPakDe','#kebohonganbaru']
	
	with open(DATA_PATH+'Cleaned/'+"cleaned_tweets_{}.txt".format(args.iter),'r') as f:
		for line in tqdm(f):
			tweet = json.loads(line)

			if tweet['text']!='':

				tweet_hashtags_lst = ['#'+tweet['hashtags'][idx]['text'].lower() for idx in range(len(tweet['hashtags']))]

				try:
					location = tweet['location']['full_name'].split(',')[0]
				except:
					location = tweet['location']

				tweet_dict = {
				'tweet_id': tweet['tweet_id'],
				'user_id': tweet['user_id'],
				'created_at': tweet['created_at'],
				'location': tweet['location'],
				'text': re.sub(r"kunci turun","lockdown",tweet['text']),
				'sentiment_score': extract_sentiment(tweet['text']),
				'verified': tweet['verified'],
				'reply_count': tweet['reply_count'],
				'retweet_count': tweet['retweet_count'],
				'favorite_count': tweet['favorite_count']}

				for hashtag in hashtags_list:
					tweet_dict[hashtag] = check_hashtags(hashtag,tweet_hashtags_lst)

				df_list.append(tweet_dict)

	column_name = ['tweet_id','user_id','created_at','location','text','sentiment_score','verified','reply_count','retweet_count','favorite_count']
	for hashtag in hashtags_list:
		column_name.append(hashtag)

	df = pd.DataFrame(df_list,columns=column_name)
	
	df.to_csv(DATA_PATH+'Final/Not_Aggregated/'+"final_tweets_{}.csv".format(args.iter),index=False)