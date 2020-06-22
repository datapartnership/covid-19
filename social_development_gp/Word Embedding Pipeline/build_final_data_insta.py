"""
Module to build not aggregated final instagram data based on the preprocessed instagram data
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import os
import argparse
import json
import pandas as pd
import re
from tqdm import tqdm
import datetime

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH  = os.path.join(SCRIPT_PATH, 'Dataset/Instagram/')

parser = argparse.ArgumentParser()
parser.add_argument('--start_date', type=int, required=True, help='Starting Date')
parser.add_argument('--start_month', type=int, required=True, help='Starting Month')
parser.add_argument('--start_iter', type=int, required=True, help='Starting Iter')


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


def main():

	args = parser.parse_args()

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
	

	split = args.start_iter - 1
	thres = -1
	while True:
		i = 0
		df_list=[]
		stopped=False
		with open(DATA_PATH+'Cleaned/'+"cleaned_insta_1.txt",'r') as f:
			for line in tqdm(f):
				if i > thres:
					data = json.loads(line)

					if (data['text']!='') and (datetime.datetime(int(data['created_at'].split('/')[2]),int(data['created_at'].split('/')[0]),int(data['created_at'].split('/')[1])) >= datetime.datetime(2020,args.start_month,args.start_date)):

						data_hashtags_lst = ['#'+data['hashtags'][idx].lower() for idx in range(len(data['hashtags']))]

						data_dict = {
						'user_id': data['user_id'],
						'created_at': data['created_at'],
						'text': re.sub(r"kunci turun","lockdown",data['text']),
						'sentiment_score': extract_sentiment(data['text']),
						'comments_count': data['comments_count'],
						'likes_count': data['likes_count']
						}

						for hashtag in hashtags_list:
							data_dict[hashtag] = check_hashtags(hashtag,data_hashtags_lst)

						df_list.append(data_dict)

				i+=1

				if (i % 1000000 == 0) and (i > thres) and (len(df_list)>0):
					split += 1
					thres = i
					stopped = True
					break

		column_name = ['user_id','created_at','text','sentiment_score','comments_count','likes_count']
		for hashtag in hashtags_list:
			column_name.append(hashtag)

		df = pd.DataFrame(df_list,columns=column_name)
		
		df.to_csv(DATA_PATH+'Final/Not_Aggregated/'+"final_insta_1_{}.csv".format(split),index=False)

		#Free Up Memory
		del df
		del df_list

		if not stopped:
			break

if __name__ == "__main__":
	main()