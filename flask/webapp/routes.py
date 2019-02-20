from flask import render_template, flash, redirect, session, request
from webapp import app
from webapp import mongo
from webapp.forms import LoginForm
from webapp.forms import RegisterForm
from webapp.scraping_functions import read_from_db
from webapp.scraping_functions import return_curated_URL
from webapp.scraping_functions import get_last_search
from webapp.users import verifyCredentials
from webapp.users import storeUser

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
@app.route('/recipes')
def recipes():
    #since username is a dictionary entry, can't reference it if it doesn't exist yet
    if 'username' in session:
        user = {'username':session['username']}
    else:
        user = {'username':None}
        #user =  {'username':'Larry'}

    #temporary list to pass into render_template
    search = mongo.db.recipes.find()
    URL_list = []
    for x in search:
        URL_list.append(x['URL'])


    return render_template('recipes.html', title = 'Whats for Dinner-recipeList', user = user, recipes = URL_list)
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