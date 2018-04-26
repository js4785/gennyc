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


from event import Event, EventForm
import unittest


class MainTest(unittest.TestCase):
    """This class uses the Flask tests app to run an integration test against a
    local instance of the server."""

    def setUp(self):
        self.event = Event(1, "PLUG AND PLAY : KEEP IT FRESH",
                           "Join us to explore innovation!",
                           "sports-fitness", "April 26 12:00 AM",
                           "April 26 02:00 AM", 10, 0, "My House", "440 North Wolfe Road",
                           "sports-fitness", 37, 122)
        self.event_form = EventForm()

    def test_to_json(self):
        self.assertEqual(Event.to_json(self.event),
                         {
                            "address_1": "440 North Wolfe Road",
                            "category": "sports-fitness",
                            "description": "Join us to explore innovation!",
                            "eid": 1,
                            "ename": "PLUG AND PLAY : KEEP IT FRESH",
                            "end_date": "April 26 02:00 AM",
                            "lat": 37,
                            "lname": "My House",
                            "lon": 122,
                            "num_attending": 0,
                            "num_cap": 10,
                            "start_date": "April 26 12:00 AM",
                            "tag": "sports-fitness"
                        })

    def test_get_eid(self):
        self.assertEqual(Event.get_eid(self.event), 1)


if __name__ == '__main__':
    unittest.main()
