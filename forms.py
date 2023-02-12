from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError, Length, Regexp
import re

'''
Declare custom validator functions here
'''

# def phone_number_validator(form):
#     """ Validate phone numbers like:
#     1234567890 - no space
#     123.456.7890 - dot separator
#     123-456-7890 - dash separator
#     123 456 7890 - space separator
#     Patterns:
#     000 = [0-9]{3}
#     0000 = [0-9]{4}
#     -.  = ?[-. ]
#     """
#     number = form.phone.data

#     regex = re.compile('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
#     return regex.match(number)


'''
The lists containing state and genres choices are re-used across 
artist and venue form. We can extract them and re-use in class. 
'''

states_choices = [
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
genres_choices = [
            ('Alternative', 'Alternative'),
            ('Blues', 'Blues'),
            ('Classical', 'Classical'),
            ('Country', 'Country'),
            ('Electronic', 'Electronic'),
            ('Folk', 'Folk'),
            ('Funk', 'Funk'),
            ('Hip-Hop', 'Hip-Hop'),
            ('Heavy Metal', 'Heavy Metal'),
            ('Instrumental', 'Instrumental'),
            ('Jazz', 'Jazz'),
            ('Musical Theatre', 'Musical Theatre'),
            ('Pop', 'Pop'),
            ('Punk', 'Punk'),
            ('R&B', 'R&B'),
            ('Reggae', 'Reggae'),
            ('Rock n Roll', 'Rock n Roll'),
            ('Soul', 'Soul'),
            ('Other', 'Other'),
        ]

class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=states_choices
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    # add custom validation for phone numbers: digits only 
    phone = StringField(
        'phone', validators=[Regexp(regex=r'^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$', message="Invalid Phone Number")]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=genres_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    # added URL validator for website too
    website_link = StringField(
        'website_link', validators=[URL()]
    )
    
    seeking_talent = BooleanField(
    'seeking_talent')

    seeking_description = StringField(
        'seeking_description'
    )

    # def validate(self, field):
    #     if not phone_number_validator(self, field):
    #         raise ValidationError('Invalid phone number')

    # def validate(self, field):
    #     '''
    #     define a custom validate method
    #     '''
    #     rv = Form.validate(self)
    #     if not rv:
    #         return False
    #     if not phone_number_validator(self,self.phone.data):
    #         self.phone.errors.append('Invalid phone number.')
    #         return False
    #     if not set(self.genres.data).issubset(dict(genres_choices).keys()):
    #         self.genres.errors.append('Invalid genres')
    #         return False
    #     # if validation is passed 
    #     return True
  

class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=states_choices
    )
    phone = StringField(
        'phone', validators=[Regexp(regex=r'^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$', message="Invalid Phone Number")]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=genres_choices
     )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
     )

    website_link = StringField(
        'website_link', validators=[URL()]
     )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
     )
    # def validate(self, field):
    #     if not phone_number_validator(self.phone.data):
    #         raise ValidationError('Invalid phone number')
    # def validate(self):
    #     '''
    #     define a custom validate method
    #     '''
    #     rv = Form.validate(self)
    #     if not rv:
    #         return False
    #     if not phone_number_validator(self,self.phone.data):
    #         self.phone.errors.append('Invalid phone number.')
    #         return False
    #     if not set(self.genres.data).issubset(dict(genres_choices).keys()):
    #         self.genres.errors.append('Invalid genres')
    #         return False
    #     # if validation is passed 
    #     return True

