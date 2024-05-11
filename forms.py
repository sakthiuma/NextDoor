from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField, FloatField
from wtforms.fields.simple import TextAreaField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    firstname = StringField('First name', validators=[DataRequired(), Length(max=25)])
    lastname = StringField('Last name', validators=[DataRequired(), Length(max=25)])
    houseno = IntegerField('House no', validators=[DataRequired()])
    streetadd = StringField('Street address', validators=[DataRequired()])
    aptno = IntegerField('Apartment no', default=1)
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    zipcode = IntegerField('Zipcode', validators=[DataRequired()])
    description = TextAreaField('Description')
    password = PasswordField('Password', validators=[DataRequired()])
    confirmpassword = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PostThreadForm(FlaskForm):
    title = StringField('Title')
    content = StringField('Content')
    f_username = SelectField('Choose which friend should receive the message', choices=[])
    neigh_username = SelectField('Choose which neighbor should receive the message', choices=[])
    all_friend = BooleanField('Message to all friends')
    all_neigh = BooleanField('Message to all neighbors')
    to_block = BooleanField('Message to entire block')
    to_hood = BooleanField('Message to entire hood')
    submit = SubmitField('Post')


class ThreadReplyForm(FlaskForm):
    content = TextAreaField('Your reply')
    submit = SubmitField('Post')


class SearchForm(FlaskForm):
    text_search = StringField('Filter threads having the text -')
    loc_search = FloatField('Filter threads within this distance (in miles)', default=0)
    submit = SubmitField('Search')


class AddNeighborForm(FlaskForm):
    neigh_username = SelectField('Select a user to be added as neighbor ')
    submit = SubmitField('Add neighbor')


class AddFriendForm(FlaskForm):
    f_username = SelectField('Select a user to be added as friend')
    submit = SubmitField('Send friend request')

class AddBlockForm(FlaskForm):
    bname = SelectField('Select the block you want to join')
    submit = SubmitField('Submit join request')


class ForgotPasswordForm(FlaskForm):
    username = StringField(" Enter the username you registered with (Hint: its your first-name and last-name together with no space and caps)", validators=[DataRequired()])
    password = PasswordField('Enter the new password', validators=[DataRequired()])
    confirmpassword = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change password')


class AddressUpdateForm(FlaskForm):
    houseno = IntegerField('House no', validators=[DataRequired()])
    streetadd = StringField('Street address', validators=[DataRequired()])
    aptno = IntegerField('Apartment no', default=1)
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    zipcode = IntegerField('Zipcode', validators=[DataRequired()])
    submit = SubmitField('Update Address')


class DescriptionUpdateForm(FlaskForm):
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Update Description')