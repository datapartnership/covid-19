import os
import random
import json
import sys
from time import sleep
from datetime import datetime

hashtag = sys.argv[1]#likesforlikes
now = datetime.now()
now = int(datetime.timestamp(now))
print(hashtag)
f = open(hashtag + "/file.info")
f_name = f.read().split("\n")[0]
f.close()
if f_name != "":
	f = open(hashtag + "/" + f_name)
	line = f.readlines()
	if line != "":
		json_line = json.loads(line[-1])
		prev_count = json_line["data"]["hashtag"]["edge_hashtag_to_media"]["count"]
		json_line = json.loads(line[0])
		data = json_line["data"]["hashtag"]["edge_hashtag_to_media"]["edges"]
		post = data[0]
		basestamp = post["node"]["taken_at_timestamp"]
		print(basestamp)
	else:
		prev_count = 1
		basestamp = 0
else:
	prev_count = 1
	basestamp = 0
out = open(hashtag + "/" + str(now) + "_data.json","a")
present_count = prev_count + 2
count = 1
k = open(hashtag + "/continue.info")
end_hash = k.read().strip()
k.close()
is_true = True

while present_count > prev_count:
	try:
		if end_hash == "None":
			break
		com = 'wget -qO ' + hashtag + '/1.json \'https://www.instagram.com/graphql/query/?query_hash=ded47faa9a1aaded10161a2ff32abb6b&variables={"after":"' + str(end_hash) + '","tag_name":"' + str(hashtag).lower() + '","first":50}\''
		os.system(com)
		f = open(hashtag + "/1.json")
		lines = f.read()
		json_lines = json.loads(lines)
		if str(json_lines["data"]["hashtag"]) == "None":
			print(hashtag,"No Data",com)
			break
		data = json_lines["data"]["hashtag"]["edge_hashtag_to_media"]["edges"]
		if len(data) != 0:
			post = data[0]
			timestamp = post["node"]["taken_at_timestamp"]
		else:
			print("error",com)
			break
		if timestamp < basestamp:
			break
		end_hash = str(json_lines["data"]["hashtag"]["edge_hashtag_to_media"]["page_info"]["end_cursor"])
		is_true = bool(json_lines["data"]["hashtag"]["edge_hashtag_to_media"]["page_info"]["has_next_page"])
		nodes = len(json_lines["data"]["hashtag"]["edge_hashtag_to_media"]["edges"])
		present_count = present_count - nodes
		print(timestamp,basestamp,present_count)
		print(end_hash,is_true)
		if count == 1:
			present_count = int(json_lines["data"]["hashtag"]["edge_hashtag_to_media"]["count"])
		out.write(lines + "\n")
		k = open(hashtag + "/continue.info","w")
		k.write(end_hash)
		k.close()
		count = count + 1
	except:
		print(lines)
		sleep(5)
		print("error",com)
		continue
print(count,"iterations")
out.close()
k = open(hashtag + "/continue.info","w")
k.write("")
k.close()
k = open(hashtag + "/file.info","w")
k.write(str(now) + "_data.json")
k.close()
