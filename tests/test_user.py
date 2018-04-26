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


from user_class import User
import unittest


class MainTest(unittest.TestCase):
    """This class uses the Flask tests app to run an integration test against a
    local instance of the server."""

    def setUp(self):
        self.user = User("teresa", "teresa", "teresachoe@gmail.com",
                         "Teresa", "Choe", "1996-06-11", "None", True)

    def test_proper_date(self):
        self.assertEqual(User.proper_date(self.user, self.user.dob), "1996-06-11 00:00:00")

    def test_is_authenticated(self):
        self.assertEqual(User.is_authenticated(self.user), True)

    def test_is_active(self):
        self.assertEqual(User.is_active(self.user), True)

    def test_is_anonymous(self):
        self.assertEqual(User.is_anonymous(self.user), False)

    def test_get_id(self):
        self.assertEqual(User.get_id(self.user), "teresa")


if __name__ == '__main__':
    unittest.main()
