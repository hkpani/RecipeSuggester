import os

class Config(object):
	#one variable assignment per line, here we are only configuring SECRET_KEY
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'