from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, FileField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed, FileRequired


ALLOWED_FILE_TYPES = {'jpg','jpeg','png','gif','bmp','tiff','webp'}

class AddItemForm(FlaskForm):

	name = StringField("Name:", validators=[DataRequired(), Length(max=50)])
	price = FloatField("Price:", validators=[DataRequired()])
	category = StringField("Category:", validators=[DataRequired(), Length(max=50)])
	image = FileField("Image:", validators=[FileRequired(),FileAllowed(ALLOWED_FILE_TYPES, 'Images only!')])
	details = StringField("Details:", validators=[DataRequired()])
	submit = SubmitField("Add")

class OrderEditForm(FlaskForm):

	status = StringField("Status:", validators=[DataRequired()])
	submit = SubmitField("Update")