from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp




class LoginForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	password = PasswordField("Password:", validators=[DataRequired(),Regexp("^[a-zA-Z0-9_\-&$@#!%^*+.]{8,30}$", message='Password must be 8 characters long and should contain letters, numbers and symbols.')])
	submit = SubmitField("Login")

class RegisterForm(FlaskForm):
	name = StringField("Name:", validators=[DataRequired(), Length(max=50)])
	password = PasswordField("Password:", validators=[DataRequired(),Regexp(r"\d+", message='Credit Card Number must contain numbers only')])
	confirm = PasswordField("Confirm Password:",validators=[EqualTo('password', message='Passwords must match')])
	credit_card =IntegerField("Credit Card Number:",validators=[DataRequired(),])
	submit = SubmitField("Register")