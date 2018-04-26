"""Model Api
"""
# -*- coding: utf-8 -*-
from flask import Flask
from flask_restful import Resource, Api
import predictor
app = Flask(__name__)
app.debug = True

# === APP CONFIGURATIONS

app.config['SECRET_KEY'] = 'secretkey123984392032'
m = predictor.Model()

api = Api(app)


class PredictTag(Resource):
    """Predict tag."""
    def get(self, title):
        """Get prediction."""
        response = m.predict_bayes(title)
        return response


api.add_resource(PredictTag, '/api/model/predict_tag/<string:title>')

if __name__ == '__main__':
    app.run(debug=True)
