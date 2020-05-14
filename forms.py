from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError
from enums import State, Genre

# ---------------------
# Custom validators
# ---------------------


def genre_validator(form, field):
    for item in field.data:
        if item not in [choice.value for choice in Genre]:
            raise ValidationError(
                f"Valid enums are {', '.join([choice.value for choice in Genre])}")


# ---------------------
# Form classes
# ---------------------

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
        default=datetime.today()
    )


class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state',
        validators=[
            DataRequired(),
            AnyOf([(choice.value) for choice in State])
        ],
        choices=State.choices()
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres',
        validators=[
            DataRequired(),
            genre_validator
        ],
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website = StringField(
        'website',
        validators=[URL()]
    )
    seeking_talent = BooleanField(
        'seeking_talent'
    )
    seeking_description = TextAreaField(
        'seeking_description'
    )


class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state',
        validators=[
            DataRequired(),
            AnyOf([(choice.value) for choice in State])
        ],
        choices=State.choices()
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres',
        validators=[
            DataRequired(),
            genre_validator
        ],
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )

    website = StringField(
        'website',
        validators=[URL()]
    )
    seeking_venue = BooleanField(
        'seeking_venue'
    )
    seeking_description = TextAreaField(
        'seeking_description'
    )
