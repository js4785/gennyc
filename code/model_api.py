import logging
from flask import Flask
app = Flask(__name__)
app.debug = True

from flask_restful import Resource, Api
import predictor
m = predictor.Model()

api = Api(app)

class PredictTag(Resource):
    def get(self, title):
        response = m.predict_bayes(title)
        return response
api.add_resource(PredictTag, '/api/model/predict_tag/<string:title>')

if __name__ == '__main__':
    app.run(debug=True)
