from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class RecipeForm(FlaskForm):
	base_recipe = StringField('Base Recipe', validators=[DataRequired()])
	additive1 = StringField('Additive 1', validators=[DataRequired()])
	additive2 = StringField('Additive 2', validators=[DataRequired()])
	submit = SubmitField('Generate recipe URL')

class SaveDataForm(FlaskForm):
	recipe = HiddenField()
	submit = SubmitField('Save Recipe')

class DiscardDataForm(FlaskForm):
	submit = SubmitField('Discard Recipe')
