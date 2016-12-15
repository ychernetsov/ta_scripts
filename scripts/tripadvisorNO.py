#This is query API endpoint: "https://extraction.import.io/query/extractor/{Extractor GUID}?_apikey={yourAPIKey}"

# This is the framework for chaining the Extractors required to do the tripadvisorNO extraction
# You will need to parse the json at each step that you wish to collect data.

# Steps:
# 1. Get all links generated by Extractor1
# 2. Query links from Extractor1 and get last page value from each link
# 3. Based on location id and lat page generate all links for all locations 

Extractor1 = "afd62919-3ed5-47fa-9bb0-4f83aaf26198" #Replace this with the GUID of YOUR Extractors (Locations List)


import json
import urllib
import re
import csv
import time # if you want to pause between queries

#It is best to store your API Key in a separate file - this is something that you should not share. Create yourself a .txt file and put your APIKey in this file.
apikey = open("apikey.txt")
apikey = apikey.read()
e = open('errors.txt','w') #file for errors
with open('TripAdvisorNO_step1_urls.csv','wb') as f: # if you want to upload URLs directly to the import.io dashboard you can write the results to a .csv file and upload it manually
    writer = csv.writer(f)

    # 1. Get all links generated by Extractor1
    page = 0
    total = 380 # there are 113 pages with step 20
    page_counter = 1
    error_page = 0
    while page < total:
        print "Querying page ", page_counter, " from ", total/20+1, " pages..."
        try:
            page = str(page)
            jsonurl = "https://extraction.import.io/query/extractor/"+Extractor1+"?_apikey="+apikey+"&url=https%3A%2F%2Fwww.tripadvisor.co.uk%2FRestaurants-g190455-oa"+page+"-Norway.html%23LOCATION_LIST"
            data = urllib.urlopen(jsonurl).read()
            info = json.loads(data)
            result = info['extractorData']['data'][0]['group']
            page = int(page)
            page += 20
            page_counter += 1

            #location id is presented in every single url within -g{location_id}-. Below reGexp is applied to retreive location id from the url 
            #every result contains 20 urls, so we should loop through each result to get an access to each url
            for idx in range(0, len(result)):
                match_id_location = re.search(r'-g(\d+)-', result[idx]['link'][0]['href']) #regexp pattern for location id
                location_id = match_id_location.group(1) #matching location id

                # 2. Query links from Extractor1 and get last page value from each link
                url = result[idx]['link'][0]['href']
                htmlfile = urllib.urlopen(url)
                htmltext = htmlfile.read()

                #not all cases have pagination. We use try except construction
                #if case has pagination
                try:
                    match_lastpage = re.search(r"\('STANDARD_PAGINATION', 'last', '(\d+)', 0\)", htmltext) #regexp pattern for lats page 
                    last_page = match_lastpage.group(1)#matching last page

                    # 3. Based on location id and lat page generate all links for all locations
                    for i in range(0, int(last_page)):
                        link = "https://www.tripadvisor.co.uk/RestaurantSearch?Action=PAGE&geo="+location_id+"&ajax=1&itags=10591&sortOrder=popularity&o=a"+str(i*30)+"&availSearchEnabled=true"
                        writer.writerow([link]) 
                #if case doesn't have pagination             
                except:
                    link = url
                    writer.writerow([link])
        except Exception as errors:
            page = int(page)
            page += 20
            print "Page ", page_counter, " didn't responded"
            page_counter += 1
            error_page += 1
            e.write(str(error_page)+". "+str(errors.message) + '\n')
            pass

print "Queried ", page_counter - error_page, " pages from ", total/20+1, " in total"
f.close()

#now you can open TripAdvisorNO_step1_urls.csv with generated urls and use all these links for the next extractor in dash - JustEat 2 - TripAdvisorNO (restList) d21ef074-c058-4d5f-abb7-3dc9e4d35a21

        
         

