import urllib3
from bs4 import BeautifulSoup
import pandas as pd
import re
from time import sleep
import json

def get_ingredients(url_to_scrape, ingredients):
    #create PoolManager for HTTP requests
    http = urllib3.PoolManager()
    #Don't want to send Too many Requests to the website so sleep for a while 
    sleep(2)

    source_code = http.request('GET',url_to_scrape)

    soup = BeautifulSoup(source_code.data,'lxml')

    #block = soup.find_all('ul',class_='checklist dropdownwrapper list-ingredients-1')
    li_block = soup.find_all('li',class_='checkList__line')
    print(li_block)

    temp_ingredients = []

    for y in li_block:
        #get the title which contains the whole string containing quantity, unit MM and ingredient
        title_string = y.find(name='label',title=True)
        if(title_string):
            temp_ingredients.append(title_string['title'])

    #append to the caller's list
    ingredients.append(temp_ingredients)

def scrape_recipe(num_pages,scrape_url,df_update,keyword):
    # Columns for the dataframe
    df_columns = ['Tag','Name','URL','Ingredients']
    #create PoolManager for HTTP requests
    http = urllib3.PoolManager()

    for x in range(1,num_pages):
        if x == 1:
            pass
        else:
            scrape_url = scrape_url + "&page=" + str(x)

        source_code = http.request('GET',scrape_url)

        soup = BeautifulSoup(source_code.data,'lxml')

        block = soup.find_all('div',class_='grid-card-image-container')

        dish_tag = keyword
        dish = []
        link = []
        ingredients = []

        for y in block:
            temp_title = y.find(name='img',title=True)
            temp_link = y.find(name='a',href=True)
            #check using regex to see if title has the keyword in it
            #first convert to lowercase
            #check_string = temp_title['title'].lower()
            #search function goes through the string and returns match object if found
            #if re.search(keyword.lower(),check_string):
            #    dish.append(temp_title['title'])
            #    link.append(temp_link['href'])
            #    get_ingredients(link)
            dish.append(temp_title['title'])
            link.append(temp_link['href'])
            #this step gets all the ingredients, quantity and unit MM for each row
            get_ingredients(temp_link['href'],ingredients)

        df_data = {df_columns[0]:[dish_tag for x in range(len(dish))],df_columns[1]:dish,df_columns[2]:link,df_columns[3]:ingredients}

        #append the collected dishes and respective URLs to the dataframe
        df_temp = pd.DataFrame(data=df_data)
        #doesn't happen in-place , have to actually store it in the original dataframe
        df_update = df_update.append(df_temp,ignore_index=True)

        #Don't want to send Too many Requests to the website so sleep for a while 
        sleep(2)

    json_data = df_update.to_json(orient='records')

    #for now, lets print our json formatted data that we scraped
    print(json_data)