"""
Module to expand the manually extracted keywords from misinformation news corpus
by finding similar keyword of the verbs on each misinformation news extracted before
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import gensim
import re


forbidden_keywords_list = []
with open('/mnt/louis/Issue Monitoring/forbidden_keywords.txt','r') as f:
	for line in f:
		forbidden_keywords_list.append(re.sub('\n','',line).lower())


def main():
	#Load Model
	model = gensim.models.Word2Vec.load('/mnt/louis/Issue Monitoring/model/w2v_all_300.model')

	#Import Verbs List
	verbs_lists = []
	with open("/mnt/louis/Dataset/news_corpus_verb.txt","r") as f:
		for line in f:
			if line!='\n':
				verbs_lists.append(re.sub('\n','',line).split(','))
			else:
				verbs_lists.append([])

	#Import Manually Curated Keyword List
	keyword_lists = []
	with open("/mnt/louis/Dataset/news_corpus_keyword.txt","r") as f:
		for line in f:
			line = line.lower()
			line = re.sub('\n','',line)
			keyword_lists.append(line.replace(' ',',').split(','))

	with open("/mnt/louis/Dataset/news_corpus_keyword_expanded.txt","a+") as f_out:
		for i,verbs_list in enumerate(verbs_lists):
			keyword_list = keyword_lists[i]
			keyword_list = [word for word in keyword_list if word not in verbs_list]
			if keyword_list:
				expanded_keywords = keyword_list[0]
				keyword_list.pop(0)
				while True:
					if keyword_list:
						expanded_keywords += ' ' + keyword_list[0]
						keyword_list.pop(0)
					else:
						break
			else:
				expanded_keywords = ''


			if verbs_list:
				expanded_keywords += ';'
				for j,verb in enumerate(verbs_list):
					if j == 0:
						expanded_keywords += verb
					else:
						expanded_keywords += ';' + verb

					try:
						similar_word_list = model.most_similar(verb, topn = 5)
						expanded_keywords += ' ' + similar_word_list[0][0]#Top similar word with the verb
						similar_word_list.pop(0)
						for similar_word in similar_word_list:
							if (similar_word[0] not in forbidden_keywords_list) and (not similar_word[0].isdigit()) and (similar_word[1]>0.6) and (similar_word[0] not in ['corona','covid','korona','covid19','covid-19']):
								expanded_keywords += ' ' + similar_word[0]

					except Exception as e:
						print(e)

			f_out.write(expanded_keywords+'\n')


if __name__=='__main__':
	main()