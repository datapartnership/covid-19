# script to use data from https://github.com/ActiveConclusion/COVID19_mobility which scrapes google and apple mobility reports every day
import sys,os;

google_link = "https://github.com/ActiveConclusion/COVID19_mobility/blob/master/google_reports/mobility_report_countries.csv?raw=true";
apple_link = "https://github.com/ActiveConclusion/COVID19_mobility/blob/master/apple_reports/apple_mobility_report.csv?raw=true";

#apple: country,sub-region,subregion_and_city,geo_type,date,driving,transit,walking
#google: country,region,date,retail,grocery and pharmacy,parks,transit stations,workplaces,residential

command1 = "echo date,retail,grocery and pharmacy,parks,transit stations,workplaces,residential > /var/www/html/google_mobility_trends.csv"
out = open("/var/www/html/google_mobility_trends.csv","w");
out.write("date\tretail\tgrocery and pharmacy\tparks\ttransit stations\tworkplaces\tresidential\n");

google_command = 'wget -qO- "https://github.com/ActiveConclusion/COVID19_mobility/blob/master/google_reports/mobility_report_countries.csv?raw=true" | grep "Indonesia,Total" | cut -f3- -d"," > /tmp/1'
os.system(google_command);
f = open("/tmp/1");
lines = f.readlines();
for line in lines:
    line = line.strip();
    line_split = line.split(",");
    out.write(line_split[0].replace("-","") + "\t" + ("\t").join(line_split[1:]) + "\n");
out.close();

out = open("/var/www/html/apple_mobility_trends.csv","w");
#out = open("/tmp/2","w");
out.write("date\tdriving\twalking\n");
#apple_command = 'wget -qO- "https://github.com/ActiveConclusion/COVID19_mobility/blob/master/apple_reports/apple_mobility_report.csv?raw=true" | grep "Indonesia,Total" | cut -f5,6,8 -d"," | sed -e"s/,/\t/g" | sed -e"s/-//g" >> /var/www/html/apple_mobility_trends.csv'
apple_command = 'wget -qO- https://covid19-static.cdn-apple.com/covid19-mobility-data/current/v3/en-us/applemobilitytrends-2020-06-15.csv | grep "geo_type,region,transportation_type\|country/region,Indonesia," > /tmp/ghh'
os.system(apple_command);
#os.system(command1);
f = open("/tmp/ghh");
lines = f.readlines();
line0_split = lines[0].split(",");
line1_split = lines[1].split(",");
line2_split = lines[2].split(",");

for i in range(6,len(line0_split)):
    out.write(line0_split[i].replace("-","").strip() + "\t" + line1_split[i].strip() + "\t" + line2_split[i].strip() + "\n")
out.close();
