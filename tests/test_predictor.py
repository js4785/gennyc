import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'code')))

import model_api
from predictor import Model
import unittest
import json

TEST_INPUT_NAME = 'pick up game'
TEST_OUTPUT = 'sports-fitness'
TEST_RESPONSE = '"sports-fitness"\n'
NUM_TRAINING_EVENTS = 2513
NUM_ATTRIBUTES_TEST = 17264

MEETUP_TAGS = [
    'arts-culture',
    'beliefs',
    'book-clubs',
    'career-business',
    'dancing',
    'parents-family',
    'film',
    'food',
    'hobbies-crafts',
    'education',
    'music',
    'outdoors-adventure',
    'language',
    'sports-fitness',
    'social',
    'tech',
    ]

class MainTest(unittest.TestCase):

    def setUp(self):
        self.app = model_api.app.test_client()
        self.model = Model()

    def test_model_prep(self):
        for category in self.model.categories:
            self.assertEqual(category in MEETUP_TAGS, True)
        self.assertEqual(len(self.model.events), NUM_TRAINING_EVENTS)
        self.assertEqual(self.model.attr_totals[TEST_OUTPUT], NUM_ATTRIBUTES_TEST)

    def test_simple_prediction(self):
        self.assertEqual(self.model.predict_bayes(TEST_INPUT_NAME), TEST_OUTPUT)

    def test_model_api(self):
        response = self.app.get('/api/model/predict_tag/'+ TEST_INPUT_NAME)
        self.assertEqual(response.data, TEST_RESPONSE)

if __name__ == '__main__':
    unittest.main()
