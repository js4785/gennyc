# -*- coding: utf-8 -*-
"""User class
"""

import datetime
from dateutil.parser import parse


class User:
    """User class."""
    def __init__(self,
                 username,
                 password,
                 email=None,
                 fname=None,
                 lname=None,
                 dob=None,
                 timezone=None,
                 email_verified=False,
                ):
        if username == '':
            raise ValueError('Username cannot be empty')
        if password == '':
            raise ValueError('Password cannot be empty')

        self.username = username
        self.password = password
        self.authenticated = True
        self.email = email
        self.fname = fname
        self.lname = lname
        self.dob = self.proper_date(str(dob))
        self.timezone = timezone
        self.join_date = datetime.date.today()
        self.email_verified = email_verified

        # print self.email, self.dob, self.timezone, self.join_date
        # print type(self.email), type(self.dob), type(self.timezone), type(self.join_date)

    def __eq__(self, other):
        if self.username == other.username and self.password \
            == other.password:
            return True
        return False

    def proper_date(self, date):
        """Parse to proper date."""
        d = datetime.date.today()
        try:
            d = parse(date)
        except ValueError:
            pass
        return str(d)

    def is_authenticated(self):
        """check if auth."""
        return self.authenticated

    def is_active(self):
        """check is active."""
        return True

    def is_anonymous(self):
        """check if anon."""
        return False

    def get_id(self):
        """get id."""
        return self.username
