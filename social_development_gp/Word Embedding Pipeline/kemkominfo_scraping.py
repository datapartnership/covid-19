"""
Module to scrape misinformation news from KEMKOMINFO official website
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import requests
from bs4 import BeautifulSoup
import re

if __name__=='__main__':
	i = 1
	cnt = 0

	with open("F:/WB/Dataset/KEMKOMINFO_corpus.txt","r") as f:
		old_news_list = f.readlines()

	old_news_list = [re.sub("\n","",x) for x in old_news_list]

	while True:
		URL = 'https://www.kominfo.go.id/search?search=corona&page='+str(i)
		page = requests.get(URL)

		i+=1

		soup = BeautifulSoup(page.content, 'html.parser')

		if soup.find(class_='alert'):
			break

		results = soup.find(class_='col-md-9')

		title_elems = results.find_all('a', class_='title')

		for title_elem in title_elems:
			if ("HOAKS" in title_elem.text) or ("DISINFORMASI" in title_elem.text):
				cnt+=1
				print("Scraped News: {}\r".format(cnt),end="")
				news = title_elem.text.split(']')[1].strip()
				if news in old_news_list:
					break
				with open("F:/WB/Dataset/KEMKOMINFO_corpus.txt","a+") as f_out:
					f_out.write(news+'\n')
		else:
			continue # only executed if the inner loop did NOT break
		break # only executed if the inner loop DID break

		
		


	

