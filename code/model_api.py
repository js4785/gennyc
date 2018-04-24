import logging
from flask import Flask, render_template, redirect, url_for, request, make_response
app = Flask(__name__)
app.debug = True

# === APP CONFIGURATIONS
app.config['SECRET_KEY'] = 'secretkey123984392032'
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
