from flask import redirect,session
from webapp import mongo
import bcrypt #for password hashing

#this file is for methods to store username and passwords entered by users to the database
#there are also methods to check if a username is already taken etc. 

def checkUserExists(username):
	
	user_coll = mongo.db.users
	#check if user is valid
	existing_user = user_coll.find_one({'username':username})

	#return True to the storeUser function if the existing user is not in the database
	if existing_user is None:
		return False
	else:
		return True


def storeUser(username,password):

	#check user before storing
	user_coll = mongo.db.users
	user_data_coll = mongo.db.userData
	existing_user = checkUserExists(username)

	if not existing_user: #checkUserExists returns false if user is not in DB already
		#hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
		hashpass = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
		user_coll.insert({'username' : username, 'password_hash' : hashpass})
		user_data_coll.insert({'user_id' : username, 'last_search' : None, 'saved_recipes' : []})
		return True	

	#if we got this far , means it was a taken username, ask to try again
	return False

def verifyCredentials(username,password):
	#function that verifies the username and password passed by the user
	user_coll = mongo.db.users
	existing_user = checkUserExists(username)

	if existing_user:
		#hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
		user_in_db = user_coll.find_one({'username':username})
		hashpass = bcrypt.hashpw(password.encode('utf-8'), user_in_db['password_hash'])
		if hashpass == user_in_db['password_hash']:
			session['username'] = username
			return True
		else:
			#password was not verified
			return False

	else:
		#user was not in the database
		return False
		
#maybe later do a password requirement check