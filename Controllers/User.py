import datetime

from flask_restful import Resource
from flask import request, jsonify, abort
from passlib.apps import custom_app_context 
from Other.SharedResources import db
#        Models        #
from Models.User import User as MUser

class User(Resource):
    def post(self):
        if self._retrieveUser(request.json["username"]) is None:
            userObj = MUser(username = request.json["username"],password = custom_app_context.hash(request.json["password"]),creation_time = datetime.datetime.now(), phoneNumber = request.json["phoneNumber"])
            db.session.add(userObj)
            db.session.commit()
            userJson = userObj.asJsonObj()
            del userJson["PASSWORD"]
            del userJson["ID"]
            return jsonify(userJson)
        else:
            abort(400,"User already exists.")

    def _retrieveUser(self,username):
        UserObj = MUser.query.filter(MUser.username == username).first()
        return UserObj
