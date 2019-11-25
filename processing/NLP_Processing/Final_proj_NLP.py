import json
import html2text
h = html2text.HTML2Text()
h.ignore_links = True
h.ignore_images = True
import re
import pprint
from bs4 import BeautifulSoup

mydict = {}
with open('../output2.json') as f:
  data = json.load(f)

skip_f = open('../skiplist.txt',"r")
skip_list = []
for line in skip_f:
    skip_list.append(line.strip())

print(skip_list)

for line in data:
    if line['title'] in skip_list:
        print ("Skipping "+line['title'])
    else:
        item = line
        soup = BeautifulSoup(item['html'], 'html.parser')
        company = item['title']
        mydict[company] = {}

        #####This extracts the INFOBOX in the right
        tables = soup.find_all("table",class_="infobox vcard")
        for table in tables:
            for tr in table.find_all('tr'):
                if tr.find('th'):
                    key = tr.find('th').text.strip()
                    if(tr.find('td')):
                        if(tr.find('td').find_all('br')):
                            value = tr.find('td').get_text(separator=";")
                        else:
                            value = tr.find('td').get_text()
                        mydict[company][key] = value

        #####This extracts text in each header 2
        for header in soup.find_all("h2"):
            header_name = header.text
            headertext = ""
            mydict[company][header_name] = []
            for elem in header.next_siblings:
                if elem.name == "h2":
                    break
                if elem.name == "table":  #This part converts any table into a list of dictionaries
                    list_of_sub_dict= []
                    # The first tr contains the field names.
                    headings = [th.get_text().strip() for th in elem.find("tr").find_all("th")]
                    datasets = []
                    for row in elem.find_all("tr")[1:]:
                        dataset = dict(zip(headings, (td.get_text().strip() for td in row.find_all("td"))))
                        list_of_sub_dict.append(dataset)
                    mydict[company][header_name].append(list_of_sub_dict)
                if elem.name != 'p':
                     continue
                else:
                     headertext = headertext+elem.get_text()
            mydict[company][header_name].append(headertext)

        ######This extracts main intro part
        Introtext = ""
        start = soup.find('p')
        if (start):
            for elem in start.next_siblings:
                if elem.name == 'h2':
                    break
                if elem.name != 'p':
                    continue
                else:
                    #print(elem.name)
                    Introtext = Introtext + elem.text.strip()
        mydict[company]['Intro'] = Introtext

with open("updated_scraped_data.json", "w") as f:
    f.write(json.dumps(mydict, indent=4))
# #pprint.pprint(mydict)