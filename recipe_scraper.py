import pandas as pd
from scraping_functions import scrape_recipe
from scraping_functions import read_from_db
from scraping_functions import return_curated_URL

#this is a temporary test file for making sure the methods in scraping_functions.py are working as intended
#this will be replaced with a more friendly front-end experience

#customization variables for figuring out amount of data to scrape and recipe keyword
last_page = 2
ingredient_keyword = 'chicken parmesan'
additive_list = ['salt','oregano']
user_id = 'Hank Hill'

#create an initial dataframe to append to
df = pd.DataFrame() 

keyword_list = ingredient_keyword.split()

if len(keyword_list)>1:
    #append %20 after earch search word
    for x in keyword_list:
        search_url = "https://www.allrecipes.com/search/results/?wt=" + x + "%20" 
    search_url += "&sort=re"
else:
    #don't have to format string with %20 after each input word
    search_url = "https://www.allrecipes.com/search/results/?wt=" + ingredient_keyword + "&sort=re"

#max number of pages this scrapes is 10 anyways
#scrape_recipe(last_page,search_url,df,ingredient_keyword,user_id)

curated_list = read_from_db(ingredient_keyword,additive_list,user_id)
#This is to make sure we aren't putting an illegal range with the rand function
if len(curated_list) > 0:
	print(return_curated_URL(curated_list))
    