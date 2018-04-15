from wtforms import Form, fields, validators
from datetime import datetime, date
from wtforms_components import TimeField
from wtforms.widgets.core import HTMLString, html_params, escape
from wtforms.ext.dateutil.fields import DateTimeField
import json

class Event():
    def __init__(self, eid, ename, description, start_date, end_date, num_cap, num_attending, lname, address_1, tag, lat, lon):
        self.eid = eid
        self.ename = ename
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.num_cap = num_cap
        self.num_attending = num_attending
        self.lname = lname
        self.address_1 = address_1
        self.tag = tag
        self.lat = lat
        self.lon = lon

    def toJSON(self):
        
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)


class EventForm(Form):
    currentDate = date.today()
    today = currentDate.strftime('%m/%d/%Y')

    event_name = fields.StringField("Name your event:", validators=[validators.InputRequired()])
    description = fields.TextAreaField("Event description:", validators=[validators.InputRequired()])
    formatted_address = fields.StringField("Location Address:", validators=[validators.InputRequired()])
    start_date = DateTimeField('When will it start?', display_format='%Y-%m-%d %H:%M', validators=[validators.InputRequired()],
        render_kw={"type": "datetime-local"})
    end_date = DateTimeField('When will it end?', display_format='%Y-%m-%d %H:%M', validators=[validators.InputRequired()],
        render_kw={"type": "datetime-local"})
    cap = fields.IntegerField("Maximum number of people able to participate:", validators=[])
    attending = fields.IntegerField("How many people are attending already?", validators=[])

    # location parsing fields (hidden)
    lat = fields.StringField("Latitude:")
    lng = fields.StringField("Longitude:")
    name = fields.StringField("Location Name:")
    address_2 = fields.StringField("Address Line 2:")
    postal_code = fields.StringField("Zip code:")
    sublocality = fields.StringField("City:")
    administrative_area_level_1_short = fields.StringField("State:")
