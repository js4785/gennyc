# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'code')))


import main
import unittest
from user_class import User

VALID_UNAME = 'test1'
VALID_PSSWD = 'test1'
INVALID_UNAME = 'wrong_uname'
INVALID_PSSWD = 'wrong_psswd'
VALID_UNUSED_UNAME = 'my_test_unique_uname'
VALID_UNUSED_PSSWD = 'my_test_unique_psswd'
VALID_UNUSED_EMAIL = 'my_test_fake_email@gmail.com'
VALID_UNUSED_FNAME = 'my_fake_fname'
VALID_UNUSED_LNAME = 'my_fake_lname'
VALID_UNUSED_DOB   = '1970-01-01'
VALID_UNUZED_TIME  = '(GMT -8:00) Pacific Time (US & Canada)'

def teardown_new_user():
    database = main.connect_to_cloudsql()
    cursor = database.cursor()
    query = "DELETE FROM Users WHERE username = '" + VALID_UNUSED_UNAME + "'"

    cursor.execute(query)
    database.commit()
    database.close()

class MainTest(unittest.TestCase):
    """This class uses the Flask tests app to run an integration test against a
    local instance of the server."""

    def setUp(self):
        self.app = main.app.test_client()

    def test_front_page(self):
        rv = self.app.get('/')
        assert b'explore your city' in rv.data

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login(VALID_UNAME, VALID_PSSWD)
        assert b'Search' in rv.data
        rv = self.logout()
        assert b'Login' in rv.data
        rv = self.login(VALID_UNAME, INVALID_PSSWD)
        assert b'Login' in rv.data
        assert b'Error' in rv.data
        rv = self.login(INVALID_UNAME, VALID_PSSWD)
        assert b'Error' in rv.data

    def test_connect_to_cloudsql(self):
        db = main.connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute("SELECT DATABASE();")
        data = cursor.fetchone()
        db.close()
        assert data == ('Dev',)

    def test_query_for_user(self):
        my_user = User(VALID_UNAME, VALID_PSSWD)
        rv = main.query_for_user(my_user)
        assert rv is not None

        my_user = User(INVALID_UNAME, INVALID_PSSWD)
        rv = main.query_for_user(my_user)
        assert rv is None

    def test_authenticate_user(self):
        my_user = User(VALID_UNAME, VALID_PSSWD)
        rv = main.authenticate_user(my_user)
        assert rv == True

        my_user = User(INVALID_UNAME, INVALID_PSSWD)
        rv = main.authenticate_user(my_user)
        assert rv == False

    def test_get_user_from_username(self):
        rv = main.get_user_from_username(VALID_UNAME)

        assert rv[1] == VALID_PSSWD
        assert rv[0] == VALID_UNAME

    def test_insert_new_user(self):
        try:
            my_user = User( VALID_UNUSED_UNAME,
                            VALID_UNUSED_PSSWD )

            main.insert_new_user(my_user)

            database = main.connect_to_cloudsql()
            cursor = database.cursor()
            query = "SELECT username, password FROM Users WHERE username = '" + VALID_UNUSED_UNAME + "' AND password = '" + VALID_UNUSED_PSSWD + "'"

            cursor.execute(query)
            data = cursor.fetchone()

            assert data[0] == VALID_UNUSED_UNAME
            assert data[1] == VALID_UNUSED_PSSWD
            teardown_new_user()
        except:
            # safely assume connect_to_cloudsql works, since
            # otherwise the insert would have failed

            # teardown procedure
            teardown_new_user()

            raise

    def test_register_user_function(self):
        try:
            my_user = User( VALID_UNUSED_UNAME,
                            VALID_UNUSED_PSSWD )

            main.register_user(my_user)

            database = main.connect_to_cloudsql()
            cursor = database.cursor()
            query = "SELECT username, password FROM Users WHERE username = '" + VALID_UNUSED_UNAME + "' AND password = '" + VALID_UNUSED_PSSWD + "'"

            cursor.execute(query)
            data = cursor.fetchone()

            assert data[0] == VALID_UNUSED_UNAME
            assert data[1] == VALID_UNUSED_PSSWD
            teardown_new_user()

        except:
            # safely assume connect_to_cloudsql works, since
            # otherwise the insert would have failed
            teardown_new_user()

            raise

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def test_register_verify_endpoints(self):
        try:
            rv = self.app.get('/register')
            assert b'Register' in rv.data

            rv = self.app.post('/register', data=dict(
                username=VALID_UNUSED_UNAME,
                password=VALID_UNUSED_PSSWD,
                email=VALID_UNUSED_EMAIL,
                fname=VALID_UNUSED_FNAME,
                lname=VALID_UNUSED_LNAME,
                dob=VALID_UNUSED_DOB,
                timezone=VALID_UNUZED_TIME
            ), follow_redirects=True)

            assert b'Please verify your email by clicking the link we sent.' in rv.data

            rv = self.login(VALID_UNUSED_UNAME, VALID_UNUSED_PSSWD)

            assert b'Please verify your email by clicking the link we sent.' in rv.data

            rv = self.logout()
            assert b'Login' in rv.data

            teardown_new_user()

            rv = self.login(VALID_UNUSED_UNAME, VALID_UNUSED_PSSWD)
            assert b'Invalid Credentials' in rv.data

        except:
            teardown_new_user()
            raise

    def test_recommendations_page(self):
        self.login(VALID_UNAME, VALID_PSSWD)
        rv = self.app.get('/recommendations')
        assert b'Find your next experience' in rv.data
        self.logout()

    def test_groups(self):
        self.login(VALID_UNAME, VALID_PSSWD)
        rv = self.app.get('/groups')
        assert b'Your Groups' in rv.data
        assert b'test_group' in rv.data
        self.logout()

    def test_profile(self):
        self.login(VALID_UNAME, VALID_PSSWD)
        rv = self.app.get('/profile', follow_redirects=True)
        assert b'James Shin' in rv.data
        assert b'arts-culture' in rv.data
        self.logout()

    def test_interest_survey(self):
        self.login(VALID_UNAME, VALID_PSSWD)
        rv = self.app.get('/survey')
        assert b'Your Interests' in rv.data
        self.logout()

    def test_post_interests(self):
        self.login('kayvon', 'kayvon')
        rv = self.app.post('/survey', data=dict(
            hobbies='hobbies-crafts',
            causes='beliefs',
            fitness='sports-fitness',
            arts_and_culture='arts-culture'
        ), follow_redirects=True)
        assert b'Find your next' in rv.data
        rv = self.app.get('/profile', follow_redirects=True)
        assert b'arts-culture' in rv.data
        self.logout()

    def test_get_group_interests(self):
        rv = self.app.get('/api/get_group_interests/6')
        assert b'beliefs' in rv.data
        assert b'hobbies-crafts' in rv.data
        assert b'sports-fitness' in rv.data

    def test_get_group_recs(self):
        rv = self.app.get('/api/get_group_event_recs/6')
        assert b'beliefs' in rv.data
        assert b'hobbies-crafts' in rv.data
        assert b'sports-fitness' in rv.data

    def test_get_user_recs(self):
        self.login(VALID_UNAME, VALID_PSSWD)
        rv = self.app.get('/api/get_event_recs')
        assert b'beliefs' in rv.data
        assert b'hobbies-crafts' in rv.data
        assert b'sports-fitness' in rv.data
        self.logout()

    def test_group_functionality(self):
        self.login(VALID_UNAME, VALID_PSSWD)
        self.app.put('/api/new_group/test_group_test/true?users=kayvon')
        rv = self.app.get('/groups')
        assert b'test_group_test' in rv.data
        rv = self.app.get('/api/validate_groupname/test_group_test')
        assert rv.status_code == 201
        self.logout()
        self.login('kayvon', 'kayvon')
        rv = self.app.put('/api/respond_to_request/test_group_test/accept')
        assert rv.status_code == 200
        rv = self.app.get('/api/validate_username/existing/test_group_test/kayvon')
        assert rv.status_code == 201
        rv = self.app.get('/api/delete_group/test_group_test')
        assert rv.status_code == 200
        self.logout()

    def test_user_validate(self):
        self.login(VALID_UNAME, VALID_PSSWD)
        rv = self.app.get('/api/validate_username/test1')
        assert rv.status_code == 201
        rv = self.app.get('/api/validate_username/kayvon')
        assert rv.status_code == 200
        self.logout()




if __name__ == '__main__':
    unittest.main()
