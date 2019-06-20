import urllib3
from bs4 import BeautifulSoup
import pandas as pd
import re
import random
from time import sleep
import json
from pymongo import MongoClient
from webapp import mongo

def get_ingredients(url_to_scrape, ingredients):
    #create PoolManager for HTTP requests
    http = urllib3.PoolManager()
    #Don't want to send Too many Requests to the website so sleep for a while 
    sleep(2)

    source_code = http.request('GET',url_to_scrape)

    soup = BeautifulSoup(source_code.data,'lxml')

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

def store_to_db(json_data):

    #using the pymongo object in the app we made, we can just directly access members
    #select the recipes collection which is a member of mongo(recipe_db)
    posts = mongo.db.recipes

    #insert json formatted data into recipes db
    posts.insert_many(json_data)

def read_from_db(base_tag, additives,userID):
    #This method narrows down the list of URLs to send to the front-end method call 
    #based on the base recipe additives the user has input for a more refined search

    result_list = []

    #using the pymongo object in the app we made, we can just directly access members
    #select the recipes collection which is a member of mongo(recipe_db)
    posts = mongo.db.recipes

    #finding all recipes with the userID AND base recipe specified 
    search = posts.find({'user_id':userID,'Tag':base_tag})

    for x in search:
        in_list = True
        #if subset of current ingredients append URL to the result list
        for y in additives:
            #Make sure all the additives are in the recipe before appending to the return list
            if not any(y in s for s in x['Ingredients']):
                in_list = False

        if in_list:
            result_list.append(x['URL'])

    return result_list

def return_curated_URL(URL_list):
    #This method is meant to take the output list of the narrowed list generated from
    #the read_from_db method and spit out a random URL from the list
    random.seed(a=None)

    curated_elem = random.randint(0,len(URL_list)-1)

    return URL_list[curated_elem]

def scrape_recipe(num_pages,scrape_url,keyword,userID):
    #empty dataframe to append to
    df_update = pd.DataFrame()

    # Columns for the dataframe
    df_columns = ['user_id','Tag','Name','URL','Ingredients']
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

        df_data = {df_columns[0]:[userID for x in range(len(dish))],df_columns[1]:[dish_tag for x in range(len(dish))],df_columns[2]:dish,df_columns[3]:link,df_columns[4]:ingredients}

        #append the collected dishes and respective URLs to the dataframe
        df_temp = pd.DataFrame(data=df_data)
        #doesn't happen in-place , have to actually store it in the original dataframe
        df_update = df_update.append(df_temp,ignore_index=True)

        #Don't want to send Too many Requests to the website so sleep for a while 
        sleep(2)

    #json_data = df_update.to_json(orient='records')
    json_data = df_update.to_dict('records')

    #print(json_data)

    if json_data: #check if there is data before storing in mongo collection, otherwise error will be thrown
        store_to_db(json_data)

    #Debug : print our json formatted data that we scraped
    #print(json_data)

def create_url(recipe):
    keyword_list = recipe.split()

    if len(keyword_list)>1:
        #append %20 after earch search word
        for x in keyword_list:
            search_url = "https://www.allrecipes.com/search/results/?wt=" + x + "%20" 
        search_url += "&sort=re"
    else:
        #don't have to format string with %20 after each input word
        search_url = "https://www.allrecipes.com/search/results/?wt=" + ingredient_keyword + "&sort=re"

    return search_url


def get_last_search(user_id):
    #returns last searched recipe
    posts = mongo.db.userData

    #since data is for one user, just use find_one
    user = posts.find_one({'user_id':user_id})

    search = user['last_search']

    if search is not None:
        return search
    else:
        return "User has not made a search yet"

def set_last_search(user_id,URL):
    #use set method to update the last search value
    posts = mongo.db.userData

    posts.update({'user_id':user_id},{'$set': {'last_search':URL}})

def get_saved_recipes(user_id):
    #returns current list of saved recipes
    posts = mongo.db.userData

    search = posts.find_one({'user_id':user_id})

    return search['saved_recipes']

def set_saved_recipes(user_id,URL):
    #use push method to append the newly saved recipe to the list
    posts = mongo.db.userData

    posts.update({'user_id':user_id},{'$push': {'saved_recipes':URL}})
