from bs4 import BeautifulSoup 
import requests 
from csv import writer
import re
import unicodedata

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'} 

def file_writer(data, file_name):
    with open(file_name, 'w', newline='\n', encoding="utf8") as write_obj:
        csv_writer = writer(write_obj, delimiter=',')
        for record in data:
            csv_writer.writerow(record)
            
def get_chief_of_state(filename):
    url = "https://www.cia.gov/library/publications/resources/world-leaders-1/"
    soup = BeautifulSoup(requests.get(url, headers=USER_AGENT).text, "html.parser") 
    result = list()
    for link in soup.findAll('li'):
        if link.find('a'):
            result.append(link.find('a').get('href'))
    
    countries = result[299:497]
    chief_of_state = list()
    
    for country in countries:
        countrySoup = BeautifulSoup(requests.get(url+country, headers =USER_AGENT ).text, "html.parser")
        countryName = countrySoup.find('span', {'id': 'countryNameSpan_'+country.replace('.html', '')}).getText().strip()
        titleList = countrySoup.find_all('span', {'class': 'title'})
        contentList = countrySoup.find_all('span', {'class': 'cos_name'})
        for i, title in enumerate(titleList):
            chief_of_state.append([countryName, title.getText().strip(), contentList[i].getText().strip()])
                 
    file_writer(chief_of_state, filename)

def get_intl_org(filename):
    url = "https://www.cia.gov/library/publications/resources/the-world-factbook/appendix/print_appendixb.html"
    soup = BeautifulSoup(requests.get(url, headers=USER_AGENT).text, "lxml") 
    
    def extract_data(className):
        dataList = soup.findAll('div', {'class': className})
        if className == "category_data":
            return [link for link in dataList]
        return [link.getText().strip() for link in dataList]
    
    def get_data_rows(data):
        input_string = unicodedata.normalize("NFKD", str(data.get_text))
        brs = ['<br>', '</br>', '<br/>']
        for br in brs:
            input_string = input_string.replace(br,'<br>')
        input_string = input_string.replace("<bound method Tag.get_text of ","")
        cate = input_string.split("<br>")
        catl = list()
        
        text = ""
    #    lookouts = ["note", "member", "observer", "candidate", "stake holder", "countries", "invitee", "partner"]
        for c in cate:
            temp = re.sub('<+/?[a-zA-Z]*(\s*[a-zA-Z]*=\".*\")*>+', '', c).strip()
            if " - " in temp and (re.search(".*\s-\s\(\d+.*\)", temp) or re.search("^\s*notes?\s-\s.*", temp)):
                catl.append(temp.split(" - ", 1))
            else:
                text += "\n" + temp
        text = text.strip()
        if text:
            catl.append(["text", text])
        return catl
    category, category_data = extract_data('category'), extract_data('category_data')
    
    result = list()
    for i, cat in enumerate(category):
        result_rows = get_data_rows(category_data[i])
        if result_rows:
            result+= [[cat] + row for row in result_rows]

    file_writer(result, filename)
    
directory =  "D://USC//ISI//CIA_Factbook_extraction//"
chief_of_state_file = directory + "ChiefOfstate.csv"
intl_org_file = directory + "IntlOrg.csv"

get_chief_of_state(chief_of_state_file)
get_intl_org(intl_org_file)