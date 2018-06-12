import pandas as pd
from scraping_functions import scrape_recipe

#customization variables for figuring out amount of data to scrape and recipe keyword
last_page = 1
ingredient_keyword = 'chicken parmesan'

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
scrape_recipe(last_page,search_url,df,ingredient_keyword)
    