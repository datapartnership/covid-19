# Word Embedding Topic Monitoring

There are 3 data sources for this topic monitoring: [Twitter](https://github.com/datapartnership/covid19/tree/master/social_development_gp/Word%20Embedding%20Pipeline#twitter), [Instagram](https://github.com/datapartnership/covid19/tree/master/social_development_gp/Word%20Embedding%20Pipeline#instagram), [GDELT News](https://github.com/datapartnership/covid19/tree/master/social_development_gp/Word%20Embedding%20Pipeline#gdelt)

## Twitter
1) [SERVER] If data is geotagged data, then run filter_geotagged_data.py

----Location: ROOT_PATH 

----Input: Raw Data from /mnt/twitter_geolocation_data

----Output: Filtered Gee-tagged data on ROOT_PATH/Dataset/Raw

2) [SERVER] Preprocess new data using preprocessing.py 

----Location: ROOT_PATH

----Input: Raw Data from /mnt/twitter_hashtag_data

----Output: Preprocessed Data on ROOT_PATH/Dataset/Cleaned

3) [SERVER] FOR EACH new preprocessed data, Run build_final_data.py 

----Location: ROOT_PATH

----Input: Preprocessed Data from ROOT_PATH/Dataset/Cleaned

----Output: CSV File on ROOT_PATH/Dataset/Final/Not_Aggregated

4) [SERVER] Run aggregate_final_data.py 

----Location: ROOT_PATH

----!!!!! IMPORTANT: The step before has to be completed first for all new data

----Input: All CSV files on ROOT_PATH/Dataset/Final/Not_Aggregated

----Output: agg_final_data.csv file on ROOT_PATH/Dataset/Final

5) [LOCAL] Run kemkominfo_scraping.py

----Location: ROOT_PATH

6) [LOCAL] (MANUAL) Add new KEMKOMINFO data ON TOP of KEMKOMINFO_corpus.txt existing rows 

----Location: ROOT_PATH/Dataset

7) [LOCAL] (MANUAL) Add keyword for KEMKOMINFO data ON TOP of KEMKOMINFO_corpus_keyword.txt existing rows

----!!!!! IMPORTANT: IF THERE IS COVID RELATED WORD, WRITE "CORONA"

----Location: ROOT_PATH/Dataset

8) [LOCAL] (MANUAL) Add cluster for KEMKOMINFO data ON TOP of KEMKOMINFO_corpus_cluster.txt existing rows

----Location: ROOT_PATH/Dataset

9) [LOCAL] (MANUAL) Add new MAFINDO data to the BELOW of MAFINDO_corpus.txt existing rows

----Location: ROOT_PATH/Dataset

10) [LOCAL] (MANUAL) Add keyword for MAFINDO data to the BELOW of MAFINDO_corpus_keyword.txt existing rows 

----!!!!! IMPORTANT: if news already contained in kemkominfo then remove it from MAFINDO_corpus.txt

----!!!!! IMPORTANT: IF THERE IS COVID RELATED WORD, WRITE "CORONA"

----Location: ROOT_PATH/Dataset

11) [LOCAL] (MANUAL) Add cluster for MAFINDO data to the BELOW of MAFINDO_corpus_cluster.txt existing rows 

----Location: ROOT_PATH/Dataset

12) [LOCAL] (MANUAL) Copy UNIQUE MAFINDO & KEMKOMINFO data to the below of news_corpus.txt existing rows

----Location: ROOT_PATH/Dataset

13) [LOCAL] (MANUAL) Copy keyword for MAFINDO & KEMKOMINFO data to the BELOW of news_corpus_keyword.txt existing rows

----Location: ROOT_PATH/Dataset

14) [LOCAL] (MANUAL) Copy cluster for MAFINDO & KEMKOMINFO data to the BELOW of news_corpus_cluster.txt existing rows

----Location: ROOT_PATH/Dataset

15) [LOCAL -> SERVER] Move newly created news_corpus.txt to SERVER /mnt/louis/Dataset

16) [LOCAL -> SERVER] Move newly created news_corpus_keyword.txt to SERVER /mnt/louis/Dataset

17) [LOCAL -> SERVER] Move newly created news_corpus_cluster.txt to SERVER /mnt/louis/Dataset

18) [SERVER] Delete news_corpus_verb.txt

---Location: ROOT_PATH/Dataset

19) [SERVER] Run extract_verb_keyword.py 

----Location: ROOT_PATH

----Output: news_corpus_verb.txt on ROOT_PATH/Dataset

20) [SERVER] Run train_w2v_weekly.py 

----Location: ROOT_PATH/Issue Monitoring

----Output: model file on ROOT_PATH/Issue Monitoring/model

21) [SERVER] Run train_w2v_all.py 

----Location: ROOT_PATH/Issue Monitoring

----Output: model file on ROOT_PATH/Issue Monitoring/model

22) [SERVER] Run extract_similar_keyword_user_level.py

----Location: ROOT_PATH/Issue Monitoring

----Output: CSV files on ROOT_PATH/Issue Monitoring

