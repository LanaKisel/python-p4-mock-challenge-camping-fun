#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        campers =[camper.to_dict(only=('id','name','age')) for camper in Camper.query.all()]
        return make_response(jsonify(campers), 200)

    def post(self):
        data = request.get_json()
        try:
            new_camper = Camper(
                name = data['name'],
                age= data['age']
            )
            db.session.add(new_camper)
            db.session.commit()
            if new_camper:
                return make_response(new_camper.to_dict(only=('id', 'name', 'age')), 201)
        except:
            return {'errors':'validation errors'}, 400   
            
api.add_resource(Campers, '/campers')

class CampersById(Resource):
    def get(self, id):
        camper = db.session.query(Camper).filter(Camper.id == id).first()
        if camper:
            return make_response(camper.to_dict(), 200)
        return {'error': 'Camper not found'}, 404 

    def patch(self, id):
        data = request.get_json()
        camper = Camper.query.filter(Camper.id == id).first()
        if camper:
            for attr in data:
                try:
                    setattr(camper, attr, data[attr])
                except:
                    return {"errors": ["validation errors"]}, 400    
            db.session.add(camper)
            db.session.commit()
            return make_response(camper.to_dict(only=('id', 'name', 'age')), 202)
        return {'error':'Camper not found'}, 404    

api.add_resource(CampersById, '/campers/<int:id>')           

class Activities(Resource):
    def get(self):
        activity = [activity.to_dict(only=('id', 'name', 'difficulty')) for activity in Activity.query.all()]
        return make_response(jsonify(activity), 200)
api.add_resource(Activities, '/activities')       

class ActivityById(Resource):
    def delete(self, id):
        activity=Activity.query.filter_by(id=id).first()
        if activity:
            db.session.delete(activity)
            db.session.commit()
            return {}, 204
        return {'error':'Activity not found'}, 404    
api.add_resource(ActivityById, '/activities/<int:id>')

class Signups(Resource):
    def post(self):
        data=request.get_json()
        try:
            new_signup= Signup(
                camper_id=data['camper_id'],
                activity_id=data['activity_id'],
                time=data['time']
            )
            db.session.add(new_signup)
            db.session.commit()
            if new_signup:
                return make_response(new_signup.to_dict(), 201)
        except:
            return {'errors':['validation errors']}, 400    
        


api.add_resource(Signups, '/signups')        
if __name__ == '__main__':
    app.run(port=5555, debug=True)
