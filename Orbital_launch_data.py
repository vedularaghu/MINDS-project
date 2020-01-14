import requests
from bs4 import BeautifulSoup
import re
import dateutil
from dateutil.parser import parse
import csv
from datetime import datetime, timedelta
import pandas as pd

page = requests.get('https://en.wikipedia.org/wiki/2019_in_spaceflight#Orbital_launches').text

soup = BeautifulSoup(page, 'lxml')

print(soup.prettify())

my_table = soup.find('table', {'class':'wikitable collapsible'})

def is_date(string, fuzzy=True):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

def check_date(date_string):
    try:
        datetime.strptime(date_string, "%d %B")
        return "Without Time"
    
    except:
        pass
    
    try:
        datetime.strptime(date_string, "%d %B%H:%M:%S")
        return "With Seconds"
    
    except:
        pass
    
    try:
        datetime.strptime(date_string, "%d %B%H:%M")
        return "Without Seconds"
    
    except:
        return False

def save_date(text):
    orbital_date = re.sub(r'\[.*?\]', '', i)
    if is_date(orbital_date):
        if check_date(orbital_date) == "Without Time":
            d = datetime.strptime(orbital_date, "%d %B")
            d = d.replace(year=2019, hour=00, minute=00, second=00)
            return(d.isoformat())                    
        elif check_date(orbital_date) == "Without Seconds":                    
            d = datetime.strptime(orbital_date, "%d %B%H:%M")
            d = d.replace(year=2019, second=00)
            return(d.isoformat())
        elif check_date(orbital_date) == "With Seconds":
            d = datetime.strptime(orbital_date, "%d %B%H:%M:%S")
            d = d.replace(year=2019)
            return(d.isoformat())


regex = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'
match_iso8601 = re.compile(regex).match
def validate_iso8601(str_val):
    try:            
        if match_iso8601( str_val ) is not None:
             return True
    except:
         pass
    return False


orbital_launch_data = []
ol_body = my_table.find('tbody')
ol_rows = ol_body.find_all('tr')

for row in ol_rows:
    ol_cols = row.find_all('td')
    ol_cols = [ele.text.strip() for ele in ol_cols]
    #print(cols)
    orbital_launch_data.append([ele for ele in ol_cols if ele])
orbital_launch_data.remove(orbital_launch_data[0])


first_item = [item[0] for item in orbital_launch_data]
date_list = []

for i in first_item:
    orbital_date = re.sub(r'\[.*?\]', '', i)
    if is_date(orbital_date):
        if check_date(orbital_date) == "Without Time":
            d = datetime.strptime(orbital_date, "%d %B")
            d = d.replace(year=2019, hour=00, minute=00, second=00)
            date_list.append(d.isoformat()) 
            first_item[first_item.index(i)] = d.isoformat()
        elif check_date(orbital_date) == "Without Seconds":                    
            d = datetime.strptime(orbital_date, "%d %B%H:%M")
            d = d.replace(year=2019, second=00)
            date_list.append(d.isoformat())
            first_item[first_item.index(i)] = d.isoformat()
        elif check_date(orbital_date) == "With Seconds":
            d = datetime.strptime(orbital_date, "%d %B%H:%M:%S")
            d = d.replace(year=2019)
            date_list.append(d.isoformat())
            first_item[first_item.index(i)] = d.isoformat()
            

final_date = []
            
start_date = datetime(2019, 1, 1)   
end_date = datetime(2019, 12, 31)  

delta = end_date - start_date      

for i in range(delta.days + 1):
    count = 0
    day = start_date + timedelta(days=i)
    for j in date_list:
        yourdate = dateutil.parser.parse(j)
        if str(yourdate.date()) == str(day.date()):
            final_date.append(yourdate.isoformat())
            count += 1
    if count == 0:
        final_date.append(day.isoformat())   

last_item = [item[-1] for item in orbital_launch_data]          

count_list = {}
for item in orbital_launch_data:
    for i in item:
        if validate_iso8601(save_date(i)) == True:
            item[item.index(i)] = save_date(i)

count = 1
flag = 0
for item in orbital_launch_data:
        for i in item:
            if validate_iso8601(i) == True:
                flag = 1
            if flag == 1:
                if (validate_iso8601(i) == True) and (i in date_list):
                    count_date = i
                    count_list[count_date] = count
                    count = 0
                if i == 'Successful' or i == 'Operational' or i == 'En Route':
                            count += 1
                            count_list[count_date] = count

list1 = []

for item in final_date:
    if item in count_list:
        list1.append(count_list[item])
    else:
        list1.append('0')

df = pd.DataFrame({'col1': final_date, 'col2': list1})
df.to_csv('output.csv', index=False)