23) [SERVER] Delete news_corpus_keyword_expanded.txt

----Location: ROOT_PATH/Dataset

24) [SERVER] Run expand_news_corpus_keyword.py

----Location: ROOT_PATH

----Output: news_corpus_keyword_expanded.txt on ROOT_PATH/Dataset

25) [SERVER] Run extract_closest_news.py using --type keyword_expanded

----Location: ROOT_PATH

26) [SERVER] Run extract_similar_keyword.py 

----Location: ROOT_PATH/Issue Monitoring

----Output: CSV files on ROOT_PATH/Issue Monitoring

27) [SERVER] Run age_gender_infer_region.py 

----Location: ROOT_PATH/Demographic_Prediction

----Output: twitter_demographic_100_region.csv

28) [SERVER] Run age_gender_infer_topic.py --data twitter

----Location: ROOT_PATH/Demographic_Prediction

----Output: twitter_demographic_topic.csv

29) [SERVER] Run plot_sentiment_time_series.py 

----!!!!! IMPORTANT: agg_final_data_insta.csv should be updated first

----Location: ROOT_PATH/Issue Monitoring

----Output: sentiment_timeseries.png

30) [SERVER] Run extract_sentiment_top_10_urls.py

----Location: ROOT_PATH/Issue Monitoring

----Output: ROOT_PATH/Issue Monitoring/sentiment_top_10_urls.csv

31) [SERVER] Run extract_sentiment_top_10_users.py --criteria retweet

----Location: ROOT_PATH/Issue Monitoring

----Output: CSV Files in ROOT_PATH/Issue Monitoring

32) [SERVER] Run extract_sentiment_top_10_users.py --criteria reply

----Location: ROOT_PATH/Issue Monitoring

----Output: CSV Files in ROOT_PATH/Issue Monitoring

33) [SERVER] Run extract_sentiment_top_20_keywords_confidence_in_government.py

----Location: ROOT_PATH/Issue Monitoring

----Output: ROOT_PATH/Issue Monitoring/sentiment_top_20_keywords_confidence_in_government.csv

34) [SERVER] Run extract_sentiment_top_20_keywords_confidence_in_government_new_normal.py

----Location: ROOT_PATH/Issue Monitoring

----Output: ROOT_PATH/Issue Monitoring/sentiment_top_20_keywords_confidence_in_government_new_normal.csv

35) [SERVER -> Local] Download results from step 22, 26, 27, 28, 29, 30, 31, 32, 33, 34

36) [SERVER] Run extract_twitter_stats.py

----Location: ROOT_PATH

37) [Local] Edit Twitter Stats from result no 36

38) [Local] Run viz_demographic_region.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

39) [Local] Edit Bar chart and Pie Chart for age gender Twitter in slides report from viz_demographic_region.ipynb

40) [Local] Run viz_demographic_topic.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

41) [Local] Run viz_keyword_count.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

42) [Local] Run viz_daily_comparison_new_normal.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

43) [Local] Run viz_keyword_count_new_normal.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

44) [Local] Run viz_areachart_weekly_evolution.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

45) [Local] Run viz_areachart_weekly_evolution_new_normal.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

46) [Local] Run viz_policy_user_level_all.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

47) [Local] Run viz_policy_user_level_all_new_normal.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

48) [Local] Run viz_policy_user_level_weekly.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

49) [Local] Run viz_policy_user_level_weekly_new_normal.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

50) [Local] Run viz_policy_user_level_overlaps.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

51) [Local] Run viz_sentiment_distribution_top_20_keywords.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

52) [Local] Run viz_sentiment_distribution_top_20_keywords_new_normal.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

53) [Local] Run viz_sentiment_distribution_top_10_domain.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

54) [Local] Run viz_sentiment_distribution_top_10_users.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

55) [Local] Run viz_sentiment_distribution_top_10_users_tweets_percentage.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output 

56) [Local] Upload top_tweet_top_10_reply_users.csv & top_tweet_top_10_retweet_users.csv to GDrive

----Location: ROOT_PATH/Issue Monitoring/data

57) [SERVER] Run extract_url.py 

----!!!!! IMPORTANT: Specifiy args only for new tweets file. Run it file by file

----Input: NEW RAW Data file 

----Output: /mnt/louis/Dataset/URL_list.txt

58) [SERVER] Run extract_top_urls.py

-----Input: /mnt/louis/Dataset/URL_list.txt

-----Output: /mnt/louis/Dataset/TOP_URLs.csv

59) [SERVER] Run extract_top_web_domain.py

----Input: /mnt/louis/Dataset/URL_list.txt

-----Output: /mnt/louis/Dataset/TOP_domain.csv

## Instagram

1) [SERVER] Preprocess new data using preprocessing_insta.py 

----Location: ROOT_PATH

----Input: Raw Data from /mnt/instagram/

----Output: Preprocessed Data on ROOT_PATH/Dataset/Instagram/Cleaned

2) [SERVER] FOR EACH new preprocessed data, build_final_data_insta.py

----Location: ROOT_PATH

----Input: Preprocessed Data from ROOT_PATH/Dataset/Instagram/Cleaned

