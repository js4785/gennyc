"""Event class and EventForm
"""
# -*- coding: utf-8 -*-
from datetime import date
import json
from wtforms import Form, fields, validators
from wtforms.ext.dateutil.fields import DateTimeField


class Event:
    """This class is a wrapper for Event objects."""

    def __init__(
            self,
            eid,
            ename,
            description,
            category,
            start_date,
            end_date,
            num_cap,
            num_attending,
            lname,
            address_1,
            tag,
            lat,
            lon,
        ):
        self.eid = eid
        self.ename = ename
        self.description = description
        self.category = category
        self.start_date = start_date
        self.end_date = end_date
        self.num_cap = num_cap
        self.num_attending = num_attending
        self.lname = lname
        self.address_1 = address_1
        self.tag = tag
        self.lat = lat
        self.lon = lon

    def to_json(self):
        """Jsonifies data."""
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


    def get_eid(self):
        """Return event id."""
        return self.eid


class EventForm(Form):
    """This class contains form fields for the Create Event form."""

    currentDate = date.today()
    today = currentDate.strftime('%m/%d/%Y')

    event_name = fields.StringField('Name your event:',
                                    validators=[validators.InputRequired()])
    description = fields.TextAreaField('Event description:',
                                       validators=[validators.InputRequired()])
    category = fields.SelectField('Event category:', choices=[
        ('hobbies-crafts', 'Arts & Crafts'),
        ('beliefs', 'Beliefs'),
        ('book-clubs', 'Book Clubs'),
        ('career-business', 'Career & Business'),
        ('education', 'Education'),
        ('fashion-beauty', 'Fashion & Beauty'),
        ('film', 'Film'),
        ('food', 'Food'),
        ('arts-culture', 'General Arts & Culture'),
        ('language', 'Language'),
        ('music', 'Music'),
        ('outdoors-adventure', 'Outoors Adventures'),
        ('parents-family', 'Parenting & Family'),
        ('social', 'Social'),
        ('sports-fitness', 'Sports & Fitness'),
        ('tech', 'Technology'),
        ], validators=[validators.InputRequired()])
    formatted_address = fields.StringField('Location Address:',
                                           validators=[validators.InputRequired()])
    start_date = DateTimeField('When will it start?',
                               display_format='%Y-%m-%d %H:%M',
                               validators=[validators.InputRequired()],
                               render_kw={'type': 'datetime-local'})
    end_date = DateTimeField('When will it end?',
                             display_format='%Y-%m-%d %H:%M',
                             validators=[validators.InputRequired()],
                             render_kw={'type': 'datetime-local'})
    cap = \
        fields.IntegerField('Maximum number of people able to participate:'
                            , validators=[])
    attending = \
        fields.IntegerField('How many people are attending already?',
                            validators=[])

    # location parsing fields (hidden)
    lat = fields.StringField('Latitude:')
    lng = fields.StringField('Longitude:')
    name = fields.StringField('Location Name:')
    address_2 = fields.StringField('Address Line 2:')
    postal_code = fields.StringField('Zip code:')
    sublocality = fields.StringField('City:')
    administrative_area_level_1_short = fields.StringField('State:')

    def __init__(self):
        self.initialized = True
