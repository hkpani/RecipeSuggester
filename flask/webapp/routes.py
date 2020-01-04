from flask import render_template, flash, redirect, session, request
from webapp import app
from webapp import mongo
from webapp.forms import LoginForm
from webapp.forms import RegisterForm
from webapp.forms import RecipeForm
from webapp.forms import SaveDataForm
from webapp.forms import DiscardDataForm
from webapp.scraping_functions import scrape_recipe
from webapp.scraping_functions import read_from_db
from webapp.scraping_functions import return_curated_URL
from webapp.scraping_functions import get_last_search
from webapp.scraping_functions import set_last_search
from webapp.scraping_functions import create_url
from webapp.scraping_functions import set_saved_recipes
from webapp.users import verifyCredentials
from webapp.users import storeUser

#Format of web pages below:
#index page will be the home page showcasing username and last search
#login page will have a username and password system to log into
#logout page will successfully end the current user session 
#register page will let new users create accounts
#recipesearch page is the main searching tool
#recipes page will list the recipes saved by user and the current recipe list


@app.route('/login', methods =['GET','POST']) #default method is only GET, have to also specify POST method
def login():
    form = LoginForm()
    #if its a GET method, render the register.html template, otherwise grab the form data from the POST and register the user
    if form.validate_on_submit():
        account_success = verifyCredentials(form.username.data,form.password.data) #each wtform has data element for the passed data

        if account_success:
            session['username'] = form.username.data #setting the user to the flask app before redirecting to homepage
            flash('Successfully logged in as user {}!'.format(form.username.data))
            return redirect('/index')
        else:
            flash('Looks like the Username you entered is invalid, try again')
            return redirect('/login')

    return render_template('login.html',title = 'Whats for Dinner-Login', form = form)

@app.route('/')
@app.route('/index')
def index():

    #since username is a dictionary entry, can't reference it if it doesn't exist yet
    if 'username' in session:
        user = {'username':session['username']}
    else:
        user =  {'username':None}

    print("username:{}".format(user['username']))
    if user['username'] is None: 
        user_id = None
        curated_url = None
    else:
        user_id = user['username']
        curated_url = get_last_search(user['username'])

    recipes = [{'chef':user_id,'recipe':curated_url}]


    #return render_template('index.html',title ='Whats for Dinner',user = user)
    return render_template('index.html', title ='Whats for Dinner-main', user = user, recipes = recipes)
@app.route('/recipes',methods =['GET','POST'])
def recipes():
    #since username is a dictionary entry, can't reference it if it doesn't exist yet
    if 'username' in session:
        user = {'username':session['username']}
    else:
        user = {'username':None}

    #if this is a get method don't display anything (User shouldnt be on this page anyways)
    result = None 
    recipe = None

    if 'username' in session:
        result = get_last_search(user['username'])
        if result == 'User has not made a search yet':
            recipe = None
        else:
            recipe = {'recipe':result}

    saveform = SaveDataForm()
    discardform = DiscardDataForm() 

    if saveform.validate_on_submit():

        if user['username']:
            set_saved_recipes(user['username'],get_last_search(user['username']))
            flash('Recipe saved in db')
            return redirect('/index')

    if discardform.validate_on_submit(): 
            flash('Discarded recipe, start a new search')
            return redirect('/index')

    
    return render_template('recipes.html',title = 'Whats for Dinner-recipeList', user=user,saveform = saveform, discardform = discardform, recipes = recipe)

@app.route('/register',methods =['GET','POST'])
def register():
    #if its a GET method, render the register.html template, otherwise grab the form data from the POST and register the user
    form = RegisterForm()
    if form.validate_on_submit():
        account_success = storeUser(form.username.data,form.password.data) #each wtform has data element for the passed data

        if account_success:
            session['username'] = form.username.data #setting the user to the flask app before redirecting to homepage
            flash('Successfully created user {}!'.format(form.username.data))
            return redirect('/index')
        else:
            flash('Looks like the Username is invalid or taken, try again')
            return redirect('/register')

    #if we reach here, it was a GET method
    return render_template('register.html',title = 'Whats for Dinner-Login', form = form)

@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html',title = 'Whats for Dinner-logout')

@app.route('/recipesearch',methods =['GET','POST'])
def recipesearch():
    inputform = RecipeForm()
    recipe_list = []
    curated_recipe = []
    
    if 'username' in session:
        user = {'username':session['username']}
    else:
        user =  {'username':None}

    #if its a GET method, render the recipesearch.html template, otherwise grab the form data from the POST and register the user
    if inputform.validate_on_submit():
        
        if user['username']:
            recipe_list = read_from_db(inputform.base_recipe.data,[inputform.additive1.data,inputform.additive2.data],session['username'])
            if not recipe_list: #base recipe doesn't exist in database, so scrape first and then search again
                #TODO : Make pages scraped a variable feature and potentially flash a message whilst scraping (if possible)
                scrape_recipe(2,create_url(inputform.base_recipe.data),inputform.base_recipe.data,user['username'])
                recipe_list = read_from_db(inputform.base_recipe.data,[inputform.additive1.data,inputform.additive2.data],session['username'])
                if recipe_list: # can't append if nothing is scraped from the website
                    curated_recipe.append(return_curated_URL(recipe_list))


            #second time around means invalid recipe was entered
            if not recipe_list:
                flash('Looks like there are no recipes for this, try a different search')
                return redirect('/recipesearch')
            else:
                curated = return_curated_URL(recipe_list)
                set_last_search(user['username'],curated)
                flash('Curated recipe below')
                return redirect('/recipes')

    return render_template('recipesearch.html',title = 'Whats for Dinner-Login', user = user, inputform = inputform, recipe=curated_recipe)
