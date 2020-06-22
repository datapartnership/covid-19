import sys,time,os,glob;
from pytrends.request import TrendReq
import pytrends
from datetime import date

folder_name = sys.argv[1]; # one of covid_updates, job_loss, food_insecurity, travel_restriction, lssr or govt_programs;

dict_keywords = {"covid_updates":["gejala virus corona", "cara pencegahan corona virus", "jumlah korban virus corona di indonesia hari ini", "apa itu social distancing"], 
        "job_loss":["PHK", "PHK Corona", "pengangguran", "bantuan untuk pengangguran", "kartu prakerja", "cara daftar kartu prakerja", "lowongan pekerjaan"], 
        "food_insecurity":["harga beras mahal", "harga pangan mahal", "stok makanan menipis", "panic buying", "panic buying corona", "sembako", "sembako gratis", "beli sembako murah"], 
        "travel_restriction":["mudik", "airport dibuka corona", "alternatif mudik", "larangan mudik", "pelabuhan dibuka"], 
        "lssr":["apa itu PSBB", "peraturan PSBB", "daerah berlakukan PSBB", "LSSR sampai kapan", "perusahaan mana yang boleh buka saat PSBB", "apakah PSBB efektif", "relaksasi PSBB", "perbedaan PSBB dan lock down"], 
        "govt_programs":["program keluarga harapan", "BPNT Sembako", "keringaan biaya BPJS TK", "keringaan biaya BPJS KES", "KUR", "Bantuan Daerah", "metode testing corona virus", "PCR test", "test cepat", "restrukturisasi kredit", "keringanan biaya listrik corona", "keringanan pajak untuk UMKM", "keringanan pajak individu"]};

f = open("google_trends_keywords.txt")
#f = open("/tmp/1");
lines = f.readlines();

dict_keywords = {"covid_updates":lines[0].strip().split(","),
        "job_loss":lines[1].strip().split(","),
        "food_insecurity":lines[2].strip().split(","),
        "travel_restriction":lines[3].strip().split(","),
        "lssr":lines[4].strip().split(","),
        "govt_programs":lines[5].strip().split(",")};

pytrend = TrendReq();#geo="ID",timeframe="2020-03-24 2020-05-20");
#kw_list = ["corona virus"];
command0 = "rm tmp/" + folder_name + "/*";
os.system(command0);

today = date.today()

# dd/mm/YY
date_today = today.strftime("%Y-%m-%d")

for word in dict_keywords[folder_name]:
    print("starting",word);
    kw_list = [word.lower().strip()];
    pytrend.build_payload(kw_list=kw_list,geo="ID",timeframe="2020-01-01 " + date_today)
    interest_over_time_df = pytrend.interest_over_time()
    interest_over_time_df.to_csv("tmp/" + folder_name + "/" + kw_list[0].replace(" ","_") + ".csv")

    related_queries_dict = pytrend.related_queries() 
#    print(related_queries_dict)
    try:
        related_queries = list(related_queries_dict[kw_list[0]]["top"]["query"])
    except:
        print("FUC",kw_list);
        continue;

    count = 0;
    for query in related_queries[:10]:
        query = query.lower().strip();
        print(query,count);
        count += 1;
        kw_list = [query];
        try:
            pytrend.build_payload(kw_list=kw_list,geo="ID",timeframe="2020-01-01 " + date_today)
        except:
            print("ERROR",kw_list,file=sys.stderr)
            continue;
        interest_over_time_df = pytrend.interest_over_time()
        if(interest_over_time_df.shape[0]==0):
            print("ERROR2",kw_list,file=sys.stderr)
            continue;
        interest_over_time_df.to_csv("tmp/" + folder_name + "/" + kw_list[0].replace(" ","_") + ".csv")
        time.sleep(10); 

for infile in glob.glob("tmp/" + folder_name + "/*"):
    f = open(infile);
    lines = f.readlines();

    flag = 0;
    if(len(lines)==1):
        flag = 1;

    f.close();
    if(flag==1):
        print("removing", infile, file=sys.stderr);
        os.system("rm " + infile);

command = "paste -d',' tmp/" + folder_name + "/*.csv | cut -f1,2,5,8,11,14,17,20,23,26,29,32,35,38,41,44,47,50,53,56,59,62,65,68,71,74,77,80,83,86,89,92,95,98,101 -d',' > google_trends_data_" + folder_name + ".csv"
os.system(command);

command1 = "cat google_trends_data_" + folder_name + ".csv | sed -e's/,/\t/g' | sed -e's/-//g' > /var/www/html/data_" + folder_name + ".tsv"
os.system(command1);
#interest_by_region_df = pytrend.interest_by_region()
#print(interest_by_region_df.head())

#trending_searches_df = pytrend.trending_searches()
#print(trending_searches_df.head())


#pytrends.get_historical_interest(kw_list, year_start=2020, month_start=2, day_start=1, year_end=2020, month_end=5, day_end=20, cat=0, geo='ID')