----Output: CSV File on ROOT_PATH/Dataset/Instagram/Final/Not_Aggregated

3) [SERVER] Run aggregate_final_data_insta.py 

----!!!!! IMPORTANT: The step before has to be completed first for all new data

----Location: ROOT_PATH

----Input: All CSV files on ROOT_PATH/Dataset/Instagram/Final/Not_Aggregated

----Output: agg_final_data.csv file on ROOT_PATH/Dataset/Instagram/Final

4) [SERVER] Run train_w2v_weekly_insta.py

----Location: ROOT_PATH/Issue Monitoring

----Output: model file on ROOT_PATH/Issue Monitoring/model

5) [SERVER] Run extract_similar_keyword_user_level_insta.py 

----Location: ROOT_PATH/Issue Monitoring

----Output: CSV files on ROOT_PATH

6) [SERVER] Run age_gender_infer_100.py --data instagram

----Location: ROOT_PATH/Demographic_Prediction

----Output: CSV file on ROOT_PATH

7) [SERVER] Run age_gender_summarize_instagram.py

----Location: ROOT_PATH/Demographic_Prediction

8) [Local] Edit Bar chart and Pie Chart for age gender Instagram in slides report from the results of age_gender_summarize_instagram.py

9) [SERVER] Run extract_instagram_stats.py

----Location: ROOT_PATH

10) [Local] Edit Instagram Stats from result no 9

11) [SERVER -> Local] Download results from step 5

12) [Local] Run viz_policy_user_level_all_insta.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

13) [Local] Run viz_policy_user_level_all_new_normal_insta.ipynb

---Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

14) [Local] Run viz_policy_user_level_weekly_insta.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

15) [Local] Run viz_policy_user_level_weekly_new_normal_insta.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

16) [Local] Run viz_policy_user_level_overlaps_insta.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Chart on ROOT_PATH/Issue Monitoring/chart_output

## GDELT
1) [SERVER] Preprocess new data using preprocessing_gdelt.py

----Location: ROOT_PATH

----Input: Generated Data from /mnt/alicia/indonesian_news

----Output: Preprocessed Data on ROOT_PATH/Dataset/GDELT

2) [SERVER] Run train_w2v_weekly_gdelt.py

----Location: ROOT_PATH/Issue Monitoring

----Output: model file on ROOT_PATH/Issue Monitoring/model

3) [SERVER] Run train_w2v_all_gdelt.py

----Location: ROOT_PATH/Issue Monitoring

----Output: model file on ROOT_PATH/Issue Monitoring/model

4) [SERVER] Run extract_similar_keyword_user_level_gdelt.py

----Location: ROOT_PATH/Issue Monitoring

----Output: CSV files on ROOT_PATH

5) [SERVER] Run extract_similar_keyword_gdelt.py

----Location: ROOT_PATH/Issue Monitoring

----Output: CSV files on ROOT_PATH

6) [SERVER] Run extract_sentiment_top_10_gdelt_domain.py

----Location: ROOT_PATH/Issue Monitoring

----Output: CSV files on ROOT_PATH

7) [SERVER -> Local] Download results from step 4, 5, 6

8) [SERVER] Run extract_gdelt_stats.py

----Location: ROOT_PATH

9) [Local] Edit GDELT Stats from result no 8

10) [Local] Run viz_sentiment_distribution_top_10_domain_gdelt.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Charts on ROOT_PATH/Issue Monitoring/chart_output

11) [Local] Run viz_keyword_count_gdelt.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Charts on ROOT_PATH/Issue Monitoring/chart_output

12) [Local] Run viz_keyword_count_new_normal_gdelt.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Charts on ROOT_PATH/Issue Monitoring/chart_output

13) [Local] Run viz_areachart_weekly_evolution_gdelt.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Charts on ROOT_PATH/Issue Monitoring/chart_output

14) [Local] Run viz_areachart_weekly_evolution_new_normal_gdelt.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Charts on ROOT_PATH/Issue Monitoring/chart_output

15) [Local] Run viz_policy_user_level_all_gdelt.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Charts on ROOT_PATH/Issue Monitoring/chart_output

16) [Local] Run viz_policy_user_level_all_new_normal_gdelt.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Charts on ROOT_PATH/Issue Monitoring/chart_output

17) [Local] Run viz_policy_user_level_weekly_gdelt.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Charts on ROOT_PATH/Issue Monitoring/chart_output

18) [Local] Run viz_policy_user_level_weekly_new_normal_gdelt.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Charts on ROOT_PATH/Issue Monitoring/chart_output

19) [Local] Run viz_policy_user_level_overlaps_gdelt.ipynb

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Charts on ROOT_PATH/Issue Monitoring/chart_output

20) [Local] Run viz_wordcloud_topic_keywords_compare.py

----!!!!! IMPORTANT: output data for Twitter, Instagram, and GDELT have to be downloaded first

----Location: ROOT_PATH/Issue Monitoring

----Output: PNG Charts on ROOT_PATH/Issue Monitoring/wordcloud_output
